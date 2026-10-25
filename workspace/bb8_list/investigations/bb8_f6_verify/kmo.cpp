// kmo: literal sim; print block vectors at K-moments (state E on 0, next "100", nothing nonzero left of head).
// kmo MACHINE STATE LEFT RIGHT MAXSTEPS MAXEV [onlychange]
// Block vector: [E0] 1 00 1^b0 (0^z) 1^b1 ... final sentinel. zero-run z: 2 -> sep, 2+2j -> j zero blocks, odd -> '!z'
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
int W[16][2], Dm[16][2], Nx[16][2]; int ns;
unsigned char *tape; ll SZ;
int main(int argc,char**argv){
  const char*M=argv[1]; int q=argv[2][0]-'A'; std::string L=argv[3], R=argv[4]; if(L=="-")L=""; ll maxs=atoll(argv[5]); ll maxev=atoll(argv[6]);
  ns=(strlen(M)+1)/7;
  for(int s=0;s<ns;++s)for(int b=0;b<2;++b){const char*p=M+s*7+b*3; if(p[0]=='-'||p[2]=='-'){Nx[s][b]=-1;continue;} W[s][b]=p[0]-'0'; Dm[s][b]=p[1]=='R'?1:-1; Nx[s][b]=p[2]-'A';}
  SZ=1LL<<30; tape=(unsigned char*)calloc(SZ,1); ll h=SZ/2; ll c=h-(ll)L.size();
  for(char ch:L) tape[c++]=ch-'0'; for(char ch:R) tape[c++]=ch-'0';
  ll lo=h-(ll)L.size(), hi=c-1; ll ev=0, hent=0, lastk=0;
  for(ll s=0;s<maxs;++s){
    int sym=tape[h];
    if(q==7) ++hent;
    if(q==4 && sym==0 && tape[h+1]==1 && tape[h+2]==0 && tape[h+3]==0){
      while(lo<h && !tape[lo]) ++lo;
      if(lo>=h){ // left blank
        while(hi>h && !tape[hi]) --hi;
        std::string o; char b[64]; ll i=h+4; std::vector<ll> bl; std::string flag;
        while(i<=hi){ ll j=i; while(j<=hi&&tape[j])++j; ll ones=j-i; ll k=j; while(k<=hi&&!tape[k])++k; ll z=k-j;
          if(k>hi){ // last run: sentinel ones
            bl.push_back(-ones); break; }
          bl.push_back(ones); if(z%2){ sprintf(b,"!z%lld@%zu ",z,bl.size()); flag+=b; } for(ll t=0;t<(z-2)/2;++t) bl.push_back(0); i=k; }
        // print with repeat compression
        size_t k=0; while(k<bl.size()){ size_t r=1; while(k+r<bl.size()&&bl[k+r]==bl[k])++r; if(r>=3){sprintf(b,"%lld^%zu ",bl[k],r);k+=r;} else {sprintf(b,"%lld ",bl[k]);++k;} o+=b; }
        printf("K %lld H=%lld nb=%zu | %s%s\n",s,hent,bl.size(),o.c_str(),flag.c_str()); hent=0;
        if(++ev>=maxev) return 0;
      }
    }
    int nx=Nx[q][sym]; if(nx<0){ ll ones=0; for(ll i=lo;i<=hi;++i) ones+=tape[i]; printf("HALT %lld %c%d ones=%lld H=%lld\n",s,'A'+q,sym,ones,hent); return 0; }
    tape[h]=W[q][sym]; h+=Dm[q][sym]; q=nx; if(h<lo)lo=h; if(h>hi)hi=h;
    if(h<2||h>SZ-3){printf("EDGE %lld\n",s); return 0;}
  }
  printf("END %lld\n",maxs); return 0;
}
