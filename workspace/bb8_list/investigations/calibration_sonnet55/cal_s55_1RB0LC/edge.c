#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int T[8][2][3];
int main(int argc,char**argv){
  const char*M="1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA";
  for(int i=0;i<8;i++)for(int s=0;s<2;s++){const char*e=M+i*7+3*s; if(e[0]=='-'){T[i][s][0]=-1;}else{T[i][s][0]=e[0]-'0';T[i][s][1]=e[1]=='R'?1:-1;T[i][s][2]=e[2]-'A';}}
  long long N=atoll(argv[1]); int SZ=1<<26; char*tp=calloc(SZ,1); long p=SZ/2,lo=p,hi=p; int q=0;
  for(long long t=0;t<N;t++){
    if(p<lo-0){ /* new left edge */ 
      lo=p; }
    if(p<lo){ }
    int *r=T[q][(int)tp[p]]; if(r[0]<0){printf("HALT t=%lld q=%d p=%ld\n",t,q,p);break;}
    /* left edge event: head moved left of leftmost 1 */
    tp[p]=r[0]; p+=r[1]; q=r[2]; if(p<lo)lo=p; if(p>hi)hi=p;
    if(p<=lo && q!=-1){
      /* check tape at p and left is zero: p<=lo means p is at leftmost visited */
    }
  }
  printf("end p=%ld q=%d lo=%ld hi=%ld\n",p-SZ/2,q,lo-SZ/2,hi-SZ/2);
}
