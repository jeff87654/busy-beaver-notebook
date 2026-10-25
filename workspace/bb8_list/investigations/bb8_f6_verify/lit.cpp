// lit: literal TM sim with snapshot events.
// lit MACHINE STATE LEFT RIGHT MAXSTEPS MODE [STRIDE]
//   head on RIGHT[0]. LEFT/RIGHT are 0/1 strings with optional run syntax "1^5" not supported: use expand in caller.
// MODE: e = print at every E0 with next "100" (E-moment), h = print at every H entry, x = both, n = none
// prints: step state headpos | RLE of tape from leftmost-1 to rightmost-1 with head marked [q]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
typedef long long ll;
int W[16][2], Dm[16][2], Nx[16][2]; int ns;
unsigned char *tape; ll SZ;
#include <vector>
std::string rle(ll lo, ll hi, ll h, int q){
  std::vector<std::string> tk; ll i=lo; char b[64];
  while(i<=hi){ if(i==h){ sprintf(b,"[%c%d]",'A'+q,tape[i]); tk.push_back(b); ++i; continue;}
    ll j=i; while(j<=hi && tape[j]==tape[i] && j!=h) ++j;
    if(j-i>1) sprintf(b,"%d^%lld",tape[i],j-i); else sprintf(b,"%d",tape[i]); tk.push_back(b); i=j; }
  std::string o; size_t k=0;
  while(k<tk.size()){
    bool done=false;
    for(size_t p=1;p<=4 && !done;++p){ size_t r=1; while(k+(r+1)*p<=tk.size()){ bool eq=true; for(size_t t=0;t<p;++t) if(tk[k+t]!=tk[k+r*p+t]||tk[k+t][0]=='['){eq=false;break;} if(!eq)break; ++r;}
      if(r>=3){ o+="("; for(size_t t=0;t<p;++t){ if(t) o+=" "; o+=tk[k+t]; } sprintf(b,")^%zu ",r); o+=b; k+=r*p; done=true; } }
    if(!done){ o+=tk[k]; o+=" "; ++k; }
  }
  return o;
}
std::string dec(const std::string&a){ if(a.find(',')==std::string::npos && a.find('*')==std::string::npos) return a; std::string o; size_t i=0;
  while(i<=a.size()){ size_t j=a.find(',',i); if(j==std::string::npos) j=a.size(); std::string seg=a.substr(i,j-i); size_t st=seg.find('*');
    if(st==std::string::npos) o+=seg; else { std::string p=seg.substr(0,st); long long k=atoll(seg.c_str()+st+1); for(long long t=0;t<k;++t) o+=p; } i=j+1; }
  return o; }
int main(int argc,char**argv){
  const char*M=argv[1]; int q=argv[2][0]-'A'; std::string L=dec(argv[3]), R=dec(argv[4]); if(L=="-")L=""; ll maxs=atoll(argv[5]); char mode=argv[6][0]; ll stride= argc>7?atoll(argv[7]):1; ll maxev= argc>8?atoll(argv[8]):(1LL<<62);
  ns=(strlen(M)+1)/7;
  for(int s=0;s<ns;++s)for(int b=0;b<2;++b){const char*p=M+s*7+b*3; if(p[0]=='-'||p[2]=='-'){Nx[s][b]=-1;continue;} W[s][b]=p[0]-'0'; Dm[s][b]=p[1]=='R'?1:-1; Nx[s][b]=p[2]-'A';}
  SZ=1LL<<29; tape=(unsigned char*)calloc(SZ,1); ll h=SZ/2; ll c=h-(ll)L.size();
  for(char ch:L) tape[c++]=ch-'0'; for(char ch:R) tape[c++]=ch-'0';
  ll lo=h-(ll)L.size(), hi=c-1; ll ev=0;
  for(ll s=0;s<maxs;++s){
    int sym=tape[h];
    if(mode=='t' && q==4 && sym==0 && tape[h+1]==1 && tape[h+2]==0 && tape[h+3]==0){ while(lo<h && !tape[lo]) ++lo; if(lo>=h){ printf("KMOM %lld\n",s); return 0; } }
    bool isE = (q==4 && sym==0 && tape[h+1]==1 && (mode=='f' || (tape[h+2]==0 && tape[h+3]==0))); if(mode=='f' && isE) isE=true;
    bool isH = (q==7); if(mode=='t'){isE = (q==4 && sym==0 && tape[h-1]==0 && tape[h-2]==1 && tape[h-3]==1 && tape[h+1]==1);} if(mode=='s'){isE=true;}
    if((isE && (mode=='e'||mode=='x'||mode=='s'||mode=='f'||mode=='t')) || (isH && (mode=='h'||mode=='x'))){
      if(ev>=maxev*stride){printf("MAXEV %lld\n",s);return 0;} if(ev++%stride==0){ ll a=lo; while(a<hi && !tape[a]) ++a; ll b=hi; while(b>a && !tape[b]) --b; if(h<a)a=h; if(h>b)b=h;
        printf("%lld %c%d @%lld | %s\n",s,'A'+q,sym,h-a,rle(a,b,h,q).c_str()); }
    }
    int nx=Nx[q][sym]; if(nx<0){ ll a=lo; while(a<hi&&!tape[a])++a; ll b=hi; while(b>a&&!tape[b])--b; if(h<a)a=h; if(h>b)b=h; ll ones=0; for(ll i=lo;i<=hi;++i) ones+=tape[i];
      printf("HALT %lld %c%d ones=%lld | %s\n",s,'A'+q,sym,ones,rle(a,b,h,q).c_str()); return 0; }
    tape[h]=W[q][sym]; h+=Dm[q][sym]; q=nx; if(h<lo)lo=h; if(h>hi)hi=h;
    if(h<2||h>SZ-3){printf("EDGE %lld\n",s); return 0;}
  }
  printf("END %lld\n",maxs); return 0;
}
