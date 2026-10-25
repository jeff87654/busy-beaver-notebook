// blank.cpp: literal run from blank tape (or a given word), report family configs (state B on blank, nothing to the right)
// usage: blank MACHINE N [word] [state]
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[2]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<28; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=0;
  string w= argc>3?argv[3]:""; if(argc>4) q=argv[4][0]-'A';
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p,mx=p-1; for(size_t i=0;i<w.size();i++) if(w[i]=='1'){ if(mn>mx) mn=mx=p-w.size()+i; else mx=p-w.size()+i; }
  const string P="11",S="111001";
  long long cnt=0; long long nextprint=1;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld  ones: ", st, 'A'+q, p); long long ones=0; for(long long i=mn;i<=mx;i++) ones+=tape[i]; printf("%lld span %lld\n",ones,mx-mn+1); return 0;}
    tape[p]=t.w; if(t.w){ if(mn>mx) mn=mx=p; else {mn=min(mn,p); mx=max(mx,p);} }
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    while(mx>p && !tape[mx]) --mx;
    if(mx>p) continue;
    while(mn<p && !tape[mn]) ++mn;
    long long lo=mn<p?mn:p; long long len=p-lo;
    if(len<(long long)(P.size()+S.size())) continue;
    // check suffix
    bool ok=true; for(size_t i=0;i<S.size();i++) if(tape[p-S.size()+i]!=S[i]-'0') ok=false;
    if(!ok) continue; if(tape[lo]!=1||tape[lo+1]!=1) continue;
    long long x=p-S.size(), z=lo+2; vector<long long> runs; bool good=true;
    for(;;){ long long k=0; while(x-2>=z && tape[x-2]==1 && tape[x-1]==0){x-=2;k++;} runs.push_back(k); if(x==z)break; if(x-1<z||tape[x-1]!=1){good=false;break;} x--; }
    if(!good||runs.size()<2) continue;
    long long b=runs[0]-2; if(b<0||b%3) continue; b/=3;
    vector<long long> ds; bool g2=true; for(size_t i=1;i<runs.size();i++){ if(runs[i]<1||(runs[i]-1)%3){g2=false;break;} ds.push_back((runs[i]-1)/3);} if(!g2) continue;
    long long a=ds[0]; ds.erase(ds.begin()); reverse(ds.begin(),ds.end());
    cnt++;
    if(true){ printf("step %lld K(", st+1); size_t m=ds.size(); for(size_t i=0;i<m;i++) printf("%s%lld",i?",":"",ds[i]);  printf("; %lld; %lld)\n",a,b); }
  }
  printf("done N=%lld cfgs=%lld\n",N,cnt);
}
