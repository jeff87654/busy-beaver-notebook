// usage MACHINE n b N : transition usage counts (and first-use step) from K(0^n;0;b)
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
string D(int m){string s; for(int i=0;i<m;i++) s+="10"; return s+"1";}
int main(int argc,char**argv){
  string ms=argv[1]; int n=atoi(argv[2]); long long b=atoll(argv[3]); long long N=atoll(argv[4]);
  T tm[16][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  string w="11"; for(int i=0;i<n;i++) w+=D(1); w+=D(1); for(long long i=0;i<3*b+2;i++) w+="10"; w+="111001";
  long long SZ=1LL<<27; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+w.size(); int q=1; long long cnt[16][2]={}, first[16][2]; for(auto&r:first)for(auto&x:r)x=-1;
  long long minp=p;
  for(long long st=0;st<N;st++){
    int c=tape[p]; if(first[q][c]<0) first[q][c]=st; cnt[q][c]++;
    T&t=tm[q][c]; if(!t.ok){ printf("HALT at %lld\n",st); break;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<minp) minp=p; if(p<100||p>SZ-100){printf("EDGE\n");break;}
  }
  for(int s=0;s<8;s++){ printf("%c:",'A'+s); for(int c=0;c<2;c++) printf(" %d:[%lld first %lld]",c,cnt[s][c],first[s][c]); printf("\n"); }
  printf("leftmost %lld\n",minp-off);
}
