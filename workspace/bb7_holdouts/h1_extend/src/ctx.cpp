// ctx MACHINE MAXSTEPS PAT W [MAXPRINT]: literal run; whenever the last transitions match PAT (e.g. "G1A1"), print step,
// distance to the left/right tape ends, and the window of W cells each side of the head (head cell in brackets).
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string m=argv[1]; long long MX=atoll(argv[2]); string pat=argv[3]; int W=atoi(argv[4]); int MP=argc>5?atoi(argv[5]):200;
  int w[16][2],d[16][2],nx[16][2],S=0; {stringstream ss(m);string r;while(getline(ss,r,'_')){for(int c=0;c<2;c++){string t=r.substr(3*c,3);if(t[0]=='-'){w[S][c]=0;d[S][c]=0;nx[S][c]=-1;}else{w[S][c]=t[0]-'0';d[S][c]=t[1]=='R'?1:-1;nx[S][c]=t[2]-'A';}}S++;}}
  const long long N=1<<27; vector<unsigned char> T(N,0); long long p=N/2,lo=p,hi=p; int q=0; string h; int np=0;
  for(long long s=0;s<MX;s++){
    int c=T[p]; h+=char('A'+q); h+=char('0'+c); if(h.size()>pat.size()) h.erase(0,h.size()-pat.size());
    if(h==pat && np<MP){ np++; string L,R; for(long long i=p-W;i<p;i++) L+=char('0'+T[i]); for(long long i=p+1;i<=p+W;i++) R+=char('0'+T[i]);
      printf("%lld dl=%lld dr=%lld %s[%d]%s\n",s,p-lo,hi-p,L.c_str(),c,R.c_str()); }
    if(nx[q][c]<0){printf("HALT at %lld\n",s);break;}
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c]; if(p<lo)lo=p; if(p>hi)hi=p; if(p<2||p>N-3){printf("overflow\n");break;}
  }
}
