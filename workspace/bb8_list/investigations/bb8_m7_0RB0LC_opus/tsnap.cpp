// tsnap MACHINE WORD HEAD STATE N [fac] [first] [every]: run-structure of tape at B-frontier snapshots
// output: 1-run lengths separated by ' ' (single 0) or ' | ' (00) or ' |k| ' (0^k, k>=3); k consecutive single-1 runs -> 1^k
#include "runs.h"
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; string w=argv[2]; long long head=atoll(argv[3]); int q=argv[4][0]-'A'; long long N=atoll(argv[5]);
  double fac=argc>6?atof(argv[6]):1.5; long long first=argc>7?atoll(argv[7]):20;
  T tm[16][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<29; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+head, mn=off, mx=off+(long long)w.size()-1; double nxt=first; long long cnt=0;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b;
      printf("HALT at step %lld state %c head %lld | %s\n",st,'A'+q,p-off,runs(tape,a,b).c_str()); return 0;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<mn) mn=p; if(p>mx) mx=p;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    if(p<mx) continue;
    ++cnt; if(cnt<first || cnt>=nxt){ if(cnt>=nxt) nxt=nxt*fac+1;
      long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b;
      printf("%lld [%lld] %s\n",st+1,cnt,runs(tape,a,b).c_str()); }
  }
  printf("done N=%lld cnt=%lld\n",N,cnt);
}
