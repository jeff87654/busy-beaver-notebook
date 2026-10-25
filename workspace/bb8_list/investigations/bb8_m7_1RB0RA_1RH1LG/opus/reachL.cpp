// reachL START HEADPOS STATE TARGET THEADPOS TSTATE MAXSTEPS : general reachability with explicit head positions
// (head position = index into the word; may be -1 or len). Exact tape equality (all ones inside the word span).
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms="1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF";
  string w=argv[1]; long long hp=atoll(argv[2]); int q=argv[3][0]-'A';
  string tg=argv[4]; long long thp=atoll(argv[5]); int qt=argv[6][0]-'A'; long long N=atoll(argv[7]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<26; vector<uint8_t> tape(SZ,0); long long base=SZ/2;
  for(size_t i=0;i<w.size();i++) tape[base+i]=w[i]-'0';
  long long p=base+hp;
  long long ones=0; for(char c:w) ones+=c-'0';
  long long ones_t=0; for(char c:tg) ones_t+=c-'0';
  long long L=tg.size();
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld\n", st); return 0;}
    ones += t.w - c; tape[p]=t.w; p+=t.d; q=t.n;
    if(p<10||p>SZ-10){printf("EDGE %lld\n",st);return 0;}
    if(q==qt && ones==ones_t){
      long long s0=p-thp; bool ok=true;
      for(long long i=0;i<L&&ok;i++) if(tape[s0+i]!=tg[i]-'0') ok=false;
      if(ok){ printf("REACHED at step %lld\n", st+1); return 0; }
    }
  }
  printf("NOT REACHED in %lld\n",N);
}
