#include <bits/stdc++.h>
using namespace std;
#define ll long long
#define pb push_back
#define ld long double

const int MAXN=6174;
int n, m;
int cnt;
vector <int> OG[MAXN], G[MAXN];
ld dlist[36]={1, 3, 4, 7, 9, 12, 13, 16, 19, 21, 25, 27, 28, 31, 36, 37, 39, 43, 48, 49, 52, 57, 61, 63, 64, 67, 73, 75, 76, 79, 81, 84, 91, 93, 97, 100}; //triangular lattice 距離(查 OEIS 的)
int sortedid[MAXN];
int n1, n2, nv, ne;

bool eq(ld a, ld b){//避免浮點數誤差
    if(abs(a-b)<1e-9) return true;
    return false;
}

struct node{//存節點
    vector <ld> co;
    int id, deg;
};

bool MySort(node nd1, node nd2){
    return nd1.deg<nd2.deg;
}

vector <node> nodes;
ld A, B;
ld v1, vi;
node temp;
int curid=0, cnts=0;

void findvec(ld a, ld b){//算出和(0,0),(1,0)距離是 triangular lattice 距離的點
    temp.co.clear();
    A=(a-b+1)/2;
    B=(a-A*A);
    //cout<<a<<" "<<b<<" "<<A<<" "<<sqrt(B)<<endl;
    if(B<0) return;
    temp.co.pb(sqrtl(B));
    temp.co.pb(A);
    curid++;
    temp.id=curid;
    nodes.pb(temp);
    if(B==0) return;
    temp.co.clear(); 
    temp.co.pb(-sqrtl(B));
    temp.co.pb(A);
    curid++;
    temp.id=curid;
    nodes.pb(temp);
}

void sortgraph(){//照 degree 排
    sort(nodes.begin(), nodes.end(), MySort);
    for(int i=0; i<curid; i++) sortedid[nodes[i].id]=i+1;
    int idn;
    for(int i=0; i<curid; i++){
        idn=nodes[i].id;
        for(int j: OG[idn]){
            G[i+1].pb(sortedid[j]);
        }
    }
    for(int i=0; i<curid; i++){
        nodes[i].id=i+1;
    }
}

ld res=0, tempdis;
ld dis(node nd1, node nd2){//算距離
    res=0;
    for(int i=0; i<2; i++){
        tempdis=(nd1.co[i]-nd2.co[i]);
        res+=(tempdis*tempdis);
    }
    return res;
}

vector <node> simplex;//加 simplex graph 的點
void addsimplex(int n){
    for(int i=1; i<=n; i++){
        temp.co.clear();
        for(int j=1; j<=n; j++){
            if(j==i) temp.co.pb(1);
            else temp.co.pb(0);
        }
        simplex.pb(temp);
    }
}

//找最大團
int ans=0;
set <int> vertices;
vector <int> construction;
void clique(set <int> s, vector <int> cons, int sz){
    if(s.size()==0){
        if(sz>ans){
            ans=sz;
            construction.clear();
            for(int i: cons){;
                construction.pb(i);
            }
        }
        return;
    }
    while(s.size()>0){
        if(sz+s.size()<=ans) return;
        int j=*s.begin();
        cons.pb(j);
        s.erase(j);
        set <int> s2;
        for(int nxt: G[j]){
            if(s.find(nxt)!=s.end()) s2.insert(nxt);
        }
        clique(s2, cons, sz+1);
        cons.pop_back();
    }
}


int main(){
    cin>>n;
    cin>>ans;
    ans-=2;
    nodes.pb(temp);
    for(int i=0; i<n; i++){
        for(int j=0; j<n; j++){
            findvec(dlist[i], dlist[j]);
        }
    }//窮盡所有與 (1, 0) 和 (0, 0) 距離都是前 n 小的三角格點整數距離的點

    cout<<curid<<endl;
    ld curdis;
    int edges=0;
    for(int i=1; i<=curid; i++){//建圖
        for(int j=i+1; j<=curid; j++){
            curdis=dis(nodes[i], nodes[j]);
            for(int k=0; k<n; k++){
                if(eq(curdis, dlist[k])){
                    OG[i].pb(j);
                    OG[j].pb(i);
                    nodes[i].deg++;
                    nodes[j].deg++;
                    edges++;
                    break;
                }
            }
        }
    }
    sortgraph();
    for(int i=1; i<=curid; i++){
        if(nodes[i-1].deg<ans) continue;
        vertices.insert(i);
    }
    cout<<vertices.size()<<endl;;
    cout<<'{';
    clique(vertices, construction, 0);
    for(int i: construction){
        cout<<'(';
        for(int j=0; j<2; j++){
            if(j!=1) cout<<nodes[i-1].co[j]<<", ";
            else cout<<nodes[i-1].co[j];
        }
        cout<<"),";
        cout<<'\n';
    }
    cout<<"(0, 0),\n";
    cout<<"(0, 1)\n";
    cout<<"}\n";//為了方便輸入 GGB，輸出格式加上大括號
    cout<<ans+2;
}