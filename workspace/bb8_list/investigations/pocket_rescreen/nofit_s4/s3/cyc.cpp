// cyc MACHINE Q pre X mid Y suf MAXSTEPS   (stdin lines: "a b"); config Q| pre X^a mid Y^b suf, head on first char of pre.
// Runs until event: state Q, head on blank cell at left extreme, and tape (head..last 1) parses as pre X^a' mid Y^b' suf(trailing 0s stripped).
// Prints "a b -> a' b' events steps" or "a b -> HALT steps" / "TIMEOUT" / "LEFTJUNK". Words: plain 01 strings, use '' via '-' for empty.
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int ns,W[16][2],M[16][2],N_[16][2];
void parse(const string&s){ns=0;size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W[q][b]=-1;i+=3;} else {W[q][b]=s[i]-'0';M[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]-'A';i+=3;}} q++; if(i<s.size()&&s[i]=='_')i++;} ns=q;}
string w(const char*c){string s=c; return s=="-"?"":s;}
int main(int argc,char**argv){SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 parse(argv[1]); int Q=argv[2][0]-'A'; string pre=w(argv[3]),X=w(argv[4]),mid=w(argv[5]),Y=w(argv[6]),suf=w(argv[7]); long long MX=atoll(argv[8]);
 while(!suf.empty()&&suf.back()=='0')suf.pop_back();
 const long long SZ=1LL<<27; vector<unsigned char> t(SZ,0); long long a,b;
 while(cin>>a>>b){ string s=pre; for(long long i=0;i<a;i++)s+=X; s+=mid; for(long long i=0;i<b;i++)s+=Y; s+=suf;
  long long p=SZ/2, mn=p, mx=p+s.size()-1; for(size_t i=0;i<s.size();i++)t[p+i]=s[i]-'0'; int q=Q; long long ev=0; bool done=false;
  for(long long st=0;st<MX;st++){ int c=t[p]; if(W[q][c]<0){printf("%lld %lld -> HALT %lld\n",a,b,st);done=true;break;}
   t[p]=W[q][c]; p+=M[q][c]; q=N_[q][c]; if(p<mn)mn=p; if(p>mx)mx=p;
   if(p<2||p>SZ-3){printf("%lld %lld -> TAPE\n",a,b);done=true;break;}
   if(q==Q&&p==mn&&t[p]==0){ ev++; long long e=mx; while(e>p&&t[e]==0)e--; string r; for(long long x=p;x<=e;x++)r+=char('0'+t[x]);
     if(r.compare(0,pre.size(),pre)!=0)continue; size_t i0=pre.size(); long long amax=0;
     if(!X.empty()){ size_t k=i0; while(r.compare(k,X.size(),X)==0){k+=X.size();amax++;} }
     bool ok=false; long long a2=0,b2=0;
     for(long long aa=amax;aa>=0&&!ok;aa--){ size_t i=i0+aa*X.size(); if(r.compare(i,mid.size(),mid)!=0)continue; i+=mid.size(); long long bb=0;
       if(!Y.empty())while(r.compare(i,Y.size(),Y)==0){i+=Y.size();bb++;}
       if(r.substr(i)==suf){ok=true;a2=aa;b2=bb;} }
     if(!ok)continue;
     printf("%lld %lld -> %lld %lld %lld %lld\n",a,b,a2,b2,ev,st+1);done=true;break;}
  }
  if(!done)printf("%lld %lld -> TIMEOUT\n",a,b);
  fflush(stdout); for(long long x=mn;x<=mx;x++)t[x]=0; }
}
