// ev: literal TM run from a constructed tape (template orientation: tape LEFT of head, head on blank in state Q).
//  ev MACHINE O Q MAXSTEPS MAXOUT  < lines: each line = one job: "<bits>" or "B" (blank tape, start state A)
//  For each job prints one line: outcomes separated by ' ; ' :
//    "M <step> <mask> <rle-bits>" for each moment (state Q, head on blank, right side blank) after >=1 step,
//    "H <step> <ones> <slot> <rle-tape-around>" at halt, "T <step>" on step limit, "X" tape overflow.
//  mask = 2*NS hex digits? -> printed as list of slot indices used since last moment, e.g. A0.B1.
//  Machine may have up to 16 states; '---' or 'xxH' = halt.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
int nx[16][2], wr[16][2], dr[16][2]; int ns;
static std::string rle(const std::vector<uint8_t>&T,long long a,long long b){std::string o;long long i=a;while(i<b){long long j=i;while(j<b&&T[j]==T[i])++j;o+=char('0'+T[i]);if(j-i>1)o+="^"+std::to_string(j-i);o+='.';i=j;}return o.empty()?"-":o;}
int main(int argc,char**argv){
  if(argc<6)return 2; const char*M=argv[1]; bool mir=argv[2][0]=='L'; int Q=argv[3][0]-'A'; long long N=atoll(argv[4]); long long maxout=atoll(argv[5]); char fam=argc>6?argv[6][0]:'-';
  int nst=(int)((strlen(M)+1)/7); ns=0; for(const char*t=M;*t;){for(int c=0;c<2;++c){if(t[0]=='-'||t[2]=='-'||t[2]=='Z'||(t[2]-'A')>=nst)nx[ns][c]=-1;else{wr[ns][c]=t[0]-'0';dr[ns][c]=(t[1]=='R')?1:-1;if(mir)dr[ns][c]=-dr[ns][c];nx[ns][c]=t[2]-'A';}t+=3;}++ns;if(*t=='_')++t;}
  const long long SZ=1LL<<25; std::vector<uint8_t> T(SZ,0); std::vector<long long> used(32,0), pr(64,0); int last=-1;
  static char buf[1<<22];
  while(fgets(buf,sizeof buf,stdin)){
    std::string w(buf); while(!w.empty()&&(w.back()=='\n'||w.back()=='\r'||w.back()==' '))w.pop_back(); if(w.empty())continue;
    std::fill(T.begin(),T.end(),0); long long p=SZ/2; int q; long long lo=p,hi=p;
    if(w=="B"){q=0;} else {q=Q; for(size_t i=0;i<w.size();++i)T[p-(long long)w.size()+(long long)i]=w[i]-'0'; lo=p-(long long)w.size();}
    for(auto&u:used)u=0; for(auto&u:pr)u=0; last=-1; long long nout=0; std::string out; bool done=false;
    for(long long st=0;st<N;++st){
      if(p<=2||p>=SZ-2){out+="X";done=true;break;}
      int c=T[p];
      if(nx[q][c]<0){long long ones=0;for(long long i=lo;i<=hi;++i)ones+=T[i]; long long a=lo,b=hi+1; if(p<a)a=p; if(p+1>b)b=p+1;
        char tmp[128];sprintf(tmp,"H %lld %lld %c%d %lld ",st,ones,'A'+q,c,p-a); out+=tmp; out+=(b-a<4000)?rle(T,a,b):"big"; done=true;break;}
      if(last>=0)pr[last*2+c]++; last=q*2+c; used[q*2+c]++; T[p]=wr[q][c]; if(T[p]){if(p<lo)lo=p;if(p>hi)hi=p;}
      p+=dr[q][c]; q=nx[q][c];
      if(q!=Q||T[p])continue;
      while(hi>lo&&!T[hi])--hi; if(hi>p)continue;
      while(lo<p&&!T[lo])++lo;
      // moment (a=0 filter by family: B: ..00(10)^y1, A: ..00(10)^y, C: ..001^y0)
      if(fam!='-'){ long long x=p-1;
        if(fam=='B'){ if(T[x]!=1)continue; --x; while(x-1>=lo&&T[x]==0&&T[x-1]==1)x-=2; }
        else if(fam=='A'){ while(x-1>=lo&&T[x]==0&&T[x-1]==1)x-=2; }
        else if(fam=='C'){ if(T[x]!=0)continue; --x; while(x>=lo&&T[x]==1)--x; }
    else if(fam=='c'){ while(x>=lo&&T[x]==1)--x; }
        if(fam=='C'||fam=='c'){ if(!(x-1>=lo&&T[x]==0&&T[x-1]==0))continue; } else { if(!(x-1>=lo&&T[x]==0&&!(x-2>=lo&&T[x-2]==1&&T[x-1]==0)))continue; } }
      std::string mk; for(int i=0;i<2*ns;++i)if(used[i]){mk+=char('A'+i/2);mk+=char('0'+i%2);} if(mk.empty())mk="-"; if(getenv("EVPAIRS")){mk+=":";for(int i=0;i<4*ns;++i)if(pr[i]){mk+=char('A'+i/4);mk+=char('0'+(i/2)%2);mk+=char('0'+i%2);}}
      char tmp[64]; sprintf(tmp,"M %lld %s ",st+1,mk.c_str()); out+=tmp;
      std::string bits; for(long long i=lo;i<p;++i)bits+=char('0'+T[i]);
      if(mir){} // template orientation already: for mirrored machines the tape left of head in template = cells left (we mirror moves)
      out+=(bits.size()<200000)?bits:std::string("big");
      for(auto&u:used)u=0; for(auto&u:pr)u=0;
      if(++nout>=maxout){done=true;break;}
      out+=" ; ";
    }
    if(!done){char tmp[64];sprintf(tmp,"T %lld",N);out+=tmp;}
    puts(out.c_str()); fflush(stdout);
  }
}
