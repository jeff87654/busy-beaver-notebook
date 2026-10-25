// run: reads lines "LEFT | HEADBLOCKS..." : tokens like 01^3 10 11 ; the head (state A) is on the first cell of the token after '|'
// usage: run MAXSTEPS < cases ; prints per line: HALT steps / RUN
#include <bits/stdc++.h>
using namespace std;
int W[7][2],D[7][2],Q[7][2];
int main(int argc,char**argv){
  string M="1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA";
  for(int s=0;s<7;s++)for(int c=0;c<2;c++){string t=M.substr(s*7+3*c,3); if(t[0]=='-'){Q[s][c]=-1;continue;} W[s][c]=t[0]-'0';D[s][c]=t[1]=='R'?1:-1;Q[s][c]=t[2]-'A';}
  long long MX=atoll(argv[1]); string line;
  while(getline(cin,line)){
    if(line.empty())continue;
    stringstream ss(line); string tok; vector<int> cells; long long head=-1; int st=0;
    while(ss>>tok){ if(tok=="|"){head=cells.size();continue;} if(tok.size()==1&&isalpha(tok[0])){st=tok[0]-'A';continue;}
      string b=tok; int c=1; auto p=tok.find('^'); if(p!=string::npos){b=tok.substr(0,p);c=stoi(tok.substr(p+1));}
      for(int i=0;i<c;i++) for(char ch:b) cells.push_back(ch-'0'); }
    long long N=cells.size(); long long off=1<<22; vector<char> tp(2*off+N+10,0);
    for(long long i=0;i<N;i++) tp[off+i]=cells[i];
    long long pos=off+head; long long s; bool h=false; long long lo=pos,hi=pos;
    for(s=0;s<MX;s++){ int c=tp[pos]; if(Q[st][c]<0){h=true;break;} tp[pos]=W[st][c]; pos+=D[st][c]; st=Q[st][c]; if(pos<=1||pos>=(long long)tp.size()-2){break;} }
    if(h) printf("HALT %lld | %s\n",s,line.c_str()); else printf("RUN %lld | %s\n",s,line.c_str());
    fflush(stdout);
  }
}
