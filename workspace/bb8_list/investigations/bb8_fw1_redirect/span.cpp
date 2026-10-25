#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2],Dd[16][2],NX[16][2];
int main(int argc,char**argv){std::string m=argv[1];long long N=atoll(argv[2]);int n=(m.size()+1)/7;
 for(int q=0;q<n;++q)for(int c=0;c<2;++c){const char*x=m.c_str()+7*q+3*c;if(x[0]=='-'){NX[q][c]=-1;continue;}W[q][c]=x[0]-'0';Dd[q][c]=x[1]=='R'?1:-1;NX[q][c]=x[2]-'A';}
 long long size=1<<24,off=size/2;std::vector<unsigned char>t(size,0);long long pos=0,mn=0,mx=0;int q=0;long long nxt=1<<14;
 for(long long st=0;st<N;++st){int c=t[pos+off];if(NX[q][c]<0){printf("HALT %lld\n",st);break;}t[pos+off]=W[q][c];pos+=Dd[q][c];q=NX[q][c];if(pos<mn)mn=pos;if(pos>mx)mx=pos;
  if(st==nxt){printf("%lld:%lld ",st,mx-mn);nxt*=2;}}
 printf("\n");}
