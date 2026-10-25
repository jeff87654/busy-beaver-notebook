// tv: literal simulator with compressed tape views.
// tv MACHINE MAXSTEPS SIDE FROM EVERY MAXPRINT
//   prints config each time head reaches a new extreme on SIDE (L/R), for record index >= FROM, every EVERY-th,
//   at most MAXPRINT lines. Format: "rec step span | compressed tape with head [Q]"
// tv MACHINE MAXSTEPS S
//   summary only.
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>
#include <cctype>
#include <windows.h>
struct TM { int nx[8][2], w[8][2], d[8][2]; int n; };
static bool parse(const char *s, TM &m){ int q=0,len=strlen(s); for(int i=0;i<len;i+=7){ for(int c=0;c<2;++c){const char*x=s+i+3*c; if(x[0]=='-'){m.nx[q][c]=-1;m.w[q][c]=1;m.d[q][c]=1;} else {m.w[q][c]=x[0]-'0';m.d[q][c]=x[1]=='R'?1:-1;m.nx[q][c]=x[2]-'A';}} ++q;} m.n=q; return true;}
static std::string seg(const std::vector<unsigned char>&T,long long i,long long hi){
  std::string o;
  while(i<=hi){ int bp=0; long long br=0;
    for(int p=1;p<=12;++p){ long long r=1; while(i+(r+1)*p-1<=hi){ bool ok=true; for(int k=0;k<p;++k) if(T[i+r*p+k]!=T[i+k]){ok=false;break;} if(!ok)break; ++r;}
      if(r>=3 && r*p>br*bp){bp=p;br=r;} }
    if(bp){ o+="("; for(int k=0;k<bp;++k) o+=char('0'+T[i+k]); o+=")^"+std::to_string(br)+" "; i+=br*bp; }
    else { o+=char('0'+T[i]); o+=" "; ++i; } }
  return o;
}
static std::string comp(const std::vector<unsigned char>&T,long long lo,long long hi,long long hp,int q){
  long long a=lo<hp?lo:hp, b=hi>hp?hi:hp;
  return seg(T,a,hp-1)+"["+char('A'+q)+"]"+char('0'+T[hp])+" "+seg(T,hp+1,b);
}
int main(int argc,char**argv){
  SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS); TM m; parse(argv[1],m); long long maxs=atoll(argv[2]); char side=argv[3][0]; int fst = argv[3][1]==':' ? argv[3][2]-'A' : -1;
  long long from= argc>4?atoll(argv[4]):0, every=argc>5?atoll(argv[5]):1, maxp=argc>6?atoll(argv[6]):50;
  const long long SZ=1LL<<25; std::vector<unsigned char>T(SZ,0); long long p=SZ/2,mn=p,mx=p; int q=0; long long rec=0,printed=0;
  if(argc>9){ q=argv[7][0]-'A'; long long hi=atoll(argv[8]); std::string spec=argv[9]; long long pos=p; size_t i=0;
    while(i<spec.size()){ while(i<spec.size()&&spec[i]==' ')++i; if(i>=spec.size())break; std::string w; while(i<spec.size()&&(spec[i]=='0'||spec[i]=='1')) w+=spec[i++]; long long n=1; if(i<spec.size()&&spec[i]=='^'){++i; n=0; while(i<spec.size()&&isdigit(spec[i])) n=n*10+(spec[i++]-'0');} for(long long r=0;r<n;++r) for(char c:w) T[pos++]=c-'0'; }
    mn=p; mx=pos-1; p=p+hi; }
  for(long long st=0;st<maxs;++st){
    int s=T[p]; int nq=m.nx[q][s];
    if(nq<0){ long long ones=0; for(long long i=mn;i<=mx;++i) ones+=T[i]; printf("HALT step %lld ones %lld\n",st,ones); return 0;}
    T[p]=m.w[q][s]; p+=m.d[q][s]; q=nq;
    if(p<4||p>=SZ-4){printf("TAPE %lld\n",st);return 0;}
    bool ev=false; static long long hist[2][8];
    if(p<mn){mn=p; hist[0][q]++; if(side=='L') ev=true;} if(p>mx){mx=p; hist[1][q]++; if(side=='R') ev=true;}
    if(ev && fst>=0 && q!=fst) ev=false;
    if(ev){ ++rec; if(rec>=from && (rec-from)%every==0 && printed<maxp && side!='S'){ ++printed; printf("%lld %lld %lld | %s\n",rec,st+1,mx-mn+1,comp(T,mn,mx,p,q).c_str()); if(printed>=maxp){printf("STOP %lld\n",st+1);return 0;} } }
  }
  printf("END %lld span %lld recL/R %lld\n",maxs,mx-mn+1,rec);
}
