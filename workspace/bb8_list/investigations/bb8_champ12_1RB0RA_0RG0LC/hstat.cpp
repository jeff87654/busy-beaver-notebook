// count reads of (state,symbol) pairs along a literal run: hstat MACHINE N [word state]
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[2]);
  int W[8][2],D[8][2],NX[8][2]; bool ok[8][2];
  {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); ok[i][c]=t!="---"; if(ok[i][c]){W[i][c]=t[0]-'0';D[i][c]=t[1]=='R'?1:-1;NX[i][c]=t[2]-'A';}} i++;}}
  long long SZ=1LL<<27; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=0;
  string w=argc>3?argv[3]:""; if(argc>4) q=argv[4][0]-'A';
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long cnt[8][2]={};
  for(long long st=0;st<N;st++){ int c=tape[p]; cnt[q][c]++; if(!ok[q][c]){printf("HALT step %lld\n",st);break;} tape[p]=W[q][c]; p+=D[q][c]; q=NX[q][c]; if(p<100||p>SZ-100) break;}
  for(int s=0;s<8;s++) printf("%c: %lld %lld\n",'A'+s,cnt[s][0],cnt[s][1]);
}
