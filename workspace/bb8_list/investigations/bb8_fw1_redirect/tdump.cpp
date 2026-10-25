// tdump MACHINE N1 [N2 ...]: run from blank, at each listed step print state, head offset and run-length tape
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2],Dd[16][2],NX[16][2];
int main(int argc,char**argv){std::string m=argv[1];int n=(m.size()+1)/7;
 for(int q=0;q<n;++q)for(int c=0;c<2;++c){const char*x=m.c_str()+7*q+3*c;if(x[0]=='-'){NX[q][c]=-1;continue;}W[q][c]=x[0]-'0';Dd[q][c]=x[1]=='R'?1:-1;NX[q][c]=x[2]-'A';}
 long long size=1<<25,off=size/2;std::vector<unsigned char>t(size,0);long long pos=0,lo=0,hi=0;int q=0;int ai=2;
 for(long long st=0;ai<argc;++st){ if(st==atoll(argv[ai])){ printf("step %lld state %c head %lld: ",st,'A'+q,pos-lo);
   for(long long i=lo;i<=hi;){long long j=i;while(j<=hi&&t[j+off]==t[i+off])++j;long long k=j-i; if(k>=3)printf("%d^%lld ",t[i+off],k);else for(long long z=0;z<k;z++)printf("%d",t[i+off]); if(k<3)printf(" "); i=j;} printf("\n"); ++ai; if(ai>=argc)break;}
  int c=t[pos+off];if(NX[q][c]<0){printf("HALT %lld\n",st);break;}t[pos+off]=W[q][c];pos+=Dd[q][c];q=NX[q][c];if(pos<lo)lo=pos;if(pos>hi)hi=pos;}
}
