// snap MACHINE N K : run from blank; at steps 10^k-ish checkpoints (N*i/K) print state, head offset and RLE tape.
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>
int main(int argc,char**argv){
  const char*s=argv[1]; long long N=atoll(argv[2]); int K=atoi(argv[3]);
  int nx[16][2],w[16][2],d[16][2]; int n=0,len=strlen(s);
  for(int i=0;i<len;i+=7){for(int c=0;c<2;c++){const char*x=s+i+3*c; if(x[0]=='-'){nx[n][c]=-1;w[n][c]=1;d[n][c]=1;} else {w[n][c]=x[0]-'0';d[n][c]=x[1]=='R'?1:-1;nx[n][c]=x[2]-'A';}} n++;}
  long long SZ=1LL<<26; std::vector<unsigned char>T(SZ,0); long long p=SZ/2,lo=p,hi=p; int q=0;
  long long nextc=1; int ci=0; double r=1;
  for(long long st=0;st<N;st++){
    if(st==nextc){ std::string o; long long i=lo; while(i<=hi){long long j=i; while(j<=hi&&T[j]==T[i])j++; o+=char('0'+T[i]); if(j-i>1){o+="^"+std::to_string(j-i);} o+=' '; i=j;}
      printf("t=%lld q=%c head=%lld span=%lld | %s\n",st,'A'+q,p-lo,hi-lo+1,o.c_str()); fflush(stdout); nextc=(long long)(nextc*2);}
    int c=T[p]; if(nx[q][c]<0){printf("HALT %lld\n",st);return 0;}
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c]; if(p<lo)lo=p; if(p>hi)hi=p; if(p<5||p>SZ-5){printf("TAPE\n");return 0;}
  }
  printf("END %lld\n",N); return 0;}
