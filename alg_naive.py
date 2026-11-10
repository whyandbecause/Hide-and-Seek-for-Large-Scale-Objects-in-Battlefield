"""Myopic standalone-value greedy baseline under the paper's joint model.

Usage: python3 alg_naive.py <num_obj> <num_loc> <d_max>
The assignment is identical to the original global greedy baseline, but the
reported objective uses exactly the same graph builder and joint objective as
alg_our.py, including f(x,y)=(d_xy/d_max)^2.
"""
import sys
import numpy as np
import alg_our as AO


def alg_naive():
    n, m, d_max = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    val, coord, cand, candp, edges = AO.read_instance(n, m)
    ii, jj, probs = edges
    order = np.argsort(-(1 - probs) * val[ii])
    ass = np.full(n, -1, dtype=int)
    occupied = np.zeros(m, dtype=bool)
    for k in order:
        i, j = int(ii[k]), int(jj[k])
        if ass[i] < 0 and not occupied[j]:
            ass[i] = j
            occupied[j] = True

    def prob_of(i, j):
        k = int(np.searchsorted(cand[i], j))
        if k >= len(cand[i]) or cand[i][k] != j:
            raise KeyError((i, j))
        return float(candp[i][k])

    _A, F = AO.build_graph(coord, d_max)
    value = AO.total_value(ass, prob_of, val, F)
    print("naive protected value: %f" % value)
    return value


if __name__ == "__main__":
    alg_naive()
