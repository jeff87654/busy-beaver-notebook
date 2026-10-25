// tprof MACHINE STEPS: literal run from blank; per slot: uses, first step, last step; log2-bucketed use steps for rare slots
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2],Dd[16][2],NX[16][2];
int main(int argc,char**argv){std::string m=argv[1];long long N=atoll(argv[2]);int n=(m.size()+1)/7;
 for(int q=0;q<n;++q)for(int c=0;c<2;++c){const char*x=m.c_str()+7*q+3*c;if(x[0]=='-'){NX[q][c]=-1;continue;}W[q][c]=x[0]-'0';Dd[q][c]=x[1]=='R'?1:-1;NX[q][c]=x[2]-'A';}
 long long size=1<<22,off=size/2;std::vector<unsigned char>t(size,0);long long pos=0;int q=0;
 long long cnt[16][2]={},first[16][2],last[16][2];std::vector<long long> ev[16][2];
 for(int a=0;a<16;a++)for(int b=0;b<2;b++){first[a][b]=-1;last[a][b]=-1;}
 long long st=0;for(;st<N;++st){ if(pos+off<2||pos+off+2>=size){std::vector<unsigned char>nt(size*2,0);memcpy(nt.data()+size/2,t.data(),size);off+=size/2;size*=2;t.swap(nt);}
  int c=t[pos+off]; if(NX[q][c]<0){printf("HALT %lld state %c read %d\n",st,'A'+q,c);break;}
  cnt[q][c]++; if(first[q][c]<0)first[q][c]=st; last[q][c]=st; if(ev[q][c].size()<40)ev[q][c].push_back(st);
  t[pos+off]=W[q][c];pos+=Dd[q][c];q=NX[q][c];}
 printf("steps %lld\n",st);
 for(int a=0;a<n;a++)for(int b=0;b<2;b++){printf("%c%d uses=%lld first=%lld last=%lld",'A'+a,b,cnt[a][b],first[a][b],last[a][b]);
  if(cnt[a][b]&&cnt[a][b]<=40){printf(" at");for(auto x:ev[a][b])printf(" %lld",x);} printf("\n");}
}
