// spn MACHINE O Q N < tapes : per job print "H steps ones" or "R pmin pmax ones lastmom" after N steps (positions relative to head start)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
int nx[16][2],wr[16][2],dr[16][2];
int main(int argc,char**argv){
  const char*M=argv[1]; bool mir=argv[2][0]=='L'; int Q=argv[3][0]-'A'; long long N=atoll(argv[4]);
  int nst=(int)((strlen(M)+1)/7),ns=0; for(const char*t=M;*t;){for(int c=0;c<2;++c){if(t[0]=='-'||t[2]=='-'||(t[2]-'A')>=nst)nx[ns][c]=-1;else{wr[ns][c]=t[0]-'0';dr[ns][c]=(t[1]=='R')?1:-1;if(mir)dr[ns][c]=-dr[ns][c];nx[ns][c]=t[2]-'A';}t+=3;}++ns;if(*t=='_')++t;}
  static char buf[1<<20];
  while(fgets(buf,sizeof buf,stdin)){
    std::string w(buf); while(!w.empty()&&(w.back()=='\n'||w.back()=='\r'))w.pop_back(); if(w.empty())continue;
    long long SZ=2*(w.size()+N)+16; std::vector<uint8_t>T(SZ,0); long long p0=w.size()+N+8,p=p0; int q=Q;
    for(size_t i=0;i<w.size();++i)T[p-(long long)w.size()+i]=w[i]-'0';
    long long pmin=p,pmax=p,st; bool h=false;
    for(st=0;st<N;++st){int c=T[p]; if(nx[q][c]<0){h=true;break;} T[p]=wr[q][c]; p+=dr[q][c]; q=nx[q][c]; if(p<pmin)pmin=p; if(p>pmax)pmax=p;}
    long long ones=0; for(auto v:T)ones+=v;
    if(h)printf("H %lld %lld\n",st,ones); else printf("R %lld %lld %lld\n",pmin-p0,pmax-p0,ones);
    fflush(stdout);
  }
}
