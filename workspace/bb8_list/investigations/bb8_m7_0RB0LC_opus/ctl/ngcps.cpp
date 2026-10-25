// ngcps MACHINE n : plain n-gram closed position set decider. Prints NONHALT (closed, no halting config) or FAIL.
#include <bits/stdc++.h>
using namespace std;
struct Tr{int w,d,q; bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; int n=atoi(argv[2]); int start=argc>3?argv[3][0]-'A':0;
  Tr tm[16][2]; int S=0; { stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){ string t=r.substr(3*c,3); if(t[0]=='-'||t[2]=='Z') tm[S][c]={0,0,0,false}; else tm[S][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true}; } S++; } }
  uint64_t mask=(n==64)?~0ULL:((1ULL<<n)-1);
  // left n-gram: bits, bit 0 = nearest to head (rightmost). right n-gram: bit 0 = nearest to head (leftmost).
  vector<char> LS(1ULL<<n,0), RS(1ULL<<n,0); LS[0]=RS[0]=1;
  // config key: q (4 bits) | m (1) | l (n) | r (n)
  auto key=[&](int q,int m,uint64_t l,uint64_t r){ return ((uint64_t)q<<(2*n+1))|((uint64_t)m<<(2*n))|(l<<n)|r; };
  unordered_set<uint64_t> seen; deque<uint64_t> work;
  auto add=[&](uint64_t k){ if(seen.insert(k).second) work.push_back(k); };
  add(key(start,0,0,0));
  bool changed=true; long long iters=0;
  // we must re-process configs when LS/RS grow: simple approach: loop until no change, re-scanning all configs.
  vector<uint64_t> all;
  while(changed){
    changed=false; iters++;
    while(!work.empty()){ uint64_t k=work.front(); work.pop_front(); all.push_back(k); }
    for(size_t idx=0; idx<all.size(); idx++){
      uint64_t k=all[idx]; uint64_t r=k&mask, l=(k>>n)&mask; int m=(k>>(2*n))&1; int q=(int)(k>>(2*n+1));
      Tr t=tm[q][m];
      if(!t.ok){ printf("FAIL n=%d: halting config reachable: state %c m=%d\n",n,'A'+q,m);
        string ls,rs; for(int i=n-1;i>=0;i--) ls+=char('0'+((l>>i)&1)); for(int i=0;i<n;i++) rs+=char('0'+((r>>i)&1)); printf("  local: %s [%c%d] %s\n",ls.c_str(),'A'+q,m,rs.c_str()); return 0; }
      if(t.d==1){
        uint64_t nl=((l<<1)|t.w)&mask; if(!LS[nl]){ LS[nl]=1; changed=true; }
        int nm=r&1; uint64_t rb=r>>1;
        for(int x=0;x<2;x++){ uint64_t nr=rb|((uint64_t)x<<(n-1)); if(RS[nr]){ uint64_t kk=key(t.q,nm,nl,nr); if(seen.insert(kk).second){ all.push_back(kk); changed=true; } } }
      } else {
        uint64_t nr=((r<<1)|t.w)&mask; if(!RS[nr]){ RS[nr]=1; changed=true; }
        int nm=l&1; uint64_t lb=l>>1;
        for(int x=0;x<2;x++){ uint64_t nl=lb|((uint64_t)x<<(n-1)); if(LS[nl]){ uint64_t kk=key(t.q,nm,nl,nr); if(seen.insert(kk).second){ all.push_back(kk); changed=true; } } }
      }
    }
    fprintf(stderr,"iter %lld configs %zu\n",iters,all.size());
  }
  long long nl=0,nr=0; for(auto c:LS) nl+=c; for(auto c:RS) nr+=c;
  printf("NONHALT n=%d: closed set with %zu configs, %lld left %d-grams, %lld right %d-grams\n",n,all.size(),nl,n,nr,n);
}
