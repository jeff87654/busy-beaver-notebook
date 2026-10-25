// multi MACHINE K0 K1 L0 L1 N : for each K, L run M3-like tape 1^2 3| (1|)^K L| 1| 1. from B-frontier for N steps; print matrix (H halt, . ok, E edge)
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; int K0=atoi(argv[2]),K1=atoi(argv[3]),L0=atoi(argv[4]),L1=atoi(argv[5]); long long N=atoll(argv[6]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  const long long SZ=1LL<<22; vector<uint8_t> tape(SZ,0);
  for(int K=K0;K<=K1;K++){
    string row;
    for(int L=L0;L<=L1;L++){
      string w="1010"+string(3,'1')+"00"; for(int i=0;i<K;i++) w+="100"; w+=string(L,'1')+"00"+"1"+"00"+"1";
      fill(tape.begin(),tape.end(),0); long long p=SZ/2; int q=1;
      for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
      char res='.';
      for(long long st=0;st<N;st++){
        int c=tape[p]; T&t=tm[q][c];
        if(!t.ok){res='H';break;}
        tape[p]=t.w; p+=t.d; q=t.n;
        if(p<100||p>SZ-100){res='E';break;}
      }
      row+=res;
    }
    printf("K=%3d %s\n",K,row.c_str()); fflush(stdout);
  }
}
