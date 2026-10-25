// usage: count how often each transition fires in a literal run from the blank tape, and when it first/last fired.
//   usage MACHINE STEPS
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string tm=argv[1]; long long S=atoll(argv[2]); int n=(tm.size()+1)/7;
  int nx[16][2],wr[16][2],dr[16][2];
  for(int q=0;q<n;q++)for(int c=0;c<2;c++){const char*t=tm.c_str()+7*q+3*c; if(t[2]=='-'||t[2]=='Z'){nx[q][c]=-1;continue;} wr[q][c]=t[0]-'0'; dr[q][c]=t[1]=='R'?1:-1; nx[q][c]=t[2]-'A';}
  long long N=1<<24; vector<uint8_t> T(N,0); long long p=N/2; int q=0;
  long long cnt[16][2]={},first[16][2],last[16][2],ep[16][2]={}; for(auto&r:first)for(auto&x:r)x=-1;
  long long st=0;
  for(;st<S;st++){ int c=T[p]; if(nx[q][c]<0){printf("halt at %lld\n",st);break;}
    if(last[q][c]<st-1000||first[q][c]<0) ep[q][c]++; // episodes: separated by >1000 steps
    if(first[q][c]<0) first[q][c]=st; last[q][c]=st; cnt[q][c]++;
    T[p]=wr[q][c]; p+=dr[q][c]; q=nx[q][c]; if(p<1||p>=N-1){printf("tape out\n");break;} }
  for(int s=0;s<n;s++)for(int c=0;c<2;c++) printf("%c%d %s count=%lld frac=%.2e first=%lld episodes=%lld\n",'A'+s,c,
     nx[s][c]<0?"---":string(tm.c_str()+7*s+3*c,3).c_str(),cnt[s][c],cnt[s][c]/(double)st,first[s][c],ep[s][c]);
}
