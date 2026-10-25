// snap MACHINE STEPS K : after each checkpoint STEPS*j/K (j=1..K) print the next record-extreme config compressed (state, side)
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int ns,W_[16][2],M_[16][2],N_[16][2];
void parse(const string&s){ns=0;size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W_[q][b]=-1;i+=3;} else {W_[q][b]=s[i]-'0';M_[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]-'A';i+=3;}} q++; if(i<s.size()&&s[i]=='_')i++;} ns=q;}
string comp(const string& t){ string o; size_t i=0,n=t.size();
 while(i<n){ int bp=0,bk=0; size_t bc=0;
  for(int p=1;p<=16&&i+p<=n;p++){ size_t k=1; while(i+(k+1)*p<=n && t.compare(i+k*p,p,t,i,p)==0)k++; if(k>=3 && k*p>bc){bc=k*p;bp=p;bk=k;} }
  if(bk>=3 && bc>=6){ string blk=t.substr(i,bp); o+=(bp==1?blk:"("+blk+")")+"^"+to_string(bk)+" "; i+=bc; }
  else { o+=t[i]; i++; } } return o;}
int main(int argc,char**argv){SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 parse(argv[1]); long long S=atoll(argv[2]); int K=atoi(argv[3]); int maxc=argc>4?atoi(argv[4]):160;
 const long long SZ=1LL<<27; vector<unsigned char> t(SZ,0); long long p=SZ/2,mn=p,mx=p; int q=0; int j=1;
 for(long long st=0;;st++){ int c=t[p]; if(W_[q][c]<0){ long long o=0; for(long long x=mn;x<=mx;x++)o+=t[x]; printf("HALT %lld ones %lld\n",st,o); return 0;}
  t[p]=W_[q][c]; p+=M_[q][c]; q=N_[q][c]; bool rec=false; if(p<mn){mn=p;rec=true;} if(p>mx){mx=p;rec=true;}
  if(p<2||p>SZ-3){printf("TAPE\n");return 0;}
  if(rec && st+1>=S*j/K){ long long a=mn; while(a<mx&&t[a]==0)a++; long long b=mx; while(b>a&&t[b]==0)b--; if(p<a)a=p; if(p>b)b=p;
   string L,R; for(long long x=a;x<p;x++)L+=char('0'+t[x]); for(long long x=p;x<=b;x++)R+=char('0'+t[x]);
   string s=comp(L)+"<"+string(1,'A'+q)+"> "+comp(R); if((int)s.size()>maxc) s=s.substr(0,maxc/2)+" ... "+s.substr(s.size()-maxc/2);
   printf("%lld %c span=%lld | %s\n",st+1,p==mn?'L':'R',mx-mn+1,s.c_str()); if(++j>K) return 0; } } }
