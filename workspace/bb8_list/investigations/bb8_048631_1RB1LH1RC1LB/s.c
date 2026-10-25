#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char**argv){
  const char*M="1RB1LH_1RC1LB_0RD1RE_1LB0LB_1RF0LA_1LG1LF_1RH0LD_---0LE";
  int w[8][2],d[8][2],n[8][2];
  for(int i=0;i<8;i++)for(int s=0;s<2;s++){const char*c=M+i*7+3*s;
    if(c[0]=='-'){w[i][s]=-1;continue;}w[i][s]=c[0]-'0';d[i][s]=c[1]=='R'?1:-1;n[i][s]=c[2]-'A';}
  long long N=atoll(argv[1]);long L=1<<28;unsigned char*t=calloc(L,1);
  long p=L/2,lo=p,hi=p;int s=0;
  for(long long i=0;i<N;i++){
    int r=t[p];if(w[s][r]<0){printf("HALT step %lld\n",i);return 0;}
    t[p]=w[s][r];p+=d[s][r];s=n[s][r];
    if(p<lo){lo=p; if(s==1){ // print RLE
      printf("%lld:",i+1);long q=lo;while(q<=hi){long e=q;while(e<=hi&&t[e]==t[q])e++;printf(" %d^%ld",t[q],e-q);q=e;}printf("\n");}}
    if(p>hi)hi=p;
    if(hi-lo>L/2-10){printf("size\n");return 1;}
  }
  printf("done\n");
}
