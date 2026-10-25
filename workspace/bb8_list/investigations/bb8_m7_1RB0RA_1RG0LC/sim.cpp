// sim MACHINE WORD STATE N : literal run; WORD = tape (head on blank just right of it). Prints tape in RLE at the end.
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<26; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2];
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long st=0; bool halted=false;
  for(;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){halted=true;break;}
    tape[p]=t.w; p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);break;}
  }
  long long mn=SZ,mx=0,sig=0; for(long long i=0;i<SZ;i++) if(tape[i]){mn=min(mn,i);mx=max(mx,i);sig++;}
  printf("%s step %lld state %c sigma %lld head %lld span [%lld,%lld]\n",halted?"HALT":"stop",st,'A'+q,sig,p-SZ/2,mn-SZ/2,mx-SZ/2);
  string out; long long lo=min(mn,p), hi=max(mx,p);
  for(long long i=lo;i<=hi;){
    if(i==p){ out+="["+string(1,'A'+q)+"]"+to_string((int)tape[p])+" "; i++; continue;}
    int c=tape[i]; long long j=i; while(j<=hi&&j!=p&&tape[j]==c) j++;
    out+=to_string(c)+"^"+to_string(j-i)+" "; i=j;
  }
  printf("%s\n",out.c_str());
}
