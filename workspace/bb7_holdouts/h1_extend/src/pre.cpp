// pre MACHINE MAXSTEPS : literal run from blank; histogram of the last 4 transitions (state+read) before every
// step, restricted to sequences ending in a given slot's predecessor states (all 4-grams printed with counts).
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string m=argv[1]; long long MX=atoll(argv[2]); int NG=argc>3?atoi(argv[3]):4;
  int w[16][2],d[16][2],nx[16][2],S=0; {stringstream ss(m);string r;while(getline(ss,r,'_')){for(int c=0;c<2;c++){string t=r.substr(3*c,3);if(t[0]=='-'){w[S][c]=0;d[S][c]=0;nx[S][c]=-1;}else{w[S][c]=t[0]-'0';d[S][c]=t[1]=='R'?1:-1;nx[S][c]=t[2]-'A';}}S++;}}
  const long long N=1<<27; vector<unsigned char> T(N,0); long long p=N/2; int q=0;
  map<string,long long> h; string hist;
  for(long long s=0;s<MX;s++){
    int c=T[p]; hist+=char('A'+q); hist+=char('0'+c); if((int)hist.size()>2*NG) hist.erase(0,2);
    h[hist]++;
    if(nx[q][c]<0){printf("HALT at %lld\n",s);break;}
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c]; if(p<2||p>N-3){printf("overflow\n");break;}
  }
  for(auto&e:h) printf("%s %lld\n",e.first.c_str(),e.second);
}
