# Hide and Seek for Large Scale Objects in Battlefield — Code

This repository contains the scheduling code for the paper
"Hide and Seek for Large Scale Objects in Battlefield" (TMC-2026-01-0162).

Given `n` targets with values and `m` candidate hiding locations on a
two-dimensional map, the goal is to deploy the targets so that the total
protection probability-value `sum_i (1 - p_i) * v_i` is maximized, where the
joint detection probability of target `o_i` hidden at location `l_x` is

    p_i = 1 - (1 - p_ix) * prod_{d_xy <= d_max} f(x, y) * (1 - p_jy),

with the distance-dependent influence factor `f(x, y) = (d_xy / d_max)^2`.

Implementation note: `base[x] = (1 - p_ix) * v_i` is the standalone weight,
while `base[x] * att[x]` is the current joint protection value `A(x; I)`.
All induced-loss calculations use the latter. The withdrawal term `Delta(k)`
is evaluated directly from `A(x; I')` after the tentative withdrawal, matching
the revised Algorithm 3 in the paper.

## Files

| File | Description |
|---|---|
| `mincostmaxflow.cpp` | SPFA negative-cost-augmentation solver for maximum-weight bipartite matching with optional deployment (Stage 1); an alternative to the auction implementation. |
| `mincostmaxflow_auction.cpp` | Exact auction solver for the same optional-deployment maximum-weight matching problem; recommended for large instances. It has no cardinality bonus. |
| `alg_our.py` | The proposed three-stage algorithm: maximum-weight matching, current-degree lazy-heap independent-set filtering, and unified joint-gain refinement (add / withdraw / relocate) with dual warm start and at most 60 passes. |
| `alg_naive.py` | Naive baseline: myopic greedy by standalone protection value. |
| `alg_og.py` | Online greedy (OG) baseline: targets arrive in a random order and each is irreversibly assigned to the free candidate location with the maximum current marginal gain. |
| `run_fig7_12.py` | Reproduces the data of Figs. 7-12 (sizes 200-2000, seeds 0-2, fix/dec distance settings). |
| `plot_fig7_12.py` | Reproduces the six figures (PDF + PNG) from `exp_results.json`. |
| `run_fig13_16.py` | Recomputes the runtime/ablation, density-sensitivity, and exact-optimality experiments of Figs. 13-16 under the same distance-dependent model. |
| `exact_search.cpp` | Branch-and-bound exhaustive solver used to obtain the exact OPT for the 50 small instances in Fig. 16; targets may remain undeployed. |
| `verify_joint_gains.py` | Checks addition, withdrawal, and relocation gains against direct objective recomputation on random small instances. |
| `verify_matching_and_filtering.py` | Checks optional-deployment matching against brute force, including the maximum-cardinality counterexample, and checks filtering, independence, and the maximum-degree bound. |
| `verify_exact_search.py` | Cross-checks branch-and-bound OPT against plain exhaustive enumeration on 12 random small instances. |
| `plot_fig13_16.py` | Reproduces Figs. 13-16 (PDF + PNG), with OG as the common comparison baseline. |
| `run_real_experiment.py` | Reproduces the second real-image experiment (Figs. 20-21): 10 targets, 20 floating-point detection-box centers, exact OPT, OG, naive, and the proposed algorithm. |
| `real_image.png` | Supplied 1254 x 1210 battlefield map used by the real-image experiment. |
| `experiment_data/realmap.json` | Preserved real-image results, including all distance-grid values, exact-search node counts, and the deployment at `d_max = 150`. |


## Requirements

- Python 3.10+ with NumPy and SciPy (matplotlib and Pillow only for figures)
- A C++ compiler (`g++ -O2`)

## Verify the joint-gain formulas

    python3 verify_joint_gains.py

The test compares every sampled addition, withdrawal, and relocation gain with
a direct recomputation of the complete joint objective. To cross-check the two
matching solvers and the current-degree filtering implementation, compile and
run:

    g++ -O2 -o mincostmaxflow_spfa mincostmaxflow.cpp
    g++ -O2 -o mincostmaxflow_auction mincostmaxflow_auction.cpp
    SPFA_BIN=./mincostmaxflow_spfa AUCTION_BIN=./mincostmaxflow_auction \
        python3 verify_matching_and_filtering.py
    g++ -O2 -o exact_search exact_search.cpp
    EXACT_BIN=./exact_search python3 verify_exact_search.py

## Quick start

Compile the maximum-weight matching solver:

    g++ -O2 -o mincostmaxflow mincostmaxflow_auction.cpp

Prepare an instance in the working directory (two files, generated e.g. by
`run_fig7_12.py`):

- `{n}_{m}_network.txt` — first line: number of edges; then one edge per line
  `from to capacity cost`, where target vertices are `0..n-1`, location
  vertices are `n..n+m-1`, source is `n+m`, sink is `n+m+1`, and the cost on a
  target-location edge is the integer detection probability `p_ix * 100`.
- `{n}_{m}_val_loc.txt` — first `n` lines: target values; next `m` lines:
  location coordinates `x y`.

All methods, including the standalone `alg_naive.py`, are evaluated under the
same joint detection model with the distance-dependent factor f(x, y) (Eq. (2)).
The naive assignment remains myopic; only its objective evaluation is shared
with `alg_our.py` to prevent model mismatches.

Run the algorithms (values are printed to stdout):

    ./mincostmaxflow n m {n}_{m}_network.txt          # writes {n}_{m}_result.txt
    python3 alg_our.py   n m d_max {n}_{m}_result.txt  # our protected value
    python3 alg_naive.py n m d_max                     # naive protected value
    python3 alg_og.py    n m d_max [num_orders]        # OG protected value


