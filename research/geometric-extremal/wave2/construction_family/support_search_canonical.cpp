#include <array>
#include <chrono>
#include <fstream>
#include <iostream>
#include <sstream>
#include <set>
#include <vector>
#include <string>
#include <cmath>
using namespace std;
const array<array<int,3>,10> BASE={{{-2,-1,9},{-1,-2,9},{1,-1,9},{1,0,5},{2,1,8},{1,1,5},{1,2,8},{0,1,5},{-1,1,8},{-1,0,5}}};
string TAG="support";
struct Result{int n=0,k=0;vector<array<int,2>> points;array<int,10> support;long code=0;};
int classes(const vector<array<int,2>>& p){
 unsigned long long bits[128]={};int k=0;
 for(size_t i=0;i<p.size();i++)for(size_t j=0;j<i;j++){
  int a=p[i][0]-p[j][0],b=p[i][1]-p[j][1],q=a*a+a*b+b*b;
  if(q>=8192)return 100000;
  auto mask=1ULL<<(q%64);auto& v=bits[q/64];if(!(v&mask)){v|=mask;k++;}
 }
 return k;
}
vector<array<int,2>> points(const array<int,10>& c){
 vector<array<int,2>> p;
 // a is explicitly bounded by x<=c3 and -x<=c9. b<=c7 and
 // -a-2b<=c1 imply b>=ceil((-a-c1)/2): no finite-grid truncation.
 for(int a=-c[9];a<=c[3];a++){
  int lo=(int)ceil(double(-a-c[1])/2.);
  for(int b=lo;b<=c[7];b++){
   bool yes=true;for(int j=0;j<10;j++)if(BASE[j][0]*a+BASE[j][1]*b>c[j]){yes=false;break;}
   if(yes)p.push_back({a,b});
  }
 }
 return p;
}
void save(const Result& r,const string& folder){
 ofstream f(folder+"/"+TAG+"_k"+to_string(r.k)+"_n"+to_string(r.n)+"_code"+to_string(r.code)+".json");
 f<<"{\"problem\":\"few_distance\",\"metric\":\"triangular\",\"max_distances\":"<<r.k<<",\"points\":[";
 for(size_t i=0;i<r.points.size();i++){if(i)f<<",";f<<"["<<r.points[i][0]<<","<<r.points[i][1]<<"]";}
 f<<"],\"provenance\":{\"method\":\"exhaustive integer support offsets of 10-gon\",\"code\":"<<r.code<<",\"halfplanes\":[";
 for(int i=0;i<10;i++){if(i)f<<",";f<<"["<<BASE[i][0]<<","<<BASE[i][1]<<","<<r.support[i]<<"]";}
 f<<"]}}\n";
}
int main(int argc,char**argv){
 int delta=argc>1?stoi(argv[1]):1;string folder=argv[2],log=argv[3];bool canonical=argc>4&&string(argv[4])=="canon";if(canonical)TAG="support_canonical";int radix=2*delta+1;long count=1;for(int j=0;j<(canonical?8:10);j++)count*=radix;
 array<Result,151> best;ofstream f(log);f<<"code,n,k\n";auto tick=chrono::steady_clock::now();long trials=0;
 for(long code=0;code<count;code++){
  long rem=code;array<int,10> c;for(int j=0;j<10;j++){if(canonical&&(j==3||j==7)){c[j]=6;continue;}c[j]=BASE[j][2]+int(rem%radix)-delta;rem/=radix;}
  auto p=points(c);if(p.size()<3)continue;int k=classes(p);f<<code<<","<<p.size()<<","<<k<<"\n";trials++;
  if(k<=150&&int(p.size())>best[k].n){best[k]={int(p.size()),k,p,c,code};save(best[k],folder);}
 }
 double runtime=chrono::duration<double>(chrono::steady_clock::now()-tick).count();
 cout<<"{\"delta\":"<<delta<<",\"completed\":"<<trials<<",\"elapsed_seconds\":"<<runtime<<",\"best_exact_class\":{";
 bool first=true;for(int k=1;k<=150;k++)if(best[k].n){if(!first)cout<<",";first=false;cout<<"\""<<k<<"\":"<<best[k].n;}
 cout<<"}}\n";
}
