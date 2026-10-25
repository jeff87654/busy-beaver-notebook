// left MACHINE WORD STATE N first last : print tape when head steps left of the leftmost nonblank cell (new left-edge visits), numbered first..last
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]); int first=atoi(argv[5]), last=atoi(argv[6]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<28; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2];
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p-w.size(),mx=p; int cnt=0;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld\n", st, 'A'+q, p-SZ/2); 
       for(long long i=mn;i<=mx;i++) putchar('0'+tape[i]); putchar('\n'); return 0;}
    tape[p]=t.w; if(t.w){ mn=min(mn,p); mx=max(mx,p);} 
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(p<mn){ // head left of all ones
      cnt++; if(cnt>=first&&cnt<=last){ printf("%lld %c ", st+1,'A'+q); for(long long i=mn;i<=mx;i++) { if(i==p) putchar('['); putchar('0'+tape[i]);} putchar('\n'); }
      mn=p; if(cnt>last) break;
    }
  }
  printf("done leftvisits=%d\n",cnt);
}
