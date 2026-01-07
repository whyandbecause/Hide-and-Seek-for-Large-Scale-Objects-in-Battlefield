#include <iostream>
#include <fstream>
#include <cstring>
#include <queue>
using namespace std;

const double inf = 1000000000.0;

int *Head;
int *Depth;
int *cur;
int *Next;	
int *V;
double *W;

class Graph {
private:
    int edge_cnt=0, node_cnt=0, cnt=-1;
    int s, t;
public:	
	Graph(int ss, int tt, char fname[]) {
		s = ss;
		t = tt;
		node_cnt = tt+1;
		input(fname);
		cout << "source_node s=" << s << endl;
		cout << "target_node t=" << t << endl;
		cout << "node_count=" << node_cnt << endl;
		cout << "edge_count=" << edge_cnt << endl;
		
	}
	~Graph() {
		free(Head);
		free(Depth);
		free(cur);
		free(Next);
		free(V);
		free(W);
	}    
	void input(char fname[]) {
		freopen(fname, "r", stdin);
		int u, v;
		double w;
		int num;
		scanf("%d", &num);
		edge_cnt = 2*num;
		init();
		for(int i=0; i<num; i++) {
			scanf("%d%d%lf", &u, &v, &w);
			Add_Edge(u,v,w);
		}
	}
    void init() {
    	Head = (int *)malloc(node_cnt*sizeof(int));
    	Depth = (int *)malloc(node_cnt*sizeof(int));
    	cur = (int *)malloc(node_cnt*sizeof(int));
    	Next = (int *)malloc(edge_cnt*sizeof(int));
    	V = (int *)malloc(edge_cnt*sizeof(int));
    	W = (double *)malloc(edge_cnt*sizeof(double));
    	
        cnt=-1;
        memset(Head,-1,sizeof(node_cnt*sizeof(int)));
        memset(Next,-1,sizeof(edge_cnt*sizeof(int)));     
    }
    void _Add(int u, int v, double w) {
        cnt++;
        Next[cnt]=Head[u];
        Head[u]=cnt;
        V[cnt]=v;
        W[cnt]=w;
    }
    void Add_Edge(int u, int v, double w) {
        _Add(u,v,w);
        _Add(v,u,0);
    }
    double dfs(int u, double flow) {
        if (u==t)
            return flow;
        for (int& i=cur[u]; i!=-1; i=Next[i]) {//注意这里的&符号，这样i增加的同时也能改变cur[u]的值，达到记录当前弧的目的
            if ((Depth[V[i]]==Depth[u]+1) && (W[i]>0)) {
                double di=dfs(V[i], min(flow,W[i]));
                if (di>0) {
                    W[i] -= di;
                    W[i^1] += di;//最低位异或操作，cnt应从0开始，相当于连接的两个_Add操作（正反边操作）
                    return di;
                }
            }
        }
        return 0;
    }
    int bfs() {
        queue<int> Q;
        while (!Q.empty())
            Q.pop();
          
        memset(Depth, 0, node_cnt*sizeof(int)); // important
        
        Depth[s]=1;
        Q.push(s);
        while (!Q.empty()) {
            int u = Q.front();
            Q.pop();
            for (int i=Head[u]; i!=-1; i=Next[i]) {
                if ((Depth[V[i]]==0) && (W[i]>0)) {
                    Depth[V[i]] = Depth[u]+1;
                    Q.push(V[i]);
                }
            }
        }
        if (Depth[t]>0)
            return 1;
        return 0;
    }
    double Dinic() {
        double Ans=0;
        int x = 0;
        while (bfs()) {
            for (int i=0; i<node_cnt; i++)//每一次建立完分层图后都要把cur置为每一个点的第一条边 
                cur[i] = Head[i];
            while (double d = dfs(s,inf))
            {
                Ans+=d;
            }
        }
        return Ans;
    }
};

int main(int argc, char *argv[]) {
	int m = stoi(argv[1]);
	int n = stoi(argv[2]);
	Graph g(m+n,m+n+1,argv[3]);
	printf("Maxflow: %lf\n", g.Dinic());
	return 0;
}
