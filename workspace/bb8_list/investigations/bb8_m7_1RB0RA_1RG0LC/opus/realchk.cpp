// realchk CERT N : run the machine from the blank tape for N steps with writer annotations; check every configuration
// is covered by the certificate: (q, m, left state, right state) in C and every folded side state in S.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
struct T{int w,d,n;bool ok;};
int kL,kR,ANN,GON; unsigned char GT[256][2]; T TMX[8][2];
u64 wL,wR;
u64 foldL(u64 s,int c){ return ((s&wL)<<5|c)&wL; }
u64 foldR(u64 s,int c){ return (((s&wR)<<5|c)&wR)|((u64)GT[(s>>55)&255][c&1]<<55); }
int main(int argc,char**argv){
  string ms="1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE";
  {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") TMX[i][c]={0,0,0,false}; else TMX[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  FILE*f=fopen(argv[1],"r"); char tag[4]; fscanf(f,"%s %d %d %d %d",tag,&kL,&kR,&ANN,&GON);
  wL=(1ULL<<(5*kL))-1; wR=(1ULL<<(5*kR))-1;
  unordered_set<u64> SL,SR; set<tuple<int,int,u64,u64>> Cs; unordered_set<u64> Ch;
  auto ck=[&](int q,int m,u64 a,u64 b){ u64 h=a*0x9E3779B97F4A7C15ULL^(b+0x632BE59BD9B4E019ULL+(a<<6)+(b>>2)); return h^((u64)q<<1|m); };
  vector<tuple<int,int,u64,u64>> CL;
  while(fscanf(f,"%s",tag)==1){
    if(tag[0]=='S'){int sd; unsigned long long s; fscanf(f,"%d %llu",&sd,&s); (sd?SR:SL).insert(s);}
    else {int q,m; unsigned long long a,b; fscanf(f,"%d %d %llu %llu",&q,&m,&a,&b); CL.push_back({q,m,a,b});}
  }
  set<tuple<int,int,u64,u64>> C(CL.begin(),CL.end());
  for(int g=0;g<256;g++) for(int x=0;x<2;x++){int r=0; for(int X=0;X<8;X++){T t=TMX[X][x]; if(!t.ok||(t.d==1&&((g>>t.n)&1))) r|=1<<X;} GT[g][x]=r;}
  int g=0; for(int it=0;it<64;it++) g=GT[g][0]; u64 zL=0,zR=(u64)g<<55;
  long long N=atoll(argv[2]);
  // tape of codes; stacks of chain states
  long long SZ=1LL<<24; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=0;
  vector<u64> LS{zL}, RS{zR};  // top = state of the side adjacent to the head
  // right stack must hold states for the right side: initially blank
  long long st=0, maxlen=0;
  for(;st<N;st++){
    int m=tape[p]&1;
    if(!C.count({q,m,LS.back(),RS.back()})){ printf("NOT COVERED at step %lld state %c%d\n",st,'A'+q,m); return 1; }
    T t=TMX[q][m]; if(!t.ok){ printf("HALT at %lld\n",st); return 1; }
    int code=t.w+2*(1+q);
    tape[p]=code;
    if(t.d==1){ // fold into left, unfold right
      if(!SL.count(LS.back())){ printf("fold of unlearned L state at %lld\n",st); return 1; }
      LS.push_back(foldL(LS.back(),code));
      if(RS.size()>1) RS.pop_back();  // else right side stays blank (z)
      p++;
    } else {
      if(!SR.count(RS.back())){ printf("fold of unlearned R state at %lld\n",st); return 1; }
      RS.push_back(foldR(RS.back(),code));
      if(LS.size()>1) LS.pop_back();
      p--;
    }
    q=t.n;
    if(p<10||p>SZ-10){printf("EDGE\n");return 1;}
    maxlen=max(maxlen,(long long)(LS.size()+RS.size()));
  }
  printf("OK: %lld steps covered, max tape %lld\n",st,maxlen);
}
