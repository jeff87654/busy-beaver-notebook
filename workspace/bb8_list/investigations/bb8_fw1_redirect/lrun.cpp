// lrun LIST N : blank-tape run of each machine (col 1 of LIST) for N steps. Prints machine, H:steps:ones:slot | X/C:step:span | T:span:ones
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <fstream>
int W[20][2],Dd[20][2],NX[20][2];
int main(int argc,char**argv){std::ifstream f(argv[1]);long long N=atoll(argv[2]);std::string l;
 std::vector<unsigned char>t;
 while(std::getline(f,l)){std::string m=l.substr(0,l.find('\t'));if(m.size()<20)continue;int n=(m.size()+1)/7;
  for(int q=0;q<n;++q)for(int c=0;c<2;++c){const char*x=m.c_str()+7*q+3*c;if(x[0]=='-'){NX[q][c]=-1;continue;}W[q][c]=x[0]-'0';Dd[q][c]=x[1]=='R'?1:-1;NX[q][c]=x[2]-'A';}
  long long size=1<<16,off=size/2;t.assign(size,0);long long pos=0,mn=0,mx=0,ckp=1024,lastsp=-1;int q=0;char k='T';long long st=0;
  for(;st<N;++st){ if(pos+off<2||pos+off+2>=size){ if(size>=(1LL<<27)){k='W';break;} std::vector<unsigned char>nt(size*2,0);memcpy(nt.data()+size/2,t.data(),size);off+=size/2;size*=2;t.swap(nt);}
   int c=t[pos+off]; if(NX[q][c]<0){k='H';break;} t[pos+off]=W[q][c];pos+=Dd[q][c];q=NX[q][c]; if(pos<mn)mn=pos;if(pos>mx)mx=pos;
   if(st==ckp){long long sp=mx-mn; if(st>=32768&&sp>8.0*sqrt((double)st)+200){k='X';break;} if(st>=131072&&sp==lastsp){k='C';break;} lastsp=sp;ckp*=2;} }
  long long ones=0;for(auto v:t)ones+=v;
  if(k=='H')printf("%s\tH:%lld:%lld:%c%d\n",m.c_str(),st,ones,'A'+q,t[pos+off]);else printf("%s\t%c:%lld:%lld:%lld\n",m.c_str(),k,st,mx-mn,ones);
  fflush(stdout);}
}
