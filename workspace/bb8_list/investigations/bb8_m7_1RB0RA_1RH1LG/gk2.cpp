// gk MACHINE word state N maxprint : literal run; at every B-at-frontier snapshot test generalized K form
//   11 D(m1)..D(mk) (10)^r 111001 , D(m)=(10)^m 1 (m>=1); print step, tokens (left to right), r
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]); int maxprint=atoi(argv[5]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<29; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2];
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p-w.size(),mx=p; int cnt=0;
  static const char S[]="111001";
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld\n", st, 'A'+q, p-SZ/2); return 0;}
    tape[p]=t.w; if(t.w){ mn=min(mn,p); mx=max(mx,p);} 
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    while(mx>=p && !tape[mx]) --mx; 
    if(mx>=p) continue;
    while(mn<p && !tape[mn]) ++mn;
    long long L=p-mn; if(L<8) continue;
    if(tape[mn]!=1||tape[mn+1]!=1) continue;
    long long tt=-1, e=0;
    { if(!(tape[p-1]==1&&tape[p-2]==0&&tape[p-3]==0&&tape[p-4]==1)) continue;
      long long x=p-4; long long t2=0; const int B8[8]={1,1,1,1,1,1,0,0};
      while(x-8>=mn+2){ bool bk=true; for(int u=0;u<8;u++) if(tape[x-8+u]!=B8[u]) {bk=false;break;} if(!bk) break; x-=8; t2++; }
      if(!(tape[x-1]==1&&tape[x-2]==1)) continue;
      tt=t2; e=x-2; }
    long long i=mn+2; vector<long long> toks; long long r=0; bool good=true;
    while(true){
      long long j=0; while(i+1<e && tape[i]==1&&tape[i+1]==0){ i+=2; j++; }
      if(i==e){ r=j; break; }
      if(tape[i]==1 && j>=1){ toks.push_back(j); i++; if(i>e){good=false;break;} continue; }
      good=false; break;
    }
    if(!good) continue;
    cnt++; if(cnt<=maxprint){ printf("step %lld K[",st+1); for(size_t k=0;k<toks.size();k++) printf("%s%lld",k?",":"",toks[k]); printf("] r=%lld\n",r); }
  }
  printf("done N=%lld cnt=%d\n",N,cnt);
}
