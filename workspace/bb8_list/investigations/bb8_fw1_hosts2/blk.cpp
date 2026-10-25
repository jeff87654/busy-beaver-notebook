// blk BASE MODE N THR : enumerate variants as scr.cpp (mode 8 / 7), run each from blank tape (state A) for N steps
// (orientation irrelevant from blank). Print variants that halt at step >= THR: "<machine>\tH steps sigma span".
// Summary counts: halt<THR, halt>=THR, running.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
struct Tr{int w,d,n;};
int NS; Tr tab[16][2];
static std::string fmtM(){std::string s;for(int i=0;i<NS;++i){if(i)s+='_';for(int c=0;c<2;++c){Tr t=tab[i][c];if(t.n<0)s+="---";else{s+=char('0'+t.w);s+=(t.d>0?'R':'L');s+=char('A'+t.n);}}}return s;}
static std::vector<uint8_t> T;
int main(int argc,char**argv){
  std::string base=argv[1]; int mode=atoi(argv[2]); long long N=atoll(argv[3]), THR=atoll(argv[4]);
  int ns=0; for(size_t i=0;i<base.size();){for(int c=0;c<2;++c){std::string t=base.substr(i,3);if(t[0]=='-')tab[ns][c]={0,0,-1};else tab[ns][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A'};i+=3;}++ns;if(i<base.size()&&base[i]=='_')++i;}
  Tr orig[16][2]; memcpy(orig,tab,sizeof tab);
  long long SZ=2*N+16; T.assign(SZ,0);
  long long cnt[3]={0,0,0};
  auto test=[&](){
    long long p=N+8,lo=p,hi=p; int q=0; long long st;
    for(st=0;st<N;++st){ int c=T[p]; Tr t=tab[q][c]; if(t.n<0)break; T[p]=t.w; p+=t.d; q=t.n; if(p<lo)lo=p; if(p>hi)hi=p; }
    long long ones=0; for(long long i=lo;i<=hi;++i){ones+=T[i];T[i]=0;}
    if(st<N){ if(st>=THR){cnt[1]++; printf("%s\tH %lld %lld %lld\n",fmtM().c_str(),st,ones,hi-lo+1); fflush(stdout);} else cnt[0]++; }
    else cnt[2]++;
  };
  std::vector<Tr> opts; int NSt=(mode==8?ns+1:ns);
  opts.push_back({0,0,-1}); for(int w=0;w<2;++w)for(int d=-1;d<=1;d+=2)for(int n=0;n<NSt;++n)opts.push_back({w,d,n});
  if(mode==8){ NS=ns+1;
    for(int X=0;X<2*ns;++X)for(int w=0;w<2;++w)for(int d=-1;d<=1;d+=2){ memcpy(tab,orig,sizeof tab); tab[X/2][X%2]={w,d,ns};
      for(auto h0:opts)for(auto h1:opts){ tab[ns][0]=h0; tab[ns][1]=h1; test(); } }
  } else { NS=ns;
    for(int X=0;X<2*ns;++X)for(auto o:opts){ memcpy(tab,orig,sizeof tab); Tr g=orig[X/2][X%2]; if(o.n==g.n&&o.w==g.w&&o.d==g.d)continue; tab[X/2][X%2]=o; test(); } }
  std::string z="# halt<thr "+std::to_string(cnt[0])+" halt>=thr "+std::to_string(cnt[1])+" running "+std::to_string(cnt[2]); puts(z.c_str());
}
