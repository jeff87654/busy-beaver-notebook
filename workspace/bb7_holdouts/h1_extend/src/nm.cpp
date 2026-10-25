// nm MACHINE WORD POS Q MAXSTEPS PAT : literal run from tape WORD at cells 0.., head at POS (may be -1), state Q;
// counts occurrences of the transition n-gram PAT (e.g. "A1E1" = near miss) and prints HALT/END + count.
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string m=argv[1], word=argv[2]; long long P0=atoll(argv[3]); int q=argv[4][0]-'A'; long long MX=atoll(argv[5]); string pat=argv[6];
  int w[16][2],d[16][2],nx[16][2],S=0; {stringstream ss(m);string r;while(getline(ss,r,'_')){for(int c=0;c<2;c++){string t=r.substr(3*c,3);if(t[0]=='-'){w[S][c]=0;d[S][c]=0;nx[S][c]=-1;}else{w[S][c]=t[0]-'0';d[S][c]=t[1]=='R'?1:-1;nx[S][c]=t[2]-'A';}}S++;}}
  long long N=1<<22; vector<unsigned char> T(N,0); long long base=N/2; for(size_t i=0;i<word.size();i++) T[base+i]=word[i]-'0'; long long p=base+P0;
  string h; long long cnt=0, s; int L=pat.size();
  for(s=0;s<MX;s++){
    int c=T[p]; h+=char('A'+q); h+=char('0'+c); if((int)h.size()>L) h.erase(0,h.size()-L); if(h==pat) cnt++;
    if(nx[q][c]<0){ printf("HALT %lld %c%d near=%lld\n",s,'A'+q,c,cnt); return 0; }
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c];
    if(p<2||p>=N-2){ vector<unsigned char> T2(2*N,0); memcpy(&T2[N/2],T.data(),N); T.swap(T2); p+=N/2; base+=N/2; N*=2; }
  }
  printf("END near=%lld\n",cnt);
}
