// dtr: direct TM tracer with D-token view.  dtr MACHINE MAXSTEPS [--ev Q0,E1,..] [--every N] [--maxout N] [--start W:H:Q]
// token view: maximal (10)^m 1 -> "m", runs of zeros of length k>=2 between tokens -> "z<k>", head shown as {Qs} inside.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
static std::vector<unsigned char> t; static ll lo,hi,p; static int s;
static std::string view(){
  // greedy periodic compression of the tape (lo..hi trimmed of blanks); head marked as {Q} before its cell
  ll a=lo,b=hi; while(a<p&&!t[a])a++; while(b>p&&!t[b])b--;
  std::string out; ll i=a;
  while(i<=b){
    if(i==p){ char buf[8]; snprintf(buf,8," {%c}",'A'+s); out+=buf; }
    ll best=1,bestc=1,bestlen=1;
    for(ll L=1;L<=12;L++){ ll c=1; while(true){ ll j=i+c*L; if(j+L-1>b) break; bool ok=true; for(ll k=0;k<L;k++){ if(t[j+k]!=t[i+k]) {ok=false;break;} } if(!ok)break;
        // do not swallow the head cell
        if(p>i && p<j+L) break; c++; }
      if(p>i && p<i+L && L>1) continue;
      if(c>=2 && c*L>bestlen+ (L>best?L:0)){best=L;bestc=c;bestlen=c*L;} }
    if(bestc>=2 && bestlen>=4){ std::string pat; for(ll k=0;k<best;k++) pat+=char('0'+t[i+k]); char buf[48]; snprintf(buf,48," (%s)^%lld",pat.c_str(),bestc); out+=buf; i+=bestlen; }
    else { if(out.empty()||out.back()==' '||out.back()==')'||(out.size()>0&&out[out.size()-1]>='0'&&out[out.size()-1]<='9'&&false)) ; out+=' '; out+=char('0'+t[i]); i++; }
  }
  return out;
}
int main(int argc,char**argv){
  std::string m=argv[1]; ll maxs=(ll)atof(argv[2]); ll every=0, maxout=1000; unsigned evmask=0; std::string start;
  for(int i=3;i<argc;i++){ std::string a=argv[i];
    if(a=="--ev"){ std::string e=argv[++i]; for(size_t k=0;k+1<e.size();k+=3) evmask|=1u<<((e[k]-'A')*2+(e[k+1]-'0'));}
    else if(a=="--every") every=(ll)atof(argv[++i]); else if(a=="--maxout") maxout=atoll(argv[++i]); else if(a=="--start") start=argv[++i];}
  int n=(m.size()+1)/7; int W[64],D[64],N[64];
  for(int q=0;q<n;q++)for(int c=0;c<2;c++){const char*x=m.c_str()+q*7+c*3; int i=q*2+c;
    if(x[0]=='-'||x[2]-'A'>=n||x[2]<'A'){W[i]=-1;continue;} W[i]=x[0]-'0';D[i]=x[1]=='R'?1:-1;N[i]=x[2]-'A';}
  ll L=1LL<<27; t.assign(L,0); p=L/2; s=0;
  if(!start.empty()){ size_t a=start.find(':'),b=start.rfind(':'); std::string w=start.substr(0,a); ll h=atoll(start.substr(a+1,b-a-1).c_str());
    for(size_t k=0;k<w.size();k++) t[L/2+k]=w[k]-'0'; p=L/2+h; s=start[b+1]-'A'; lo=L/2; hi=L/2+w.size(); if(p<lo)lo=p; if(p>hi)hi=p;} else {lo=hi=p;}
  ll st=0, outn=0;
  while(st<maxs){
    int i=s*2+t[p];
    if((evmask>>i&1) || (every && st%every==0)){ printf("@%lld %s\n",st,view().c_str()); if(++outn>=maxout) {printf("MAXOUT\n");return 0;} }
    if(W[i]<0){ ll ones=0; for(ll k=lo;k<=hi;k++)ones+=t[k]; printf("HALT %c%d steps %lld ones %lld\n%s\n",'A'+s,t[p],st,ones,view().c_str()); return 0;}
    t[p]=W[i]; p+=D[i]; s=N[i]; st++;
    if(p<lo){lo=p; if(p<=1){printf("TAPE\n");return 1;}} if(p>hi){hi=p; if(p>=L-2){printf("TAPE\n");return 1;}}
  }
  printf("RUN %lld\n%s\n",st,view().c_str()); return 0;}
