// litk MACHINE WORD Q MAXSTEPS : literal run from tape WORD (cells 0..len-1), head at len (right of word), state Q.
// prints HALT step state read ones, or END. Also counts entries into each state.
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string m=argv[1], word=argv[2]; int q=atoi(argv[3]); long long MX=atoll(argv[4]);
  int w[16][2],d[16][2],nx[16][2],S=0; {stringstream ss(m);string r;while(getline(ss,r,'_')){for(int c=0;c<2;c++){string t=r.substr(3*c,3);if(t[0]=='-'){w[S][c]=0;d[S][c]=0;nx[S][c]=-1;}else{w[S][c]=t[0]-'0';d[S][c]=t[1]=='R'?1:-1;nx[S][c]=t[2]-'A';}}S++;}}
  long long N=1<<24; vector<unsigned char> T(N,0); long long base=N/2; for(size_t i=0;i<word.size();i++) T[base+i]=word[i]-'0'; long long p=base+word.size();
  long long lo=base, hi=p; long long ent[16]={0};
  for(long long s=0;s<MX;s++){
    int c=T[p]; if(nx[q][c]<0){ long long o=0; for(long long i=lo;i<=hi;i++) o+=T[i]; printf("HALT %lld %c%d ones=%lld width=%lld\n",s,'A'+q,c,o,hi-lo+1); return 0; }
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c]; ent[q]++; if(p<lo)lo=p; if(p>hi)hi=p;
    if(p<2||p>=N-2){ // grow
      vector<unsigned char> T2(2*N,0); memcpy(&T2[N/2],T.data(),N); T.swap(T2); p+=N/2; lo+=N/2; hi+=N/2; N*=2; }
  }
  printf("END width=%lld entH=%lld\n",hi-lo+1,ent[7]);
}
