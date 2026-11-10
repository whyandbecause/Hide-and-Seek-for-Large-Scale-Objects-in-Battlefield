r"""
Our algorithm for "Hide and Seek for Large Scale Objects in Battlefield"
(TMC-2026-01-0162, revised version).

Usage (unchanged):
    python3 alg_our.py <num_obj> <num_loc> <dis_max> <mcmf_result_file>

Input files (same conventions as before):
    <num_obj>_<num_loc>_val_loc.txt   target values, then location coordinates
    <num_obj>_<num_loc>_network.txt   candidate edges  "obj  loc+num_obj  1  p*100"
    <mcmf_result_file>                MCMF flow output "obj loc flow p*100 val x y"

Corrections with respect to the original version:
 1) The joint detection probability now multiplies the distance-dependent
    influence factor f(x,y)=(d_xy/d_max)^2 for every neighbor within d_max,
    exactly as defined in the paper (the original code omitted f, i.e. it
    effectively used f=1 for every in-range neighbor).
 2) Stage 3 is the strengthened unified local update of revised Algorithm 3:
    every target may be added, withdrawn, or relocated; the gain of moving
    target o_k to l_z is  gain(k->z) = Delta(k) + b(z) - l(z),  evaluated in
    closed form on I' = I \ {current location of o_k}, which equals the exact
    change of the objective.
 3) Dual warm start: the refinement is run from the Stage-2 filtered
    deployment and from a marginal-gain greedy (GMG) deployment; the better
    local optimum is returned.
 4) Stage 1 is maximum-weight bipartite matching with optional deployment,
    and Stage 2 maintains degrees in the current residual graph with a lazy
    priority queue, matching the revised proof and Algorithms 1--2.
"""
import sys
import heapq
import numpy as np
from scipy.sparse import csr_matrix

TOL = 1e-9
EPS = 1e-12  # guards division by a zero influence factor (f=0 happens only
             # when two locations coincide, i.e. mutual exposure is total)


# ---------------------------------------------------------------- instances
def read_instance(num_obj, num_loc):
    """values, coordinates, per-target candidate sets L_k, and edge arrays."""
    with open("%d_%d_val_loc.txt" % (num_obj, num_loc)) as f:
        tok = f.read().split()
    val = np.array([int(t) for t in tok[:num_obj]], dtype=float)
    xy = tok[num_obj:num_obj + 2 * num_loc]
    coord = np.array([int(t) for t in xy], dtype=float).reshape(num_loc, 2)
    cand = [[] for _ in range(num_obj)]
    candp = [[] for _ in range(num_obj)]
    with open("%d_%d_network.txt" % (num_obj, num_loc)) as f:
        f.readline()  # edge count
        for line in f:
            u, v, _cap, c = line.split()
            u, v = int(u), int(v)
            if u < num_obj <= v < num_obj + num_loc:  # obj -> location edge
                cand[u].append(v - num_obj)
                candp[u].append(int(c) / 100.0)
    ei, ej, ep = [], [], []
    for i in range(num_obj):
        order = np.argsort(cand[i])
        cand[i] = np.array(cand[i], dtype=int)[order]
        candp[i] = np.array(candp[i], dtype=float)[order]
        ei += [i] * len(cand[i])
        ej += cand[i].tolist()
        ep += candp[i].tolist()
    edges = (np.array(ei, dtype=int), np.array(ej, dtype=int),
             np.array(ep, dtype=float))
    return val, coord, cand, candp, edges


def read_flow(fname, num_obj):
    """Maximum-weight matching assignment: (target, location, p, value)."""
    res = []
    with open(fname) as f:
        for line in f:
            x = line.split()
            res.append((int(x[0]), int(x[1]) - num_obj,
                        int(x[3]) / 100.0, float(x[4])))
    return res


# ------------------------------------------------------- influence graph
def build_graph(coord, d_max):
    """Sparse influence graph over all m locations.
    A: 0/1 adjacency (d_xy <= d_max); F: same pattern with f=(d/d_max)^2."""
    m = len(coord)
    try:
        from scipy.spatial import cKDTree
        pairs = cKDTree(coord).query_pairs(d_max + 1e-9, output_type='ndarray')
    except ImportError:  # numpy fallback, O(m^2) in blocks
        rows, cols = [], []
        for s in range(0, m, 512):
            d2 = ((coord[s:s + 512, None, :] - coord[None, :, :]) ** 2).sum(-1)
            r, c = np.where(d2 <= (d_max + 1e-9) ** 2)
            keep = s + r < c
            rows.append(s + r[keep]); cols.append(c[keep])
        pairs = np.stack([np.concatenate(rows), np.concatenate(cols)], 1) \
            if rows else np.zeros((0, 2), dtype=int)
    if len(pairs):
        d = np.linalg.norm(coord[pairs[:, 0]] - coord[pairs[:, 1]], axis=1)
        fv = (d / d_max) ** 2
        r = np.concatenate([pairs[:, 0], pairs[:, 1]])
        c = np.concatenate([pairs[:, 1], pairs[:, 0]])
        f2 = np.concatenate([fv, fv])
    else:
        r = c = np.zeros(0, dtype=int); f2 = np.zeros(0)
    A = csr_matrix((np.ones(len(r)), (r, c)), shape=(m, m))
    F = csr_matrix((f2, (r, c)), shape=(m, m))
    return A, F


# ------------------------------------------------------------ stage 2
def stage2_greedy(res, A_pool, num_obj):
    """Greedy min d_G(x)/omega(x) filtering on the matching pool (Algorithm 2).
    Degrees always refer to the current induced residual graph. Returns the
    initial deployment ass[i] = location or -1."""
    N = len(res)
    w = np.array([(1 - r[2]) * r[3] for r in res])  # standalone omega(x)
    d = np.asarray(A_pool.sum(1)).ravel().astype(float)  # current induced degree
    active = np.ones(N, dtype=bool)
    label = np.full(N, -1)          # -1: undecided, 1: selected, 0: excluded
    ratio = np.divide(d, w, out=np.full(N, np.inf), where=w > 0)
    heap = [(float(ratio[x]), x) for x in range(N)]
    heapq.heapify(heap)
    indptr, indices = A_pool.indptr, A_pool.indices
    while heap:
        old_ratio, x = heapq.heappop(heap)
        if not active[x] or old_ratio != ratio[x]:
            continue  # lazy deletion of a stale degree-priority entry
        label[x] = 1
        # Delete the entire closed neighborhood from the residual graph and
        # update every current degree affected by any of those deletions.
        removed = np.concatenate(([x], indices[indptr[x]:indptr[x + 1]]))
        removed = removed[active[removed]]
        active[removed] = False
        label[removed[label[removed] == -1]] = 0
        for r in removed:
            nb = indices[indptr[r]:indptr[r + 1]]
            nb = nb[active[nb]]
            d[nb] -= 1
            ratio[nb] = np.divide(d[nb], w[nb], out=np.full(len(nb), np.inf),
                                  where=w[nb] > 0)
            for u in nb:
                heapq.heappush(heap, (float(ratio[u]), int(u)))
    ass = np.full(num_obj, -1, dtype=int)
    for k, r in enumerate(res):
        if label[k] == 1:
            ass[r[0]] = r[1]
    return ass


# -------------------------------------------- exact objective (with f)
def total_value(ass, prob_of, val, F):
    """Q = sum over deployed l_x of (1-p_ix)*prod_{y~x} f(x,y)(1-p_jy) * v_i."""
    m = F.shape[0]
    occ = np.zeros(m, bool); q = np.ones(m); base = np.zeros(m)
    for i in range(len(ass)):
        j = ass[i]
        if j >= 0:
            p = prob_of(i, j)
            occ[j] = True; q[j] = 1 - p; base[j] = (1 - p) * val[i]
    att = np.ones(m)
    indptr, indices, data = F.indptr, F.indices, F.data
    for j in np.where(occ)[0]:
        s, e = indptr[j], indptr[j + 1]
        att[indices[s:e]] *= np.maximum(data[s:e] * q[j], EPS)
    return float((base[occ] * att[occ]).sum())


# ------------------------------------------- stage 3: unified refinement
def refine(ass, prob_of, val, cand, candp, A, F, max_pass=60, seed=0):
    """Algorithm 3 repeat loop: each pass reconsiders every target o_k;
    o_k may stay, be withdrawn, or move to any free candidate l_z in L_k;
    an update is applied only when gain = Delta(k) + b(z) - l(z) > 0.
    Every existing contribution uses the current joint protection value
    A(x; J) = base[x] * att[x], not the standalone weight omega(x)."""
    n, m = len(ass), F.shape[0]
    indptr, indices, data = F.indptr, F.indices, F.data
    occ = np.zeros(m, bool); q = np.ones(m); base = np.zeros(m); att = np.ones(m)
    ass = ass.copy()
    for i in range(n):
        j = ass[i]
        if j >= 0:
            p = prob_of(i, j)
            occ[j] = True; q[j] = 1 - p; base[j] = (1 - p) * val[i]
    for j in np.where(occ)[0]:
        s, e = indptr[j], indptr[j + 1]
        att[indices[s:e]] *= np.maximum(data[s:e] * q[j], EPS)
    rng = np.random.default_rng(seed)
    for _ in range(max_pass):
        improved = False
        for i in rng.permutation(n):
            u = ass[i]
            delta_k = 0.0
            if u >= 0:  # withdraw o_k tentatively (all gains taken on I'=I\{u})
                s, e = indptr[u], indptr[u + 1]
                nb, fd = indices[s:e], data[s:e]
                sel = occ[nb]
                own_joint = base[u] * att[u]            # A(l_w; I), before withdrawal
                att[nb] /= np.maximum(fd * q[u], EPS)  # remove u's influence
                occ[u] = False
                joint_after = base[nb] * att[nb]        # A(x; I'), after withdrawal
                delta_k = float((joint_after[sel]
                                 * (1 - fd[sel] * q[u])).sum() - own_joint)
            keep = (~occ[cand[i]]) & (cand[i] != u)
            z, pz = cand[i][keep], candp[i][keep]
            best_gain, best_z, best_p = delta_k, -1, 0.0  # withdraw = baseline
            if len(z):
                joint_vec = np.where(occ, base * att, 0.0)  # A(x; I') at deployed x
                s1 = np.asarray(A[z, :] @ joint_vec).ravel()  # sum A(x; I') over neighbors
                s2 = np.asarray(F[z, :] @ joint_vec).ravel()  # sum f*A(x; I')
                b = (1 - pz) * val[i] * att[z]                # added benefit b(z)
                ell = s1 - (1 - pz) * s2                      # joint induced loss l(z)
                g = delta_k + b - ell
                k_best = int(np.argmax(g))
                if g[k_best] > best_gain:
                    best_gain = float(g[k_best])
                    best_z, best_p = int(z[k_best]), float(pz[k_best])
            if best_gain > TOL and best_z >= 0:   # relocate / add
                ass[i] = best_z
                occ[best_z] = True; q[best_z] = 1 - best_p
                base[best_z] = (1 - best_p) * val[i]
                s, e = indptr[best_z], indptr[best_z + 1]
                att[indices[s:e]] *= np.maximum(data[s:e] * q[best_z], EPS)
                improved = True
            elif best_gain > TOL:                 # pure withdrawal
                ass[i] = -1
                improved = True
            elif u >= 0:           # no improving update: restore o_k at l_w
                s, e = indptr[u], indptr[u + 1]
                att[indices[s:e]] *= np.maximum(data[s:e] * q[u], EPS)
                occ[u] = True
        if not improved:
            break
    return ass


# ---------------------------------- warm start 2: marginal-gain greedy
def gmg(val, edges, A, F, num_obj):
    """GMG: repeatedly add the (target, location) pair with the largest
    positive marginal gain under the joint detection objective (with f)."""
    m = F.shape[0]
    ei, ej, ep = edges
    occ = np.zeros(m, bool); att = np.ones(m)
    q = np.ones(m); base = np.zeros(m)
    used = np.zeros(num_obj, bool)
    ass = np.full(num_obj, -1, dtype=int)
    indptr, indices, data = F.indptr, F.indices, F.data
    for _ in range(num_obj):  # each iteration deploys one more target
        joint_vec = np.where(occ, base * att, 0.0)  # current A(x; I)
        s1 = np.asarray(A @ joint_vec).ravel()
        s2 = np.asarray(F @ joint_vec).ravel()
        g = (1 - ep) * val[ei] * att[ej] - (s1[ej] - (1 - ep) * s2[ej])
        g[used[ei] | occ[ej]] = -np.inf
        k = int(np.argmax(g))
        if g[k] <= TOL:
            break
        i, j, p = int(ei[k]), int(ej[k]), float(ep[k])
        ass[i] = j; used[i] = True
        occ[j] = True; q[j] = 1 - p; base[j] = (1 - p) * val[i]
        s, e = indptr[j], indptr[j + 1]
        att[indices[s:e]] *= np.maximum(data[s:e] * q[j], EPS)
    return ass


# ---------------------------------------------------------------- main
def alg_our():
    num_obj = int(sys.argv[1])
    num_loc = int(sys.argv[2])
    dis_max = float(sys.argv[3])
    flow_file = sys.argv[-1]

    val, coord, cand, candp, edges = read_instance(num_obj, num_loc)
    res = read_flow(flow_file, num_obj)

    def prob_of(i, j):
        k = np.searchsorted(cand[i], j)
        return float(candp[i][k])

    # influence graph over all locations (with f factors)
    A, F = build_graph(coord, dis_max)

    # stage 2: greedy filtering on the flow-pool subgraph
    pool = np.array([r[1] for r in res], dtype=int)
    A_pool = A[pool][:, pool]
    ass1 = stage2_greedy(res, A_pool, num_obj)

    # stage 3: unified refinement from both warm starts; keep the better one
    ass1 = refine(ass1, prob_of, val, cand, candp, A, F, seed=0)
    ass2 = refine(gmg(val, edges, A, F, num_obj), prob_of, val, cand, candp,
                  A, F, seed=1)
    t1 = total_value(ass1, prob_of, val, F)
    t2 = total_value(ass2, prob_of, val, F)
    ass, protect_value = (ass1, t1) if t1 >= t2 else (ass2, t2)

    cmd = "python3"
    for x in sys.argv:
        cmd = cmd + " " + x
    print(cmd)
    print("our protected value: %f" % protect_value)

    opt = 0.0  # omega(O): flow-based upper bound, unchanged
    for r in res:
        opt += (1 - r[2]) * r[3]
    print("max probability value: %f" % opt)
    return opt


if __name__ == "__main__":
    alg_our()
