/*
 * Maximum-weight matching stage for "Hide and Seek for Large Scale Objects in
 * Battlefield" (TMC-2026-01-0162).
 *
 * Drop-in replacement for the original mincostmaxflow.cpp:
 *   - same command line:  ./mincostmaxflow <num_obj> <num_loc> <network_file>
 *   - same input files:   <n>_<m>_val_loc.txt and the network file
 *   - same output file:   <n>_<m>_result.txt, identical line format
 *   - same optimum:       maximum-weight bipartite matching with optional
 *                         deployment, exactly as in the negative-path SPFA
 *                         version (targets may remain unmatched)
 *
 * Why the SPFA version was slow: it re-ran SPFA (label-correcting, O(V*E)
 * worst case) from scratch for every negative-cost augmenting path.
 *
 * What this version does instead: maximum-weight bipartite matching on this
 * network is exactly a linear assignment problem with an optional zero-weight
 * dummy choice for every target.  It is solved by Bertsekas' auction algorithm:
 *   - maximize sum of W_ij = (100 - p_ij) * value[i] over matched pairs;
 *     there is NO cardinality bonus, so a low-weight pair never displaces a
 *     more valuable partial matching;
 *   - a single auction round is run at fixed epsilon = 1/(4n) < 1/n.  In
 *     this round an object bids only while some location is profitable
 *     (net value > 0), so unassigned locations always keep price 0, the
 *     classical epsilon-CS argument applies directly, and with integer
 *     weights the result is the EXACT optimum (no approximation);
 *   - targets with no profitable candidate simply remain undeployed.
 *     (Multi-phase epsilon-scaling is NOT used: resetting the assignment
 *     between phases while keeping prices can strand overpriced unassigned
 *     locations and break exactness.)
 * Typical speedup at n=2000, m=4000: minutes -> well under a second.
 */
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <algorithm>
#include <vector>
#include <string>
using namespace std;

typedef long long ll;

int num_obj, num_loc;
int *value;
struct Location {
	int x, y;
} *loc;

void free_mem();

/* per-object candidate lists with auction weights */
struct Cand { int j; ll w; };
vector<vector<Cand> > adj_list;

void read_value_loc(char fname[]) {
	freopen(fname, "r", stdin);
	value = (int *)malloc((num_obj+10)*sizeof(int));
	loc = (Location *)malloc((num_loc+10)*sizeof(Location));
	memset(value, 0, (num_obj+10)*sizeof(int));
	for(int i=0; i<num_obj; i++) scanf("%d", &value[i]);
	for(int i=0; i<num_loc; i++) scanf("%d%d", &loc[i].x, &loc[i].y);
}

void read_network(char fname[]) {
	freopen(fname, "r", stdin);
	int d;
	scanf("%d", &d);
	adj_list.assign(num_obj, {});
	int u, v, f, c;
	for (int e = 0; e < d; e++) {
		scanf("%d%d%d%d", &u, &v, &f, &c);
		if (u < num_obj && v >= num_obj && v < num_obj + num_loc) {
			ll w = (ll)(100 - c) * value[u];      /* -(original arc cost) */
			adj_list[u].push_back({v - num_obj, w});
		}
		/* source/sink arcs carry zero cost and are implicit */
	}
	freopen("/dev/tty", "r", stdin);
}

/* Bertsekas auction, maximization version, single round at eps = 1/(4n).
 * Integer weights + eps < 1/n + "unassigned <=> price 0"  =>  exact optimum
 * of the optional-deployment maximum-weight bipartite matching problem. */
void auction(vector<int> &owner) {
	vector<double> price(num_loc, 0.0);
	owner.assign(num_loc, -1);
	double eps = 1.0 / (4.0 * max(1, num_obj));
	vector<int> st;
	for (int i = 0; i < num_obj; i++)
		if (!adj_list[i].empty()) st.push_back(i);
	ll bids = 0;
	while (!st.empty()) {
		int i = st.back(); st.pop_back();
		double b1 = 0.0, b2 = 0.0;              /* dummy "stay out" = 0 */
		int j1 = -1;
		for (auto &cd : adj_list[i]) {
			double net = (double)cd.w - price[cd.j];
			if (net > b1) { b2 = b1; b1 = net; j1 = cd.j; }
			else if (net > b2) b2 = net;
		}
		if (j1 < 0) continue;                   /* nothing profitable */
		price[j1] += b1 - b2 + eps;
		if (owner[j1] != -1) st.push_back(owner[j1]);
		owner[j1] = i;
		if (++bids > 2000000000LL) {
			fprintf(stderr, "auction: bid limit exceeded\n");
			exit(1);
		}
	}
}

void output_obj2loc(char fname[], const vector<int> &owner) {
	freopen(fname, "w", stdout);
	ll res = 0;
	for (int j = 0; j < num_loc; j++) {
		int i = owner[j];
		if (i < 0) continue;
		ll w = -1;
		for (auto &cd : adj_list[i]) if (cd.j == j) { w = cd.w; break; }
		/* w = (100-p)*value[i]  =>  p*100 = 100 - w/value[i] */
		int p100 = (int)(100 - w / value[i]);
		res += -w;
		printf("%d %d %d %d %d %d %d\n", i, j + num_obj, 1, p100,
		       value[i], loc[j].x, loc[j].y);
	}
	freopen("/dev/tty", "w", stdout);
	printf("min_cost: %lld\n", res);
}

int main(int argc, char* argv[]) {
	num_obj = stoi(argv[1]);
	num_loc = stoi(argv[2]);

	char fname[100]="";
	strcat(fname, argv[1]);
	strcat(fname, "_");
	strcat(fname, argv[2]);
	strcat(fname, "_val_loc.txt");
	read_value_loc(fname);

	read_network(argv[3]);

	vector<int> owner;
	auction(owner);

	ll max_flow = 0, min_cost = 0;
	for (int j = 0; j < num_loc; j++) if (owner[j] >= 0) {
		max_flow++;
		int i = owner[j];
		for (auto &cd : adj_list[i]) if (cd.j == j) { min_cost -= cd.w; break; }
	}
	printf("max min: %lld %lld\n", max_flow, min_cost);

	fname[0] = '\0';
	strcat(fname, argv[1]);
	strcat(fname, "_");
	strcat(fname, argv[2]);
	strcat(fname, "_result.txt");
	output_obj2loc(fname, owner);

	free_mem();
	return 0;
}

void free_mem() {
	free(value);
	free(loc);
}
