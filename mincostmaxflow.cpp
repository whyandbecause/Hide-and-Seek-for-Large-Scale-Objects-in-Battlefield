#include<cstdio>
#include<cstring>
#include<cmath>
#include<algorithm>
#include<queue>
#include<iostream>
using namespace std;

const int INF = 0x7fffffff;

void free_mem();

int num_vertice, num_edges; 
int num_obj, num_loc;

int *head, *value, cnt = -1; 
struct Edge {
    int to, next, f, c;
} *edges;
struct Location {
	int x, y;
}*loc;
inline void addedge(int from, int to, int f, int c) {
    edges[++cnt].to = to;
    edges[cnt].f = f;
    edges[cnt].c = c;
    edges[cnt].next = head[from];
    head[from] = cnt;
}
int s, t;
int *last, *inq;
int *flow, *dis;

queue<int> Q;
bool SPFA() {
    while (!Q.empty())
        Q.pop();
    memset(last, -1, num_vertice*sizeof(int));
    memset(inq, 0, num_vertice*sizeof(int));
    for(int i=0; i<num_vertice; i++) {
    	dis[i] = INF;
    	flow[s] = INF;
    }
    flow[s] = INF;
    dis[s] = 0;
    inq[s] = 1;
    Q.push(s);
    while (!Q.empty()) {
        int u = Q.front();
        Q.pop();
        inq[u] = 0;
        for (int eg = head[u]; eg != -1; eg = edges[eg].next) {
            int to = edges[eg].to; int vol = edges[eg].f;
            if (vol > 0 && dis[to] > dis[u]+edges[eg].c) {// capacity must > 0     
                last[to] = eg; // last edge for to
                flow[to] = min(flow[u], vol); // update flow
                dis[to] = dis[u] + edges[eg].c; // note it is c, not f
                if (!inq[to])
                {
                    Q.push(to);
                    inq[to] = 1;
                }
            }
        }
    }
    return last[t] != -1;
}

double max_flow=0, min_cost=0;
inline void MCMF() {
	max_flow = 0;
	min_cost = 0;
	s = num_obj + num_loc;
	t = num_obj + num_loc + 1;
	
    while (SPFA()) {
        max_flow += flow[t];
        min_cost += dis[t] * flow[t];
        for (int i = t; i != s; i = edges[last[i] ^ 1].to) {
            edges[last[i]].f -= flow[t];
            edges[last[i] ^ 1].f += flow[t];
        }
    }
}

void read_value_loc(char fname[]) {
	freopen(fname, "r", stdin);
	
	value = (int *)malloc((num_obj+10)*sizeof(int));	
	loc = (Location *)malloc((num_loc+10)*sizeof(Location));
	memset(value, 0, (num_obj+10)*sizeof(int));
	for(int i=0; i<num_obj; i++) {
		scanf("%d", &value[i]);
	}
	for(int i=0; i<num_loc; i++) {
		scanf("%d%d", &loc[i].x, &loc[i].y);
	}
}

void read_network(char fname[]) {
	freopen(fname, "r", stdin);
	
	int d;
	scanf("%d", &d);	
	num_vertice = num_obj + num_loc + 2;
	num_edges = 2 * d;
		
	
	head = (int *)malloc((num_vertice+10)*sizeof(int));			
	memset(head, -1, (num_vertice+10)*sizeof(int)); 
	
	edges = (Edge *)malloc((num_edges+10)*sizeof(Edge));
	memset(edges, -1, (num_edges+10)*sizeof(Edge)); 
	
	
	dis = (int *)malloc((num_vertice+10)*sizeof(int));
	flow = (int *)malloc((num_vertice+10)*sizeof(int));
	last = (int *)malloc((num_vertice+10)*sizeof(int));	
	inq = (int *)malloc((num_vertice+10)*sizeof(int));
	
	cnt = -1;
	int u, v, f, c;
	while (d--) {
		scanf("%d%d%d%d", &u, &v, &f, &c); 
		if(u < num_obj) {
			c = -(100-c)*value[u];			
		}
		else c = -c*100;
		
		addedge(u, v, f, c);
		addedge(v, u, 0, -c);
	}
	/*
	for(int i=0; i<num_edges; i++) {
		//printf("%d %d %lf %lf\n", edge[i].from, edge[i].to, edge[i].flow, edge[i].cost);
	}*/
	freopen("/dev/tty", "r", stdin);
}

void output_obj2loc(char fname[]) {
	freopen(fname, "w", stdout);
	int *obj2loc = (int *)malloc((num_obj+10)*sizeof(int));
	memset(obj2loc, -1, (num_obj+10)*sizeof(int));
	int res = 0; int from, flow;
	for(int i=0; i<num_edges; i+=2) {
		from = edges[i^1].to; flow = edges[i^1].f;
		if(from<num_obj && flow>0) {
			obj2loc[from] = edges[i].to-num_obj;
			res += edges[i].c * flow;
			printf("%d %d %d %d %d %d %d\n", from,  
				                               edges[i].to, 
			                                   flow, 
			                                   100 + edges[i].c/value[from],
			                                   value[from], 
			                                   loc[obj2loc[from]].x, 
			                                   loc[obj2loc[from]].y);
		}
	}
	freopen("/dev/tty", "w", stdout);
	printf("min_cost: %d\n", res);
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
	
	MCMF();			
	printf("max min: %lf %lf\n", max_flow, min_cost);
	
	fname[0] = '\0';
	strcat(fname, argv[1]);
	strcat(fname, "_");
	strcat(fname, argv[2]);
	strcat(fname, "_result.txt");
	output_obj2loc(fname);	
		
	free_mem();	
	return 0;
}

void free_mem() {
	free(value);
	free(loc);
	free(flow);
	free(last);
	free(inq);
	free(head);
	free(edges);
}

