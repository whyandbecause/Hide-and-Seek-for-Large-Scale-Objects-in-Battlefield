/* Exact depth-first search for the small-instance joint-deployment problem.
 * Input: n m d_max initial_lower_bound, values, coordinates, candidate lists.
 * A target may be undeployed; each location holds at most one target.
 * The branch bound ignores future interference but accounts for attenuation
 * already induced by deployed targets, hence it is a valid upper bound.
 */
#include <bits/stdc++.h>
using namespace std;
struct Option {int loc; double p, stand;};
int n,m; double D,best,cur; long long nodes=0;
vector<double> val,att,stand,x,y;
vector<vector<Option>> opts;
vector<vector<pair<int,double>>> nbr;
vector<int> order,owner;
vector<char> occ;

void dfs(int depth){
    ++nodes;
    double ub=cur;
    for(int k=depth;k<n;k++){
        int i=order[k]; double b=0;
        for(auto &o:opts[i]) if(!occ[o.loc]) b=max(b,o.stand*att[o.loc]);
        ub+=b;
    }
    if(ub<=best+1e-10) return;
    if(depth==n){best=max(best,cur);return;}
    int i=order[depth];
    for(auto &o:opts[i]){
        int j=o.loc; if(occ[j]) continue;
        double q=1-o.p, gain=o.stand*att[j];
        // stand[k]*att[k] is the current joint protection A(k; I).
        for(auto [k,f]:nbr[j]) if(occ[k]) gain-=stand[k]*att[k]*(1-f*q);
        vector<pair<int,double>> saved;
        saved.reserve(nbr[j].size());
        for(auto [k,f]:nbr[j]){saved.push_back({k,att[k]});att[k]*=f*q;}
        occ[j]=1; stand[j]=o.stand; owner[j]=i; cur+=gain;
        dfs(depth+1);
        cur-=gain; owner[j]=-1; stand[j]=0; occ[j]=0;
        // Save/restore also handles f*q==0 without division by zero.
        for(auto [k,old_att]:saved) att[k]=old_att;
    }
    dfs(depth+1); // leave target i undeployed
}

int main(int argc,char**argv){
    if(argc!=2){cerr<<"usage: exact_search input.txt\n";return 2;}
    ifstream in(argv[1]); if(!in){cerr<<"cannot open input\n";return 2;}
    in>>n>>m>>D>>best; val.resize(n);x.resize(m);y.resize(m);
    for(double &v:val)in>>v;
    for(int j=0;j<m;j++)in>>x[j]>>y[j];
    opts.assign(n,{});nbr.assign(m,{});
    for(int i=0;i<n;i++){
        int c;in>>c;opts[i].resize(c);
        for(auto &o:opts[i]){in>>o.loc>>o.p;o.stand=(1-o.p)*val[i];}
        sort(opts[i].begin(),opts[i].end(),[](auto&a,auto&b){return a.stand>b.stand;});
    }
    for(int a=0;a<m;a++)for(int b=0;b<m;b++)if(a!=b){
        double dx=x[a]-x[b],dy=y[a]-y[b],d=sqrt(dx*dx+dy*dy);
        if(d<=D+1e-9)nbr[a].push_back({b,(d/D)*(d/D)});
    }
    order.resize(n);iota(order.begin(),order.end(),0);
    vector<double> mx(n);
    for(int i=0;i<n;i++)for(auto&o:opts[i])mx[i]=max(mx[i],o.stand);
    sort(order.begin(),order.end(),[&](int a,int b){return mx[a]>mx[b];});
    att.assign(m,1.0);stand.assign(m,0.0);owner.assign(m,-1);occ.assign(m,0);cur=0;
    dfs(0);
    cout<<setprecision(17)<<best<<" "<<nodes<<"\n";
    return 0;
}
