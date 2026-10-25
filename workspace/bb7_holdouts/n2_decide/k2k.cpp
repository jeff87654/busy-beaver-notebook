// k2k MAXSTEPS NK : each stdin line = segment list "p,q;p,q;...;x,y" (K-config: 0^inf S1 11 S2 ... 11 Sk [A]01 0^inf)
// Prints the next NK K-configs (segments) with step counts, or HALT / NOK with a block dump.
#include <bits/stdc++.h>
using namespace std;
int W[7][2],D[7][2],Q[7][2];
string blocks(const vector<char>&tp,long long a,long long b,long long pos,int st){ // a,b aligned
  string o; string prev; int cnt=0; vector<pair<string,int>> runs;
  for(long long i=a;i<b;i+=2){ string bl; bl+=char('0'+tp[i]); bl+=char('0'+tp[i+1]); if(pos==i||pos==i+1){ bl= (pos==i? string("[")+char('A'+st)+"]"+bl : bl.substr(0,1)+"["+char('A'+st)+"]"+bl.substr(1)); }
    if(!runs.empty()&&runs.back().first==bl) runs.back().second++; else runs.push_back({bl,1}); }
  for(auto&r:runs) o+=r.first+(r.second>1?"^"+to_string(r.second):"")+" ";
  return o;
}
int main(int argc,char**argv){
  string M="1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA";
  for(int s=0;s<7;s++)for(int c=0;c<2;c++){string t=M.substr(s*7+3*c,3); if(t[0]=='-'){Q[s][c]=-1;continue;} W[s][c]=t[0]-'0';D[s][c]=t[1]=='R'?1:-1;Q[s][c]=t[2]-'A';}
  long long MX=atoll(argv[1]); int NK=atoi(argv[2]); string line;
  while(getline(cin,line)){
    if(line.empty())continue;
    vector<pair<long long,long long>> segs; { stringstream ss(line); string t; while(getline(ss,t,';')){ auto c=t.find(','); segs.push_back({stoll(t.substr(0,c)),stoll(t.substr(c+1))}); } }
    vector<int> cells; for(size_t i=0;i<segs.size();i++){ for(long long j=0;j<segs[i].first;j++){cells.push_back(0);cells.push_back(1);} for(long long j=0;j<segs[i].second;j++){cells.push_back(1);cells.push_back(0);} if(i+1<segs.size()){cells.push_back(1);cells.push_back(1);} }
    long long off=1<<20; long long N=cells.size(); vector<char> tp(2*off+2*N+100,0);
    for(long long i=0;i<N;i++) tp[off+i]=cells[i]; long long pos=off+N; tp[pos]=0; tp[pos+1]=1; int st=0;
    long long lo=off, hi=pos+1; printf("IN %s\n",line.c_str());
    int found=0; long long s;
    for(s=1;s<=MX;s++){
      int c=tp[pos]; if(Q[st][c]<0){ long long a=min(lo,pos)-4; a-= ((a-off)%2+2)%2; printf("  HALT step %lld pos-off %lld : %s\n",s,pos-off,blocks(tp,a,hi+4,pos,st).c_str()); break; }
      tp[pos]=W[st][c]; pos+=D[st][c]; st=Q[st][c]; lo=min(lo,pos); hi=max(hi,pos);
      if(pos<4||pos>(long long)tp.size()-4){printf("  OUT\n");break;}
      if(st==0 && tp[pos]==0 && tp[pos+1]==1){
        bool blank=true; for(long long j=pos+2;j<=hi+2;j++) if(tp[j]){blank=false;break;}
        if(!blank) continue;
        // parse segments left of pos with alignment of pos
        long long a=pos; while(a>lo-2) a-=2;
        while(a<pos && tp[a]==0&&tp[a+1]==0) a+=2;
        string o; long long p=0,q=0; bool ok=true; vector<string> segsS; int ph=0;
        for(long long i=a;i<pos;i+=2){ int b=tp[i]*2+tp[i+1];
          if(b==1){ if(q){ok=false;} p++; } else if(b==2){ q++; } else if(b==3){ segsS.push_back(to_string(p)+","+to_string(q)); p=q=0; } else ok=false; }
        segsS.push_back(to_string(p)+","+to_string(q));
        string ss; for(size_t i=0;i<segsS.size();i++) ss+=(i?";":"")+segsS[i];
        printf("  K step %lld shift %lld : %s%s\n",s,(pos-off-N),ok?"":"IRREG ",ok?ss.c_str():blocks(tp,a,pos+2,pos,st).c_str());
        if(++found>=NK) break;
      }
    }
    if(s>MX){ long long a=lo-4; a-=((a-off)%2+2)%2; printf("  NOK after %lld : %s\n",MX, blocks(tp,a,hi+4,pos,st).substr(0,600).c_str()); }
    fflush(stdout);
  }
}
