// hsearch MACHINE SEED NCONF MAXSTEPS : random family-like configurations, report any halt
#include "spec.h"
#include <random>
int main(int argc,char**argv){
  string ms=argv[1]; unsigned seed=atoi(argv[2]); long long NC=atoll(argv[3]); long long MS=atoll(argv[4]);
  T tm[16][2]; load_tm(ms,tm); mt19937_64 rng(seed);
  auto R=[&](int a,int b){ return (int)(rng()%(b-a+1))+a; };
  long long SZ=1LL<<24; vector<uint8_t> tape(SZ,0); long long halts=0;
  for(long long ci=0;ci<NC;ci++){
    string w;
    // prefix Q: random choice
    int qt=R(0,6);
    if(qt==1){ w+="1010111"; int k=R(0,8); for(int i=0;i<k;i++) w+="00"+string(1,'1'); w+="00"; }
    else if(qt==2){ w+="11011"; int k=R(0,5); for(int i=0;i<k;i++) w+="0"+string(1,'1'); w+="00"; }
    else if(qt==3){ int k=R(1,6); for(int i=0;i<k;i++){ w+="1"; w+= string(R(1,2),'0'); } }
    else if(qt==4){ // token list with 00 boundary
      int k=R(1,4); for(int i=0;i<k;i++){ int t=R(0,10); for(int j=0;j<t;j++) w+="10"; w+="1"; } w+="00"; if(R(0,1)){ w+="111001"; } }
    else if(qt==5){ w+="1010111"; int k=R(0,8); for(int i=0;i<k;i++) w+="001"; w+="00"; int x=R(1,12); w+=string(x,'1'); w+="00"; }
    // list
    int k=R(0,6); for(int i=0;i<k;i++){ int t=R(0,12); for(int j=0;j<t;j++) w+="10"; w+="1"; }
    int r=R(0,12); for(int j=0;j<r;j++) w+="10";
    int ht=R(0,1); int h= ht==0?3: 8;
    w+=string(h,'1');
    if(h==3){ w+="001"; }
    else { int j=R(0,3); for(int i=0;i<j;i++) w+="00111111"; w+="001001"; }
    // strip leading zeros
    size_t a=w.find('1'); if(a==string::npos) continue; w=w.substr(a);
    fill(tape.begin(),tape.end(),0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
    long long p=off+w.size(); int q=1; bool halted=false; long long st=0;
    for(st=0;st<MS;st++){ int c=tape[p]; T&t=tm[q][c]; if(!t.ok){ halted=true; break;} tape[p]=t.w; p+=t.d; q=t.n; if(p<10||p>SZ-10) break; }
    if(halted){ halts++; if(halts<=30) printf("HALT conf %lld steps %lld word %s\n",ci,st,w.c_str()); }
  }
  printf("seed %u: %lld configs, %lld halts\n",seed,NC,halts);
}
