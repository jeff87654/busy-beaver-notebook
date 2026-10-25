// simc LEFT STATE SCANNED RIGHT N [machine]: literal run from a concrete configuration; prints HALT step or run, and the final tape (RLE)
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argc>6?argv[6]:"1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE"; long long N=atoll(argv[5]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<25; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[2][0]-'A';
  string L=argv[1],R=argv[4]; if(L=="-")L=""; if(R=="-")R="";
  for(size_t i=0;i<L.size();i++) tape[p-L.size()+i]=L[i]-'0';
  tape[p]=argv[3][0]-'0';
  for(size_t i=0;i<R.size();i++) tape[p+1+i]=R[i]-'0';
  long long st=0;
  for(;st<N;st++){ T&t=tm[q][tape[p]]; if(!t.ok){printf("HALT %lld\n",st);return 0;} tape[p]=t.w; p+=t.d; q=t.n; if(p<10||p>SZ-10){printf("EDGE\n");return 0;} }
  printf("run %lld\n",st);
}
