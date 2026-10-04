/* Single-worker simulated annealing in the rational reference triangle.
 * Numerical generator only; exact checks are separate. Seed xorshift64.
 * Scores full triple enumeration after every point update. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
static uint64_t state;
static double urand(void){state^=state<<13;state^=state>>7;state^=state<<17;return (state>>11)*0x1.0p-53;}
static double score(double p[40][2],int n){
 double best=10;
 for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){
  double a=fabs((p[j][0]-p[i][0])*(p[k][1]-p[i][1])-(p[j][1]-p[i][1])*(p[k][0]-p[i][0]));
  if(a<best)best=a;
 }
 return best;
}
int main(int argc,char**argv){
 if(argc<3)return 2;state=strtoull(argv[1],0,10)+1;int steps=atoi(argv[2]),n;
 if(scanf("%d",&n)!=1||n>40||n<3)return 3;
 double p[40][2],bestp[40][2];for(int i=0;i<n;i++)if(scanf("%lf %lf",p[i],p[i]+1)!=2)return 4;
 /* Escape source basin before reheating; retain a genuinely distinct trial. */
 for(int i=0;i<n;i++){
  p[i][0]+= .08*(urand()-.5);p[i][1]+=.08*(urand()-.5);
  if(p[i][0]<0)p[i][0]=0;if(p[i][1]<0)p[i][1]=0;
  double s=p[i][0]+p[i][1];if(s>1){p[i][0]/=s;p[i][1]/=s;}
 }
 double current=score(p,n),best=current;
 for(int i=0;i<n;i++)for(int a=0;a<2;a++)bestp[i][a]=p[i][a];
 for(int it=0;it<steps;it++){
  double phase=(double)(it%(steps/4))/(steps/4);
  double temperature=.0015*pow(.001,phase),amplitude=.12*pow(.008,phase);
  int i=(int)(urand()*n);double x=p[i][0],y=p[i][1];
  if(urand()<.002){p[i][0]=urand();p[i][1]=urand();}
  else {p[i][0]+=amplitude*(urand()-.5);p[i][1]+=amplitude*(urand()-.5);}
  /* Boundary reflection/projection; all three boundary classes allowed. */
  if(p[i][0]<0)p[i][0]=0;if(p[i][1]<0)p[i][1]=0;
  double s=p[i][0]+p[i][1];if(s>1){p[i][0]/=s;p[i][1]/=s;}
  double next=score(p,n);
  if(next>=current||urand()<exp((next-current)/temperature))current=next;
  else {p[i][0]=x;p[i][1]=y;}
  if(current>best){best=current;for(int j=0;j<n;j++)for(int a=0;a<2;a++)bestp[j][a]=p[j][a];}
 }
 printf("%.17g\n",best);for(int i=0;i<n;i++)printf("%.17g %.17g\n",bestp[i][0],bestp[i][1]);
 return 0;
}
