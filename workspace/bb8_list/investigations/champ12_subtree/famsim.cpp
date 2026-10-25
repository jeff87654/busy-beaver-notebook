// famsim: start a machine on a champion-template family configuration and run it literally,
// printing a run-length view of the tape at checkpoints (10^k steps) and on halt.
//   famsim MACHINE "ds;a;b" MAXSTEPS [O Q P u s al be alB beB S]   (default: BB(7) champion template R B 11 10 1 3 1 3 2 111001)
// O = L mirrors the machine (family at the left end).
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string tm=argv[1]; string pr=argv[2]; long long maxs=atoll(argv[3]);
  string O="R",Q="B",P="11",U="10",SP="1",SS="111001"; long long al=3,be=1,alB=3,beB=2;
  if(argc>=14){O=argv[4];Q=argv[5];P=strcmp(argv[6],"-")?argv[6]:"";U=argv[7];SP=argv[8];al=atoll(argv[9]);be=atoll(argv[10]);alB=atoll(argv[11]);beB=atoll(argv[12]);SS=strcmp(argv[13],"-")?argv[13]:"";}
  if(O=="L") for(char&ch:tm){ if(ch=='L')ch='R'; else if(ch=='R')ch='L'; }
  int nx[16][2],wr[16][2],dr[16][2];
  for(int q=0;q<8;q++)for(int c=0;c<2;c++){const char*t=tm.c_str()+7*q+3*c; if(t[2]=='-'||t[2]=='Z'){nx[q][c]=-1;continue;} wr[q][c]=t[0]-'0'; dr[q][c]=t[1]=='R'?1:-1; nx[q][c]=t[2]-'A';}
  vector<string> parts; {stringstream ss(pr); string it; while(getline(ss,it,';')) parts.push_back(it);} while(parts.size()<3) parts.push_back("0");
  vector<long long> ds; if(!parts[0].empty()){stringstream ss(parts[0]); string d; while(getline(ss,d,',')) ds.push_back(atoll(d.c_str()));}
  long long a=atoll(parts[1].c_str()), b=atoll(parts[2].c_str());
  string w=P; auto rep=[&](long long n){for(long long i=0;i<n;i++) w+=U;};
  for(auto d:ds){rep(al*d+be); w+=SP;} rep(al*a+be); w+=SP; rep(alB*b+beB); w+=SS;
  long long N=1<<22; vector<uint8_t> T(N,0); long long off=N/2; long long p=off; long long lo=p, hi=p;
  for(size_t i=0;i<w.size();i++) T[off-w.size()+i]=w[i]-'0'; lo=off-w.size();
  int q=Q[0]-'A'; long long st=0, nextck=1000000;
  auto show=[&](const char*tag){ long long L=lo,H=hi; while(L<H&&!T[L])L++; while(H>L&&!T[H])H--;
    string s; for(long long i=L;i<=H;i++) s+=char('0'+T[i]);
    // RLE of the string in blocks
    string out; size_t i=0; while(i<s.size()){ size_t j=i; while(j<s.size()&&s[j]==s[i]) j++; long long n=j-i; out+= (n>3? string(1,s[i])+"^"+to_string(n)+" " : s.substr(i,n)+" "); i=j; }
    if(out.size()>600) out=out.substr(0,300)+" ... "+out.substr(out.size()-300);
    printf("%s step %lld state %c head %+lld width %lld ones %lld\n  %s\n",tag,st,'A'+q,p-off,H-L+1,(long long)count(T.begin()+L,T.begin()+H+1,1),out.c_str()); fflush(stdout); };
  while(st<maxs){
    int c=T[p]; if(nx[q][c]<0){show("HALT"); return 0;}
    T[p]=wr[q][c]; p+=dr[q][c]; q=nx[q][c]; st++;
    if(p<lo)lo=p; if(p>hi)hi=p;
    if(p<=2||p>=N-3){ // grow
      vector<uint8_t> U(2*N,0); memcpy(U.data()+N/2,T.data(),N); p+=N/2; lo+=N/2; hi+=N/2; off+=N/2; N*=2; T.swap(U);}
    if(st==nextck){show("ck"); nextck*=10;}
  }
  show("END"); return 0;
}
