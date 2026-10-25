// lastsnap MACHINE word state N : run N steps; print the last two B-at-frontier snapshots (raw bits) and the final state
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1];
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<27; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2]; long long N=atoll(argv[4]);
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p-w.size(),mx=p; string s1,s2; long long st1=0,st2=0;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld\n", st, 'A'+q, p-SZ/2); long long ones=0; for(long long i=mn;i<=mx;i++) ones+=tape[i]; printf("ones %lld\n",ones); return 0;}
    tape[p]=t.w; if(t.w){ mn=min(mn,p); mx=max(mx,p);} 
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    while(mx>=p && !tape[mx]) --mx; 
    if(mx>=p) continue;
    while(mn<p && !tape[mn]) ++mn;
    if(st+1+3000<N) continue;
    s2=s1; st2=st1; s1.clear(); st1=st+1; for(long long i=mn;i<p;i++) s1.push_back('0'+tape[i]);
  }
  if(st2) printf("%lld %s\n",st2,s2.c_str()); if(st1) printf("%lld %s\n",st1,s1.c_str());
  printf("end state %c head %lld\n",'A'+q,p-SZ/2);
}
