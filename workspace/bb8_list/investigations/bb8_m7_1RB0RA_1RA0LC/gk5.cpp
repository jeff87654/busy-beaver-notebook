// gk5 MACHINE WORD STATE N maxprint TAIL PFLAG : literal run; at every B-at-frontier snapshot ending in TAIL, parse
//   [11] D(m1)..D(mk) (10)^r TAIL, D(m)=(10)^m 1 (m>=0); print step, tokens, r.   PFLAG=1: require leading 11.
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]); int maxprint=atoi(argv[5]); string tail=argv[6]; int pflag=atoi(argv[7]);
  long long skipn = argc>8? atoll(argv[8]):0;
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<29; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2];
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p-w.size(),mx=p; int cnt=0; long long TL=tail.size();
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld\n", st, 'A'+q, p-SZ/2); return 0;}
    tape[p]=t.w; if(t.w){ mn=min(mn,p); mx=max(mx,p);} 
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    if(st<skipn) continue;
    while(mx>=p && !tape[mx]) --mx; 
    if(mx>=p) continue;
    while(mn<p && !tape[mn]) ++mn;
    long long L=p-mn; if(L<TL) continue;
    bool ok=true; for(long long u=0;u<TL;u++) if(tape[p-TL+u]!=tail[u]-'0'){ok=false;break;}
    if(!ok) continue;
    long long e=p-TL; // end of body (exclusive)
    long long i=mn;
    if(pflag){ if(!(e-i>=2&&tape[i]==1&&tape[i+1]==1)) continue; i+=2; }
    vector<long long> toks; long long r=0; bool good=true;
    while(true){
      long long j=0; while(i+1<e && tape[i]==1&&tape[i+1]==0){ i+=2; j++; }
      if(i==e){ r=j; break; }
      if(tape[i]==1){ toks.push_back(j); i++; if(i>e){good=false;break;} continue; }
      good=false; break;
    }
    if(!good) continue;
    cnt++; if(cnt<=maxprint){ printf("step %lld K[",st+1); for(size_t k=0;k<toks.size();k++) printf("%s%lld",k?",":"",toks[k]); printf("] r=%lld\n",r); }
  }
  printf("done N=%lld cnt=%d\n",N,cnt);
}
