// gk6 MACHINE TAIL PFLAG MAXSTEPS < configs : each input line "m1 ... mk | r" (tokens, then r).  Builds word [11] D(m1)..D(mk) (10)^r TAIL, runs B from the right end,
// prints the first later B-at-frontier snapshot that parses as [11] tokens (10)^r' TAIL: "in -> step out_tokens | r'" or HALT/TIMEOUT/EDGE
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; string tail=argv[2]; int pflag=atoi(argv[3]); long long N=atoll(argv[4]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long TL=tail.size();
  string line;
  long long SZ=1LL<<24; vector<uint8_t> tape(SZ);
  while(getline(cin,line)){
    // parse
    vector<long long> in; long long r=0; { stringstream ls(line); string tok; bool bar=false; while(ls>>tok){ if(tok=="|"){bar=true;continue;} if(bar) r=atoll(tok.c_str()); else in.push_back(atoll(tok.c_str())); } }
    fill(tape.begin(),tape.end(),0);
    long long p=SZ/2; string w; if(pflag) w+="11"; for(long long m:in){ for(long long k=0;k<m;k++) w+="10"; w+="1"; } for(long long k=0;k<r;k++) w+="10"; w+=tail;
    for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
    long long mn=p-w.size(),mx=p; int q=1; bool done=false;
    for(long long st=0;st<N&&!done;st++){
      int c=tape[p]; T&t=tm[q][c];
      if(!t.ok){ printf("%s => HALT %lld state %c\n",line.c_str(),st,'A'+q); done=true; break;}
      tape[p]=t.w; if(t.w){ mn=min(mn,p); mx=max(mx,p);} 
      p+=t.d; q=t.n;
      if(p<100||p>SZ-100){printf("%s => EDGE %lld\n",line.c_str(),st); done=true; break;}
      if(q!=1||tape[p]) continue;
      while(mx>=p && !tape[mx]) --mx; 
      if(mx>=p) continue;
      while(mn<p && !tape[mn]) ++mn;
      long long L=p-mn; if(L<TL) continue;
      bool ok=true; for(long long u=0;u<TL;u++) if(tape[p-TL+u]!=tail[u]-'0'){ok=false;break;}
      if(!ok) continue;
      long long e=p-TL; long long i=mn;
      if(pflag){ if(!(e-i>=2&&tape[i]==1&&tape[i+1]==1)) continue; i+=2; }
      vector<long long> toks; long long rr=0; bool good=true;
      while(true){
        long long j=0; while(i+1<e && tape[i]==1&&tape[i+1]==0){ i+=2; j++; }
        if(i==e){ rr=j; break; }
        if(tape[i]==1){ toks.push_back(j); i++; if(i>e){good=false;break;} continue; }
        good=false; break;
      }
      if(!good) continue;
      printf("%s => %lld :",line.c_str(),st+1); for(auto m:toks) printf(" %lld",m); printf(" | %lld\n",rr); done=true;
    }
    if(!done) printf("%s => TIMEOUT\n",line.c_str());
  }
}
