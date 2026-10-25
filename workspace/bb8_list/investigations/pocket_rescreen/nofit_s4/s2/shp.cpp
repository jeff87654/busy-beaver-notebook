// shp MACHINE MAXSTEPS Q SIDE MAXPRINT START_STATE "LEFT|RIGHT"  (words expanded tokens like (01)^5 allowed; '-' for blank start)
// prints event configs (state Q at extreme SIDE on blank) only when the shape (compressed form with exponents -> #) changes.
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int ns,W[16][2],M[16][2],N_[16][2];
void parse(const string&s){ns=0;size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W[q][b]=-1;i+=3;} else {W[q][b]=s[i]-'0';M[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]-'A';i+=3;}} q++; if(i<s.size()&&s[i]=='_')i++;} ns=q;}
string comp(const string& t){ string o; size_t i=0,n=t.size();
 while(i<n){ int bp=0,bk=0; size_t bc=0;
  for(int p=1;p<=6&&i+p<=n;p++){ size_t k=1; while(i+(k+1)*p<=n && t.compare(i+k*p,p,t,i,p)==0)k++; if(k>=3 && k*p>bc){bc=k*p;bp=p;bk=k;} }
  if(bk>=3 && bc>=6){ string blk=t.substr(i,bp); o+=(bp==1?blk:"("+blk+")")+"^"+to_string(bk)+" "; i+=bc; }
  else { o+=t[i]; i++; } } return o;}
string expand(const string& w){ string o; size_t i=0; while(i<w.size()){ if(w[i]=='('){size_t j=w.find(')',i); string b=w.substr(i+1,j-i-1); size_t k=j+2; long long n=0; while(k<w.size()&&isdigit(w[k]))n=n*10+(w[k++]-'0'); for(long long r=0;r<n;r++)o+=b; i=k;}
  else if((w[i]=='0'||w[i]=='1')&&i+1<w.size()&&w[i+1]=='^'){ size_t k=i+2; long long n=0; while(k<w.size()&&isdigit(w[k]))n=n*10+(w[k++]-'0'); o+=string(n,w[i]); i=k;}
  else { if(w[i]=='0'||w[i]=='1')o+=w[i]; i++; } } return o;}
string shape(const string&c){ string s; for(size_t i=0;i<c.size();i++){ if(c[i]=='^'){ s+="^#"; while(i+1<c.size()&&isdigit(c[i+1]))i++; } else s+=c[i]; } return s;}
int main(int argc,char**argv){ SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 parse(argv[1]); long long maxs=atoll(argv[2]); int Qf=argv[3][0]-'A'; char side=argv[4][0]; long long lim=atoll(argv[5]); int q=argv[6][0]-'A'; string cfg=argv[7];
 size_t bar=cfg.find('|'); string L=expand(cfg.substr(0,bar)), R=expand(cfg.substr(bar+1));
 const long long SZ=1LL<<28; vector<unsigned char> tp(SZ,0); long long p=SZ/2; for(size_t i=0;i<L.size();i++)tp[p-L.size()+i]=L[i]-'0'; for(size_t i=0;i<R.size();i++)tp[p+i]=R[i]-'0';
 long long mn=p-(long long)L.size(), mx=max(p,p+(long long)R.size()-1); string last; long long cnt=0, ev=0;
 for(long long st=0;st<maxs;st++){ int s=tp[p]; if(W[q][s]<0){ long long ones=0; for(long long x=mn;x<=mx;x++)ones+=tp[x]; printf("HALT %lld ones %lld ev %lld\n",st,ones,ev); return 0;}
  tp[p]=W[q][s]; int nq=N_[q][s]; p+=M[q][s]; q=nq; if(p<mn)mn=p; if(p>mx)mx=p; if(p<2||p>SZ-3){printf("TAPE %lld\n",st);return 0;}
  if(q==Qf && tp[p]==0 && ((side=='L'&&p==mn)||(side=='R'&&p==mx))){ ev++;
    long long a=mn; while(a<mx&&tp[a]==0)a++; long long b=mx; while(b>a&&tp[b]==0)b--; string t; for(long long x=a;x<=b;x++)t+=char('0'+tp[x]);
    string c=comp(t); string sh=shape(c); if(sh!=last){ printf("%lld ev%lld %s\n",st+1,ev,c.size()>300?(c.substr(0,300)+"...").c_str():c.c_str()); last=sh; if(++cnt>=lim)return 0; } } }
 printf("END %lld ev %lld\n",maxs,ev); }
