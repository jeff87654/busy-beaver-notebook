// literal TM run from a K-config [ds;b] to the next K-config or halt. usage: lit MACHINE maxsteps, then lines "n d1..dn b"
#include <bits/stdc++.h>
using namespace std;
int W[7][2],Dm[7][2],NS[7][2]; bool H[7][2];
int main(int argc,char**argv){
  string m=argv[1]; long long maxs=atoll(argv[2]); int skip0 = argc>3 ? atoi(argv[3]) : 0;
  for(int q=0;q<7;q++)for(int r=0;r<2;r++){string t=m.substr(q*7+r*3,3); if(t[0]=='-'){H[q][r]=1;continue;} H[q][r]=0;W[q][r]=t[0]-'0';Dm[q][r]=t[1]=='R'?1:-1;NS[q][r]=t[2]-'A';}
  int n;
  while(cin>>n){ vector<long long> ds(n); for(auto&x:ds)cin>>x; long long b; cin>>b;
    long long len=0; for(auto x:ds) len+=x+1; len+=b;
    long long PAD=len+ (maxs<4*len+1000? maxs: 4*len+1000) + 1000; // generous
    // tape size: left pad must cover leftward excursions; use vector with offset, grow if needed
    vector<char> T; long long off = 2000; T.assign(off+len+2000,0);
    long long p=off; for(auto x:ds){ for(long long i=0;i<x;i++) T[p++]=1; T[p++]=0;} for(long long i=0;i<b;i++) T[p++]=1;
    long long pos=p; int st=0; long long steps=0; long long rmost=p-1; // rightmost possible 1 index tracking
    string res="TIMEOUT";
    while(steps<maxs){
      if(pos<0){ long long add=T.size(); T.insert(T.begin(),add,0); pos+=add; rmost+=add; off+=add;}
      if(pos>=(long long)T.size()) T.resize(T.size()*2,0);
      int s=T[pos];
      if(H[st][s]){ res="HALT"; break;}
      T[pos]=W[st][s]; if(W[st][s]&&pos>rmost) rmost=pos;
      pos+=Dm[st][s]; st=NS[st][s]; steps++;
      if(st==0 && pos>rmost){ // check really rightmost: rmost may be stale (cells erased) - recompute lazily
        while(rmost>=0 && T[rmost]==0) rmost--;
        if(pos>rmost && !(skip0 && T[pos-1]==0)){ res="K"; break;}
      }
    }
    long long ones=0; for(char c:T) ones+=c;
    cout<<res<<" "<<steps<<" "<<ones<<" "<<char('A'+st);
    if(res=="K"){ long long lo=0; while(lo<pos && T[lo]==0) lo++; vector<long long> runs; long long c=0; for(long long i=lo;i<pos;i++){ if(T[i]) c++; else {runs.push_back(c); c=0;} } runs.push_back(c);
      cout<<" "<<runs.size()-1; for(auto x:runs) cout<<" "<<x; }
    cout<<"\n"; cout.flush();
  }
}
