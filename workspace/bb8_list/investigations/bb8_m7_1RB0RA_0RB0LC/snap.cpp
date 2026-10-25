// snap MACHINE WORD HEAD STATE N [fac] [first] : print RLE of tape at B-frontier snapshots (state B at blank right end)
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
static string rle(const vector<uint8_t>&t,long long lo,long long hi){
  string out; long long i=lo;
  while(i<=hi){
    if(i+3<=hi && t[i]!=t[i+1] && t[i+2]==t[i] && t[i+3]==t[i+1]){
      long long j=i; while(j+1<=hi && t[j]==t[i] && t[j+1]==t[i+1]) j+=2;
      if((j-i)/2>=2){ out+="("+to_string(t[i])+to_string(t[i+1])+")^"+to_string((j-i)/2)+" "; i=j; continue;}
    }
    long long j=i; while(j<=hi && t[j]==t[i]) ++j;
    if(j-i>=4) out+=to_string(t[i])+"^"+to_string(j-i)+" ";
    else { for(long long k=i;k<j;++k) out+=char('0'+t[k]); out+=" "; }
    i=j;
  }
  return out;
}
int main(int argc,char**argv){
  string ms=argv[1]; string w=argv[2]; long long head=atoll(argv[3]); int q=argv[4][0]-'A'; long long N=atoll(argv[5]);
  double fac=argc>6?atof(argv[6]):1.5; long long first=argc>7?atoll(argv[7]):20;
  T tm[16][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<28; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+head, mn=off, mx=off+(long long)w.size()-1; double nxt=first; long long cnt=0;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld\n",st,'A'+q,p-off); return 0;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<mn) mn=p; if(p>mx) mx=p;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    if(p<mx) continue; // frontier: head at right end of visited
    ++cnt; if(cnt<first || cnt>=nxt){ if(cnt>=nxt) nxt=nxt*fac+1; else nxt=max(nxt,(double)first);
      long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b;
      printf("%lld B %lld [%lld] %s\n",st+1,p-off,cnt,rle(tape,a,b).c_str()); }
  }
  printf("done N=%lld cnt=%lld\n",N,cnt);
}
