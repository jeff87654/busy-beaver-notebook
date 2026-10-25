// dsim: direct TM simulator (2 symbols), byte tape.  dsim MACHINE MAXSTEPS [SNAPEVERY]
// prints HALT state/sym, steps, ones; or RUN at limit. Optional RLE snapshots every SNAPEVERY steps.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
int main(int argc,char**argv){
  std::string m=argv[1]; ll maxs=atoll(argv[2]); ll snap=argc>3?atoll(argv[3]):0;
  int n=(m.size()+1)/7; int W[32],D[32],N[32];
  for(int q=0;q<n;q++)for(int c=0;c<2;c++){const char*x=m.c_str()+q*7+c*3;
    int i=q*2+c; if(x[0]=='-'||x[2]=='Z'||x[2]-'A'>=n){W[i]=-1;continue;} W[i]=x[0]-'0';D[i]=x[1]=='R'?1:-1;N[i]=x[2]-'A';}
  ll L=1LL<<26; std::vector<unsigned char> t(L,0); ll p=L/2,lo=p,hi=p; int s=0; ll st=0;
  while(st<maxs){
    int i=s*2+t[p]; if(W[i]<0){ ll ones=0; for(ll k=lo;k<=hi;k++)ones+=t[k];
      printf("HALT %c%d steps %lld ones %lld\n",'A'+s,t[p],st,ones); return 0;}
    t[p]=W[i]; p+=D[i]; s=N[i]; st++;
    if(p<lo){lo=p; if(p<=0){fprintf(stderr,"tape\n");return 1;}} if(p>hi){hi=p; if(p>=L-1){fprintf(stderr,"tape\n");return 1;}}
    if(snap&&st%snap==0){ printf("@%lld %c ",st,'A'+s); // RLE of tape lo..hi with head marker
      ll k=lo; while(k<=hi){ ll j=k; while(j<=hi&&t[j]==t[k]&&j!=p)j++; if(k==p){printf("[%d]",t[k]);k++;continue;} printf("%d^%lld ",t[k],j-k); k=j;} printf("\n");}
  }
  ll ones=0; for(ll k=lo;k<=hi;k++)ones+=t[k];
  printf("RUN steps %lld ones %lld width %lld\n",st,ones,hi-lo+1); return 0;}
