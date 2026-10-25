// tailgrid MACHINE : for h in 1..10 and tails (segment sequences, last = 1-run), list prefixes, check halting
#include "spec.h"
#include <random>
int main(int argc,char**argv){
  string ms=argv[1]; long long MS=atoll(argv[2]); int NR=atoi(argv[3]);
  T tm[16][2]; load_tm(ms,tm); mt19937_64 rng(7);
  auto R=[&](int a,int b){ return (int)(rng()%(b-a+1))+a; };
  long long SZ=1LL<<24; vector<uint8_t> tape(SZ,0);
  vector<vector<int>> tails;
  for(int a=1;a<=8;a++) tails.push_back({a});
  for(int a=1;a<=8;a++) for(int b=1;b<=8;b++) tails.push_back({a,b});
  for(int a=1;a<=8;a++) for(int b=1;b<=8;b++) for(int c=1;c<=3;c++) tails.push_back({a,b,c});
  for(int h=1;h<=10;h++) for(auto&tl:tails){
    int halts=0; long long minst=-1; string ex;
    for(int rep=0;rep<NR;rep++){
      string w; int k=R(0,5); if(R(0,1)) w+="11"; for(int i=0;i<k;i++){ int t=R(0,9); for(int j=0;j<t;j++) w+="10"; w+="1"; }
      int r=R(1,8); for(int j=0;j<r;j++) w+="10"; w+=string(h,'1'); for(int x:tl){ w+="00"; w+=string(x,'1'); }
      size_t a=w.find('1'); w=w.substr(a);
      long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
      long long p=off+w.size(); int q=1; long long st; long long mn=off,mx=p; bool hl=false;
      for(st=0;st<MS;st++){ int c=tape[p]; T&t=tm[q][c]; if(!t.ok){hl=true;break;} tape[p]=t.w; p+=t.d; q=t.n; if(p<mn)mn=p; if(p>mx)mx=p; if(p<10||p>SZ-10)break; }
      for(long long i=mn-2;i<=mx+2;i++) tape[i]=0;
      if(hl){ halts++; if(minst<0||st<minst){minst=st; ex=w;} }
    }
    if(halts){ printf("h=%d tail=",h); for(int x:tl) printf("%d,",x); printf(" halts %d/%d min steps %lld ex %s\n",halts,NR,minst,ex.c_str()); }
  }
}
