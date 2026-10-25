// literal TM sim; prints K-configs (state E, head just left of leftmost 1) as RLE of the nonblank part
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
int main(int argc,char**argv){
  const char* M=argv[1]; long long N=atoll(argv[2]);
  int W[7][2],Dd[7][2],S[7][2];
  for(int s=0;s<7;s++)for(int b=0;b<2;b++){const char*t=M+7*s+3*b; if(t[2]=='-'){S[s][b]=-1;continue;} W[s][b]=t[0]-'0';Dd[s][b]=t[1]=='R'?1:-1;S[s][b]=t[2]-'A';}
  const long long L=1<<26; std::vector<unsigned char> tape(L,0); long long h=L/2, lo=h, hi=h; int s=0;
  for(long long step=0;step<N;step++){
    int b=tape[h];
    if(S[s][b]<0){ long long ones=0; for(long long i=lo;i<=hi;i++) ones+=tape[i]; printf("HALT %lld ones %lld\n",step,ones); return 0;}
    tape[h]=W[s][b]; h+=Dd[s][b]; s=S[s][b];
    if(h<lo)lo=h; if(h>hi)hi=h;
    if(h<=1||h>=L-2){printf("OUT %lld\n",step);return 0;}
    if(s==4 && tape[h]==0){
      long long i=h+1; // check leftmost one is at h+1 (all left of h zero)
      bool ok=tape[h+1]==1; for(long long j=lo;j<h && ok;j++) if(tape[j]) ok=false;
      if(ok){ printf("K %lld",step+1); long long j=h+1; int cur=tape[j]; long long c=0;
        for(;j<=hi+1;j++){ if(tape[j]==cur) c++; else { printf(" %d^%lld",cur,c); cur=tape[j]; c=1; } }
        printf("\n"); fflush(stdout);}
    }
  }
  printf("END %lld\n",N); return 0;
}
