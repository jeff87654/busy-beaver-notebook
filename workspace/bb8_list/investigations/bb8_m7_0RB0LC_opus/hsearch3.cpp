// hsearch3 MACHINE SEED NCONF MAXSTEPS : random "reachable-like" configurations with standard tails, report any halt
#include "spec.h"
#include <random>
int main(int argc,char**argv){
  string ms=argv[1]; unsigned seed=atoi(argv[2]); long long NC=atoll(argv[3]); long long MS=atoll(argv[4]);
  T tm[16][2]; load_tm(ms,tm); mt19937_64 rng(seed);
  auto R=[&](int a,int b){ return (int)(rng()%(b-a+1))+a; };
  long long SZ=1LL<<25; vector<uint8_t> tape(SZ,0); long long halts=0;
  auto toklist=[&](string&w,int k,int maxt){ for(int i=0;i<k;i++){ int t=R(0,maxt); for(int j=0;j<t;j++) w+="10"; w+="1"; } };
  for(long long ci=0;ci<NC;ci++){
    string w;
    int nseg=R(0,3);
    for(int s=0;s<nseg;s++){
      int qt=R(0,5);
      if(qt==0){ w+="1010111"; }
      else if(qt==1){ int k=R(1,10); for(int i=0;i<k;i++) w+="100"; w.pop_back(); w.pop_back(); }
      else if(qt==2){ toklist(w,R(1,5),12); w.pop_back(); }   // token list segment
      else if(qt==3){ w+="11"; toklist(w,R(0,4),12); w.pop_back(); }
      else if(qt==4){ w+="111011"; }
      else { w+=string(R(1,8),'1'); }
      w+="00";
    }
    int mode=R(0,2);
    if(mode==0){ // rebuild-like: (1|)^K X| (6|)^j 1| 1.
      int K=R(0,30); for(int i=0;i<K;i++) w+="100"; w+=string(R(1,14),'1'); int j=R(0,3); for(int i=0;i<j;i++) w+="00111111"; w+="001001";
    } else {
      int k=R(0,7); toklist(w,k,R(2,10));
      int r=R(1,10); for(int j=0;j<r;j++) w+="10";
      int h= R(0,1)?3:8; w+=string(h,'1');
      if(h==3) w+="001"; else { int j=R(0,3); for(int i=0;i<j;i++) w+="00111111"; w+="001001"; }
    }
    size_t a=w.find('1'); if(a==string::npos) continue; w=w.substr(a);
    long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
    long long p=off+w.size(); int q=1; bool halted=false; long long st=0; long long mn=off, mx=p;
    for(st=0;st<MS;st++){ int c=tape[p]; T&t=tm[q][c]; if(!t.ok){ halted=true; break;} tape[p]=t.w; p+=t.d; q=t.n; if(p<mn)mn=p; if(p>mx)mx=p; if(p<10||p>SZ-10) break; }
    if(halted){ halts++; if(halts<=40) printf("HALT conf %lld steps %lld word %s\n",ci,st,w.c_str()); fflush(stdout); }
    for(long long i=mn-2;i<=mx+2;i++) tape[i]=0;
  }
  printf("seed %u: %lld configs, %lld halts\n",seed,NC,halts);
}
