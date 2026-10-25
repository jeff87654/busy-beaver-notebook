// e0z MACHINE WORD STATE N : literal run; counts reads of E0 / F0 / G0 by whether the next cell is 0 (and next two). prints first step of each "E0 followed by 0".
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<27; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2];
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long e0=0,e0z=0,fe=-1; long long st=0; bool halted=false;
  for(;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(q==4&&c==0){ e0++; if(tape[p+1]==0){ e0z++; if(fe<0) fe=st; } }
    if(!t.ok){halted=true;break;}
    tape[p]=t.w; p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);break;}
  }
  printf("%s steps %lld E0 reads %lld, E0 followed by 0: %lld first@%lld\n",halted?"HALT":"ok",st,e0,e0z,fe);
}
