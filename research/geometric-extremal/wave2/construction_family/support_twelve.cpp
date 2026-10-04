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
const array<array<int,3>,12> BASE={{{1,0,6},{0,1,6},{1,1,6},{-1,0,6},{0,-1,6},{-1,-1,6},{-2,-1,10},{-1,-2,10},{1,-1,10},{2,1,10},{1,2,10},{-1,1,10}}};
struct Result{int n=0,k=0;vector<array<int,2>> points;array<int,12> support;long code=0;};
int classes(const vector<array<int,2>>& p){
 unsigned long long bits[128]={};int k=0;
 for(size_t i=0;i<p.size();i++)for(size_t j=0;j<i;j++){
  int a=p[i][0]-p[j][0],b=p[i][1]-p[j][1],q=a*a+a*b+b*b;
  if(q>=8192)return 100000;
  auto mask=1ULL<<(q%64);auto& v=bits[q/64];if(!(v&mask)){v|=mask;k++;}
 }
 return k;
}
vector<array<int,2>> points(const array<int,12>& c){
 vector<array<int,2>> p;
 // Explicit unit facets give -c3<=a<=c0 and -c4<=b<=c1.
 // This is the full bounded intersection, with no finite-grid truncation.
 for(int a=-c[3];a<=c[0];a++){
  for(int b=-c[4];b<=c[1];b++){
   bool yes=true;for(int j=0;j<12;j++)if(BASE[j][0]*a+BASE[j][1]*b>c[j]){yes=false;break;}
   if(yes)p.push_back({a,b});
  }
 }
 return p;
}
void save(const Result& r,const string& folder){
 ofstream f(folder+"/support_twelve_k"+to_string(r.k)+"_n"+to_string(r.n)+"_code"+to_string(r.code)+".json");
 f<<"{\"problem\":\"few_distance\",\"metric\":\"triangular\",\"max_distances\":"<<r.k<<",\"points\":[";
 for(size_t i=0;i<r.points.size();i++){if(i)f<<",";f<<"["<<r.points[i][0]<<","<<r.points[i][1]<<"]";}
 f<<"],\"provenance\":{\"method\":\"exhaustive 12-normal integer support offsets, x/y maxima fixed6\",\"code\":"<<r.code<<",\"halfplanes\":[";
 for(int i=0;i<12;i++){if(i)f<<",";f<<"["<<BASE[i][0]<<","<<BASE[i][1]<<","<<r.support[i]<<"]";}
 f<<"]}}\n";
}
int main(int argc,char**argv){
 int delta=argc>1?stoi(argv[1]):1;string folder=argv[2],log=argv[3];int radix=2*delta+1;long count=1;for(int j=0;j<10;j++)count*=radix;
 array<Result,151> best;ofstream f(log);f<<"code,n,k\n";auto tick=chrono::steady_clock::now();long trials=0;
 for(long code=0;code<count;code++){
  long rem=code;array<int,12> c;for(int j=0;j<12;j++){if(j<2){c[j]=6;continue;}c[j]=BASE[j][2]+int(rem%radix)-delta;rem/=radix;}
  auto p=points(c);if(p.size()<3)continue;int k=classes(p);f<<code<<","<<p.size()<<","<<k<<"\n";trials++;
  if(k<=150&&int(p.size())>best[k].n){best[k]={int(p.size()),k,p,c,code};save(best[k],folder);}
 }
 double runtime=chrono::duration<double>(chrono::steady_clock::now()-tick).count();
 cout<<"{\"delta\":"<<delta<<",\"completed\":"<<trials<<",\"elapsed_seconds\":"<<runtime<<",\"best_exact_class\":{";
 bool first=true;for(int k=1;k<=150;k++)if(best[k].n){if(!first)cout<<",";first=false;cout<<"\""<<k<<"\":"<<best[k].n;}
 cout<<"}}\n";
}
