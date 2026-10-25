// blklist N THR < machines : run each from blank (state A) N steps; print halts >= THR, summary
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
int main(int argc,char**argv){
  long long N=atoll(argv[1]),THR=atoll(argv[2]); std::vector<uint8_t>T(2*N+16,0); static char buf[256];
  long long c0=0,c1=0,c2=0;
  while(fgets(buf,sizeof buf,stdin)){
    std::string M(buf); while(!M.empty()&&(M.back()=='\n'||M.back()=='\r'))M.pop_back(); if(M.empty())continue;
    int nst=(int)((M.size()+1)/7); int nx[16][2],wr[16][2],dr[16][2]; int ns=0;
    for(size_t i=0;i<M.size();){for(int c=0;c<2;++c){const char*t=M.c_str()+i; if(t[0]=='-'||t[2]=='-'||(t[2]-'A')>=nst)nx[ns][c]=-1;else{wr[ns][c]=t[0]-'0';dr[ns][c]=t[1]=='R'?1:-1;nx[ns][c]=t[2]-'A';}i+=3;}++ns;if(i<M.size()&&M[i]=='_')++i;}
    long long p=N+8,lo=p,hi=p,st; int q=0;
    for(st=0;st<N;++st){int c=T[p]; if(nx[q][c]<0)break; T[p]=wr[q][c]; p+=dr[q][c]; q=nx[q][c]; if(p<lo)lo=p; if(p>hi)hi=p;}
    long long ones=0; for(long long i=lo;i<=hi;++i){ones+=T[i];T[i]=0;}
    if(st<N){ if(st>=THR){c1++; printf("%s\tH %lld %lld\n",M.c_str(),st,ones);} else c0++; } else c2++;
  }
  std::string z="# halt<thr "+std::to_string(c0)+" halt>=thr "+std::to_string(c1)+" running "+std::to_string(c2); puts(z.c_str());
}
