// ectx MACHINE WORD STATE N nl nr : literal run; for every read of E0 (state E scanning 0), record the context (left nl cells, right nr cells); print counts
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]); int nl=atoi(argv[5]), nr=atoi(argv[6]); char QS=argc>7?argv[7][0]:'E'; int QM=argc>8?atoi(argv[8]):0;
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<27; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2];
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  map<string,long long> cnt; map<string,long long> first;
  long long st=0;
  for(;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(q==QS-'A' && c==QM){ string s; for(int j=nl;j>=1;j--) s+=char('0'+tape[p-j]); s+=" . "; for(int j=1;j<=nr;j++) s+=char('0'+tape[p+j]); if(!cnt[s]++) first[s]=st; }
    if(!t.ok){ printf("HALT at %lld\n",st); break;}
    tape[p]=t.w; p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);break;}
  }
  printf("steps %lld, %zu distinct contexts\n",st,cnt.size());
  vector<pair<long long,string>> v; for(auto&kv:cnt) v.push_back({kv.second,kv.first});
  sort(v.rbegin(),v.rend()); for(size_t i=0;i<v.size()&&i<60;i++) printf("%10lld  %s  first@%lld\n",v[i].first,v[i].second.c_str(),first[v[i].second]);
}
