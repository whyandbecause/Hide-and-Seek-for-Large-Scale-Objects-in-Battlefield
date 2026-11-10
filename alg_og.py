r"""Online Greedy (OG) baseline for the maximum protection probability-value
problem ("Hide and Seek for Large Scale Objects in Battlefield").

OG models sequential field deployment without global re-planning: targets
arrive in a random order, and each target is irreversibly assigned to the
free candidate location with the maximum current marginal gain (its added
protection value minus the exposure loss inflicted on already deployed
targets), or left undeployed when no candidate location has a positive gain.
The reported value is averaged over several random arrival orders.

Usage:
    python3 alg_og.py num_obj num_loc dis_max [num_orders]

Input files (same format as alg_our.py, in the working directory):
    {num_obj}_{num_loc}_val_loc.txt   target values + location coordinates
    {num_obj}_{num_loc}_network.txt   candidate edges with detection probs

Output:
    prints "og protected value: %f"
"""
import sys
import numpy as np

from alg_our import read_instance, build_graph, total_value, TOL, EPS


def og(val, A, F, num_obj, cand, candp, rng):
    """One random arrival order of the online greedy algorithm."""
    m = F.shape[0]
    occ = np.zeros(m, bool)          # occupied locations
    att = np.ones(m)                 # attenuation factor of each location
    q = np.ones(m)                   # 1 - p of the target at each location
    base = np.zeros(m)               # (1 - p) * v of the deployed target
    ass = np.full(num_obj, -1, dtype=int)
    indptr, indices, data = F.indptr, F.indices, F.data
    for i in rng.permutation(num_obj):
        if len(cand[i]) == 0:
            continue
        joint_vec = np.where(occ, base * att, 0.0)  # current joint A(x; I)
        s1 = np.asarray(A @ joint_vec).ravel()
        s2 = np.asarray(F @ joint_vec).ravel()
        C = cand[i]
        cp = candp[i]
        # marginal welfare gain of placing target i at each candidate location
        g = (1 - cp) * val[i] * att[C] - (s1[C] - (1 - cp) * s2[C])
        g[occ[C]] = -np.inf
        k = int(np.argmax(g))
        if not np.isfinite(g[k]) or g[k] <= TOL:
            continue
        j, p = int(C[k]), float(cp[k])
        ass[i] = j
        occ[j] = True
        q[j] = 1 - p
        base[j] = (1 - p) * val[i]
        s, e = indptr[j], indptr[j + 1]
        att[indices[s:e]] *= np.maximum(data[s:e] * q[j], EPS)
    return ass


def alg_og():
    num_obj = int(sys.argv[1])
    num_loc = int(sys.argv[2])
    dis_max = float(sys.argv[3])
    num_orders = int(sys.argv[4]) if len(sys.argv) > 4 else 3

    val, coord, cand, candp, edges = read_instance(num_obj, num_loc)
    A, F = build_graph(coord, dis_max)

    def prob_of(i, j):
        k = np.searchsorted(cand[i], j)
        return float(candp[i][k])

    vals = []
    for r in range(num_orders):
        rng = np.random.RandomState(100 + r)
        ass = og(val, A, F, num_obj, cand, candp, rng)
        vals.append(total_value(ass, prob_of, val, F))
    print("og protected value: %f" % float(np.mean(vals)))
    return float(np.mean(vals))


if __name__ == "__main__":
    alg_og()
