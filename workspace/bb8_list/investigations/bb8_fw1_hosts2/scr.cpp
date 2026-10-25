// scr: enumerate one-new-state (H) extensions and single-transition changes of a base machine; engine battery filter.
//  scr BASE O Q FAM ENGFILE RAREFILE MODE > out
//  ENGFILE lines: "<tape> <expected-moment-bits> <budget>"   RAREFILE lines: "<tape> <budget>"
//  MODE 8: 8-state extensions: redirect slot X (any of 14, incl. halt slot) -> (w,d,H) for 4 (w,d); H0,H1 in {halt} U {w,d,state<8} (33 each)
//  MODE 7: single-transition changes: slot X -> any of {halt} U {w,d,state<7}
//  Output per engine-intact variant whose rare outcomes differ from base: "<machine>\t<rare outcomes '|' separated>"
//  Also prints a summary line "# total N intact I differ D".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
#include <fstream>
#include <sstream>
#include <iostream>
struct Tr{int w,d,n;}; // n=-1 halt
int NS; Tr tab[16][2]; bool mir; int Q; char fam;

static std::string fmtM(){std::string s;for(int i=0;i<NS;++i){if(i)s+='_';for(int c=0;c<2;++c){Tr t=tab[i][c];if(t.n<0)s+="---";else{s+=char('0'+t.w);s+=(t.d>0?'R':'L');s+=char('A'+t.n);}}}return s;}
// run from tape; returns outcome string: "M<bits>" first a=0 moment, "H<step>", "T", "X"
static std::string runjob(const std::string&w,long long N,long long*steps=nullptr){
  const long long SZ=2*((long long)w.size()+N)+16; std::vector<uint8_t> T(SZ,0); long long p=(long long)w.size()+N+8; int q=Q; long long lo=p-(long long)w.size(),hi=p;
  for(size_t i=0;i<w.size();++i)T[p-(long long)w.size()+(long long)i]=w[i]-'0';
    for(long long st=0;st<N;++st){
    if(p<=2||p>=SZ-2)return "X";
    int c=T[p]; Tr t=tab[q][c];
    if(t.n<0){ if(steps)*steps=st; return "H"+std::to_string(st);}
    T[p]=t.w; if(t.w){if(p<lo)lo=p;if(p>hi)hi=p;}
    p+=mir?-t.d:t.d; q=t.n;
    if(q!=Q||T[p])continue;
    while(hi>lo&&!T[hi])--hi; if(hi>p)continue;
    while(lo<p&&!T[lo])++lo;
    long long x=p-1;
    if(fam=='B'){ if(T[x]!=1)continue; --x; while(x-1>=lo&&T[x]==0&&T[x-1]==1)x-=2; }
    else if(fam=='A'){ while(x-1>=lo&&T[x]==0&&T[x-1]==1)x-=2; }
    else if(fam=='C'){ if(T[x]!=0)continue; --x; while(x>=lo&&T[x]==1)--x; }
    else if(fam=='c'){ while(x>=lo&&T[x]==1)--x; }
    if(fam=='-'){} else if(fam=='C'||fam=='c'){ if(!(x-1>=lo&&T[x]==0&&T[x-1]==0))continue; } else { if(!(x-1>=lo&&T[x]==0&&!(x-2>=lo&&T[x-2]==1&&T[x-1]==0)))continue; }
    if(steps)*steps=st+1;
    std::string b; for(long long i=lo;i<p;++i)b+=char('0'+T[i]); return "M"+b;
  }
  return "T";
}
int main(int argc,char**argv){
  if(argc<8)return 2;
  std::string base=argv[1]; mir=argv[2][0]=='L'; Q=argv[3][0]-'A'; fam=argv[4][0]; int mode=atoi(argv[7]);
  int ns=0; for(size_t i=0;i<base.size();){for(int c=0;c<2;++c){std::string t=base.substr(i,3);if(t[0]=='-'||t[2]=='-'||t[2]=='H')tab[ns][c]={0,0,-1};else tab[ns][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A'};i+=3;}++ns;if(i<base.size()&&base[i]=='_')++i;}
  std::vector<std::string> et,ee; std::vector<long long> eb; {std::ifstream f(argv[5]);std::string a,b;long long n;while(f>>a>>b>>n){et.push_back(a);ee.push_back(b);eb.push_back(n);}}
  std::vector<std::string> rt; std::vector<long long> rb; {std::ifstream f(argv[6]);std::string a;long long n;while(f>>a>>n){rt.push_back(a);rb.push_back(n);}}
  Tr orig[16][2]; memcpy(orig,tab,sizeof tab);
  // base rare outcomes
  NS=ns; std::vector<std::string> baser; for(size_t i=0;i<rt.size();++i)baser.push_back(runjob(rt[i],rb[i]));
  long long total=0,intact=0,differ=0;
  std::vector<Tr> opts; int NSt=(mode==8?ns+1:ns);
  opts.push_back({0,0,-1}); for(int w=0;w<2;++w)for(int d=-1;d<=1;d+=2)for(int n=0;n<NSt;++n)opts.push_back({w,d,n});
  auto test=[&](){
    ++total;
    for(size_t i=0;i<et.size();++i){ std::string o=runjob(et[i],eb[i]); if(o.size()<1||o[0]!='M'||o.compare(1,std::string::npos,ee[i])!=0)return; }
    ++intact;
    std::string out; bool dif=false;
    for(size_t i=0;i<rt.size();++i){ std::string o=runjob(rt[i],rb[i]); if(o!=baser[i])dif=true; if(i)out+='|'; out+=(o==baser[i]?std::string("="):(o[0]=='M'?o:o)); }
    if(dif){++differ; printf("%s\t%s\n",fmtM().c_str(),out.c_str()); fflush(stdout);}
  };
  if(mode==8){
    NS=ns+1;
    for(int X=0;X<2*ns;++X){
      for(int w=0;w<2;++w)for(int d=-1;d<=1;d+=2){
        memcpy(tab,orig,sizeof tab); tab[X/2][X%2]={w,d,ns};
        for(auto h0:opts)for(auto h1:opts){ tab[ns][0]=h0; tab[ns][1]=h1; test(); }
      }
    }
  } else if(mode==9){
    // argv[8]=X slot (e.g. B0), argv[9]=s symbol read after X that occurs only in rare events
    int X=(argv[8][0]-'A')*2+(argv[8][1]-'0'); int sy=argv[9][0]-'0';
    NS=ns+2; int H=ns,I=ns+1; Tr tx=orig[X/2][X%2];
    std::vector<Tr> o9; o9.push_back({0,0,-1}); for(int w=0;w<2;++w)for(int d=-1;d<=1;d+=2)for(int n=0;n<ns+2;++n)o9.push_back({w,d,n});
    for(int w=0;w<2;++w)for(int d=-1;d<=1;d+=2){
      memcpy(tab,orig,sizeof tab); tab[X/2][X%2]={tx.w,tx.d,H}; tab[H][1-sy]=orig[tx.n][1-sy]; tab[H][sy]={w,d,I};
      for(auto i0:o9)for(auto i1:o9){ tab[I][0]=i0; tab[I][1]=i1; test(); }
    }
  } else {
    NS=ns;
    for(int X=0;X<2*ns;++X) for(auto o:opts){ memcpy(tab,orig,sizeof tab); if(o.n==orig[X/2][X%2].n&&o.w==orig[X/2][X%2].w&&o.d==orig[X/2][X%2].d)continue; tab[X/2][X%2]=o; test(); }
  }
  printf("# total %lld intact %lld differ %lld\n",total,intact,differ);
  // base rare outcomes for reference
  for(size_t i=0;i<rt.size();++i){std::string z="#R "+std::to_string(i)+" "+baser[i].substr(0,300); puts(z.c_str());}
}
