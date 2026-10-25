// sim MACHINE MAXSTEPS MODE [args]   (idle priority)
// rec N        : print config whenever head reaches a new extreme cell, N prints max
// at Q S N     : print when in state Q with head on blank extreme cell on side S (L/R)
// span         : print span at decades
// probe Q S N  : stdin lines "X left words|right words" (head on first char of right), run until event (Q,S) as in 'at'
//                prints "S steps config" or "H steps" or "T"
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int ns; int W[16][2], M[16][2], N_[16][2];
void parse(const string&s){ns=0;size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W[q][b]=-1;M[q][b]=0;N_[q][b]=-1;i+=3;} else {W[q][b]=s[i]-'0';M[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]=='Z'?-1:s[i+2]-'A';i+=3;}}
 q++; if(i<s.size()&&s[i]=='_')i++;} ns=q;}
string comp(const string& t){ string o; size_t i=0,n=t.size();
 while(i<n){ int bp=0,bk=0; size_t bc=0;
  for(int p=1;p<=12&&i+p<=n;p++){ size_t k=1; while(i+(k+1)*p<=n && t.compare(i+k*p,p,t,i,p)==0)k++; if(k>=3 && k*p>bc){bc=k*p;bp=p;bk=k;} }
  if(bk>=3 && bc>=6){ string blk=t.substr(i,bp); o+=(bp==1?blk:"("+blk+")")+"^"+to_string(bk)+" "; i+=bc; }
  else { o+=t[i]; i++; if(i<n){ /* space before a run token */ } }
 } return o;}
string expand(const string& w){ string o; stringstream ss(w); string tk; while(ss>>tk){ size_t c=tk.find('^'); if(c==string::npos){o+=tk;continue;}
  string b=tk.substr(0,c); long long k=atoll(tk.c_str()+c+1); if(b[0]=='(') b=b.substr(1,b.size()-2); for(long long i=0;i<k;i++)o+=b;} return o;}
const long long SZ=1LL<<27; vector<unsigned char> tp; long long p,mn,mx; int q;
void dump(long long st){ string a,b; for(long long x=mn;x<p;x++)a+=char('0'+tp[x]); for(long long x=p;x<=mx;x++)b+=char('0'+tp[x]);
 printf("%lld %c | %s <%c> %s\n",st,'A'+q,comp(a).c_str(),'A'+q,comp(b).c_str());}
int main(int argc,char**argv){ SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 parse(argv[1]); long long maxs=atoll(argv[2]); string mode=argv[3];
 tp.assign(SZ,0); p=SZ/2;mn=p;mx=p;q=0;
 long long lim=1000000; int Qf=-1; char side='?';
 if(mode=="rec") lim=atoll(argv[4]);
 if(mode=="at"||mode=="probe"){Qf=argv[4][0]-'A'; side=argv[5][0]; lim=atoll(argv[6]);}
 if(mode=="probe"){ string line;
  while(getline(cin,line)){ if(line.size()<2)continue; int q0=line[0]-'A'; size_t bar=line.find('|'); string L=expand(line.substr(1,bar-1)), R=expand(line.substr(bar+1));
   p=SZ/2; for(size_t i=0;i<L.size();i++)tp[p-L.size()+i]=L[i]-'0'; for(size_t i=0;i<R.size();i++)tp[p+i]=R[i]-'0';
   mn=p-(long long)L.size(); mx=p+(long long)R.size()-1; if(mx<p)mx=p; q=q0; bool done=false;
   for(long long st=0;st<lim;st++){ int s2=tp[p]; if(W[q][s2]<0){printf("H %lld\n",st);done=true;break;}
     tp[p]=W[q][s2]; int nq=N_[q][s2]; p+=M[q][s2]; q=nq; if(p<mn)mn=p; if(p>mx)mx=p;
     if(q==Qf && tp[p]==0 && ((side=='L'&&p==mn)||(side=='R'&&p==mx))){ printf("S "); dump(st+1); done=true; break;} }
   if(!done) puts("T");
   fflush(stdout); for(long long x=mn;x<=mx;x++)tp[x]=0; }
  return 0; }
 long long cnt=0, nextcp=1000;
 for(long long st=0;st<maxs;st++){
  int s=tp[p]; if(W[q][s]<0){ long long ones=0; for(long long x=mn;x<=mx;x++)ones+=tp[x]; printf("HALT %lld ones %lld span %lld\n",st,ones,mx-mn+1); return 0;}
  tp[p]=W[q][s]; int nq=N_[q][s]; p+=M[q][s]; q=nq;
  bool nw=false; if(p<mn){mn=p;nw=true;} if(p>mx){mx=p;nw=true;}
  if(p<2||p>SZ-3){printf("TAPE %lld\n",st);return 0;}
  if(mode=="rec" && nw){ dump(st+1); if(++cnt>=lim) return 0; }
  else if(mode=="at" && q==Qf && tp[p]==0 && ((side=='L'&&p==mn)||(side=='R'&&p==mx))){ dump(st+1); if(++cnt>=lim) return 0;}
  else if(mode=="span" && st+1==nextcp){ printf("%lld span %lld\n",st+1,mx-mn+1); nextcp*=10;}
 }
 printf("END %lld span %lld\n",maxs,mx-mn+1); }
