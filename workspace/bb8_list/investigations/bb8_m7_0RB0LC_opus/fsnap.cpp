// fsnap MACHINE RUNSPEC N [hmin] [maxQ]: at B-frontier snapshots print family parse; only when h>=hmin (rest configs); prints raw runs when parse fails
#include "fam.h"
int main(int argc,char**argv){
  string ms=argv[1]; string w=spec_word(argv[2]); long long N=atoll(argv[3]); long long hmin=argc>4?atoll(argv[4]):3; size_t maxQ=argc>5?atoll(argv[5]):200; long long maxcfg=argc>6?atoll(argv[6]):(1LL<<60); long long ncfg=0;
  T tm[16][2]; load_tm(ms,tm);
  long long SZ=getenv("FSZ")?atoll(getenv("FSZ")):(1LL<<26); vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+(long long)w.size(), mn=off, mx=p; int q=1; long long cnt=0;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b; printf("HALT at step %lld state %c head-last1 %lld | %s\n",st,'A'+q,p-b,runs(tape,a,b).c_str()); return 0;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<mn) mn=p; if(p>mx) mx=p;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]||p<mx) continue;
    ++cnt; long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b;
    Fam f=parse_fam(tape,a,b);
    if(f.ok && f.h<hmin) continue;
    string s=f.ok? fam_str(f) : ("RAW "+runs(tape,a,b));
    if(f.ok && f.Q.size()>maxQ){ string Q=f.Q; f.Q=Q.substr(0,maxQ/2)+" ... "+Q.substr(Q.size()-maxQ/2); s=fam_str(f); }
    if(s.size()>1500 && !getenv("FSNAP_NOTRUNC")) s=s.substr(0,700)+" ... "+s.substr(s.size()-700);
    printf("%lld [%lld] %s\n",st+1,cnt,s.c_str()); fflush(stdout);
    if(++ncfg>=maxcfg){ printf("stop\n"); return 0; }
  }
  printf("done N=%lld cnt=%lld\n",N,cnt);
}
