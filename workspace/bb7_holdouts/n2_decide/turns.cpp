// turns SEGS MAXSTEPS [align 0/1] : run from K-config, print run-length block view at every head turn
#include <bits/stdc++.h>
using namespace std;
int W[7][2],D[7][2],Q[7][2];
int main(int argc,char**argv){
  string M="1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA";
  for(int s=0;s<7;s++)for(int c=0;c<2;c++){string t=M.substr(s*7+3*c,3); if(t[0]=='-'){Q[s][c]=-1;continue;} W[s][c]=t[0]-'0';D[s][c]=t[1]=='R'?1:-1;Q[s][c]=t[2]-'A';}
  string line=argv[1]; long long MX=atoll(argv[2]); int al=argc>3?atoi(argv[3]):0;
  vector<pair<long long,long long>> segs; { stringstream ss(line); string t; while(getline(ss,t,';')){ auto c=t.find(','); segs.push_back({stoll(t.substr(0,c)),stoll(t.substr(c+1))}); } }
  vector<int> cells; for(size_t i=0;i<segs.size();i++){ for(long long j=0;j<segs[i].first;j++){cells.push_back(0);cells.push_back(1);} for(long long j=0;j<segs[i].second;j++){cells.push_back(1);cells.push_back(0);} if(i+1<segs.size()){cells.push_back(1);cells.push_back(1);} }
  long long off=1<<16; long long N=cells.size(); vector<char> tp(2*off+2*N+100,0);
  for(long long i=0;i<N;i++) tp[off+i]=cells[i]; long long pos=off+N; tp[pos]=0; tp[pos+1]=1; int st=0; long long lo=off,hi=pos+1;
  int pd=0;
  for(long long s=0;s<MX;s++){
    int c=tp[pos]; if(Q[st][c]<0){printf("HALT %lld\n",s);return 0;}
    int d=D[st][c];
    if(d!=pd){
      long long a=lo-4; a-= ((a-al)%2+2)%2; string o; vector<pair<string,int>> runs;
      for(long long i=a;i<hi+4;i+=2){ string bl; bl+=char('0'+tp[i]); bl+=char('0'+tp[i+1]); if(pos==i) bl="["+string(1,'A'+st)+"]"+bl; else if(pos==i+1) bl=bl.substr(0,1)+"["+string(1,'A'+st)+"]"+bl.substr(1);
        if(!runs.empty()&&runs.back().first==bl&&bl.size()==2) runs.back().second++; else runs.push_back({bl,1}); }
      for(auto&r:runs) o+=r.first+(r.second>1?"^"+to_string(r.second):"")+" ";
      printf("%7lld %s\n",s,o.c_str());
    }
    pd=d; tp[pos]=W[st][c]; pos+=d; st=Q[st][c]; lo=min(lo,pos); hi=max(hi,pos);
  }
}
