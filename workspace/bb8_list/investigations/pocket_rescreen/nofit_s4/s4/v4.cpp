// v4 MACHINE Q SIDE MAXSTEPS ; stdin lines: "S0 LEFT RIGHT REGEX" (LEFT/RIGHT 01 strings or '-', head on RIGHT[0])
// runs until event: state Q, head on blank cell at visited extreme SIDE, and tape word W matches REGEX, where
// W = (first 1 .. head) for SIDE R, (head .. last 1) for SIDE L. Prints "M steps events W" / "H steps ones" / "T events".
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int ns,W_[16][2],M_[16][2],N_[16][2];
void parse(const string&s){ns=0;size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W_[q][b]=-1;i+=3;} else {W_[q][b]=s[i]-'0';M_[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]-'A';i+=3;}} q++; if(i<s.size()&&s[i]=='_')i++;} ns=q;}
int main(int argc,char**argv){SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 parse(argv[1]); int Q=argv[2][0]-'A'; char side=argv[3][0]; long long MX=atoll(argv[4]);
 const long long SZ=1LL<<26; vector<unsigned char> t(SZ,0);
 string s0,L,R,rx;
 while(cin>>s0>>L>>R>>rx){ if(L=="-")L=""; if(R=="-")R=""; regex re((rx=="ALL"||rx.rfind("C1:",0)==0)?string("x"):rx);
  fill(t.begin(),t.end(),0); long long p=SZ/2; for(size_t i=0;i<L.size();i++)t[p-L.size()+i]=L[i]-'0'; for(size_t i=0;i<R.size();i++)t[p+i]=R[i]-'0';
  long long mn=p-(long long)L.size(), mx=max(p,p+(long long)R.size()-1); int q=s0[0]-'A'; long long ev=0; bool done=false;
  for(long long st=0;st<MX;st++){ int c=t[p]; if(W_[q][c]<0){ long long o=0; for(long long x=mn;x<=mx;x++)o+=t[x]; printf("H %lld %lld\n",st,o); done=true; break;}
   t[p]=W_[q][c]; p+=M_[q][c]; q=N_[q][c]; if(p<mn)mn=p; if(p>mx)mx=p; if(p<2||p>SZ-3){printf("TAPE\n");done=true;break;}
   if(q==Q&&t[p]==0&&((side=='R'&&p==mx)||(side=='L'&&p==mn))){ ev++; string w;
     if(side=='R'){ long long a=mn; while(a<p&&t[a]==0)a++; for(long long x=a;x<=p;x++)w+=char('0'+t[x]); }
     else { long long b=mx; while(b>p&&t[b]==0)b--; for(long long x=p;x<=b;x++)w+=char('0'+t[x]); }
     if(rx=="ALL"){ printf("E %lld %s\n",st+1,w.c_str()); if(ev>=2000000){done=true;break;} continue; }
     bool hit=false; if(rx.rfind("C1:",0)==0){ long long k=atoll(rx.c_str()+3); string pre="0"+string(k,'1')+"0"; hit=w.compare(0,pre.size(),pre)==0; } else hit=regex_match(w,re);
     if(hit){ printf("M %lld %lld %s\n",st+1,ev,w.c_str()); done=true; break; } } }
  if(!done) printf("T %lld\n",ev); fflush(stdout); } }
