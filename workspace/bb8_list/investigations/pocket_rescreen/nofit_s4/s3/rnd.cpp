// rnd MACHINE Q side PREFIX c MAXSTEPS MAXROUNDS [stdin: initial tape words (state Q, head at first char) or empty for blank]
// at each event (state Q, head on blank extreme cell on side), read tape from head (side L: rightwards; R: leftwards mirrored) ;
// if it starts with PREFIX followed by a run of char c of length n, print "steps n W" where W=rest (trailing 0s stripped), compressed
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int W_[16][2],M_[16][2],N_[16][2];
void parse(const string&s){size_t i=0;int q=0; while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W_[q][b]=-1;i+=3;} else {W_[q][b]=s[i]-'0';M_[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]-'A';i+=3;}} q++; if(i<s.size()&&s[i]=='_')i++;}}
string comp(const string& t){ string o; size_t i=0,n=t.size();
 while(i<n){ int bp=0,bk=0; size_t bc=0;
  for(int p=1;p<=12&&i+p<=n;p++){ size_t k=1; while(i+(k+1)*p<=n && t.compare(i+k*p,p,t,i,p)==0)k++; if(k>=3 && k*p>bc){bc=k*p;bp=p;bk=k;} }
  if(bk>=3 && bc>=6){ o+=" ("+t.substr(i,bp)+")^"+to_string(bk)+" "; i+=bc; } else { o+=t[i]; i++; } }
 return o;}
int main(int argc,char**argv){SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 parse(argv[1]); int Q=argv[2][0]-'A'; char side=argv[3][0]; string P=argv[4]; if(P=="-")P=""; char c=argv[5][0]; long long MX=atoll(argv[6]); long long MR=atoll(argv[7]);
 string init; { string s; while(cin>>s) init+=s; }
 const long long SZ=1LL<<28; vector<unsigned char> t(SZ,0); long long p=SZ/2,mn=p,mx=p; int q=0;
 if(!init.empty()){ for(size_t i=0;i<init.size();i++) t[p+(side=='L'?(long long)i:-(long long)i)]=init[i]-'0'; q=Q; if(side=='L')mx=p+init.size()-1; else mn=p-init.size()+1; }
 long long rounds=0;
 for(long long st=0;st<MX;st++){ int b=t[p]; if(W_[q][b]<0){ long long ones=0; for(long long x=mn;x<=mx;x++)ones+=t[x]; printf("HALT %lld ones %lld\n",st,ones); return 0;}
  t[p]=W_[q][b]; p+=M_[q][b]; q=N_[q][b]; if(p<mn)mn=p; if(p>mx)mx=p; if(p<2||p>SZ-3){puts("TAPE");return 0;}
  if(q==Q && t[p]==0 && ((side=='L'&&p==mn)||(side=='R'&&p==mx))){
    string r; if(side=='L'){ long long e=mx; while(e>p&&t[e]==0)e--; for(long long x=p;x<=e;x++)r+=char('0'+t[x]); }
    else { long long e=mn; while(e<p&&t[e]==0)e++; for(long long x=p;x>=e;x--)r+=char('0'+t[x]); }
    if(r.compare(0,P.size(),P)!=0) continue; size_t i=P.size(), j=i; while(j<r.size()&&r[j]==c)j++;
    printf("%lld %zu %s\n",st+1,j-i,comp(r.substr(j)).c_str()); fflush(stdout); if(++rounds>=MR) return 0; }
 }
 printf("END %lld\n",MX);}
