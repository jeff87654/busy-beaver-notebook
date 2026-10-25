// reach START TARGET STATE MAXSTEPS : start word with head in STATE on the blank right of it;
// report the first step at which the configuration equals TARGET (word, head on blank right of it, STATE).
// Also prints HALT if E0 is read.
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms="1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF";
  string w=argv[1], tg=argv[2]; int q=argv[3][0]-'A'; long long N=atoll(argv[4]);
  int qt = argc>5 ? argv[5][0]-'A' : q;
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<26; vector<uint8_t> tape(SZ,0); long long p=SZ/2;
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p-w.size(), mx=p;
  // target: tape[p-len..p-1]==tg, everything else zero, head at p in state qt
  long long ones_t=0; for(char c:tg) ones_t+=c-'0';
  long long ones=0; for(char c:w) ones+=c-'0';
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld\n", st); return 0;}
    ones += t.w - c;
    tape[p]=t.w; p+=t.d; q=t.n;
    if(p<mn) mn=p; if(p>mx) mx=p;
    if(p<10||p>SZ-10){printf("EDGE %lld\n",st);return 0;}
    if(q==qt && ones==ones_t && tape[p]==0){
      long long L=tg.size(); bool ok = true;
      for(long long i=0;i<L && ok;i++) if(tape[p-L+i]!=tg[i]-'0') ok=false;
      if(ok){ printf("REACHED at step %lld\n", st+1); return 0; }
    }
  }
  printf("NOT REACHED in %lld\n",N);
}
