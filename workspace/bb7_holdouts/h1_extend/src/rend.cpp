// rend MACHINE MAXSTEPS [W] : literal simulation from blank; log every step where the head is at or beyond the
// rightmost/leftmost nonblank cell (tape end events): step, side, state, read, last W cells near that end.
// Aggregates distinct (side,state,window) contexts with first step and count.
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string m=argv[1]; long long MX=atoll(argv[2]); int W=argc>3?atoi(argv[3]):8;
  int w[16][2],d[16][2],nx[16][2],S=0; {stringstream ss(m);string r;while(getline(ss,r,'_')){for(int c=0;c<2;c++){string t=r.substr(3*c,3);if(t[0]=='-'){w[S][c]=0;d[S][c]=0;nx[S][c]=-1;}else{w[S][c]=t[0]-'0';d[S][c]=t[1]=='R'?1:-1;nx[S][c]=t[2]-'A';}}S++;}}
  const long long N=1<<26; vector<unsigned char> T(N,0); long long p=N/2, lo=p, hi=p; int q=0;
  map<string,pair<long long,long long>> ctx;
  for(long long s=0;s<MX;s++){
    if(p<=lo || p>=hi){ string k; if(p>=hi){k="R";k+=char('A'+q);k+=' ';for(int i=W-1;i>=0;i--)k+=char('0'+T[p-i]);k+='|';}
                                 else {k="L";k+=char('A'+q);k+=' ';k+='|';for(int i=0;i<W;i++)k+=char('0'+T[p+i]);}
      auto it=ctx.find(k); if(it==ctx.end()) ctx[k]={s,1}; else it->second.second++; }
    int c=T[p]; if(nx[q][c]<0){printf("HALT at step %lld state %c read %d\n",s,'A'+q,c);break;}
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c];
    if(T[p-d[q>=0?0:0][0]*0]){} 
    if(p<lo)lo=p; if(p>hi)hi=p;
    if(p<2||p>N-3){printf("tape overflow at %lld\n",s);break;}
  }
  for(auto&e:ctx) printf("%s  first=%lld count=%lld\n",e.first.c_str(),e.second.first,e.second.second);
}
