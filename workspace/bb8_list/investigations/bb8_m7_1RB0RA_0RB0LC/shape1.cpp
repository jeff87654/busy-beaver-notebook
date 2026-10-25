// shape1 MACHINE n b N : from K(0^n;0;b), find first B-frontier snapshot of form 11011 (01)^x (10)^y 11 (01)^z 0011111111001001
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
string D(int m){string s; for(int i=0;i<m;i++) s+="10"; return s+"1";}
int main(int argc,char**argv){
  string ms=argv[1]; int n=atoi(argv[2]); long long b=atoll(argv[3]); long long N=atoll(argv[4]);
  T tm[16][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  string w="11"; for(int i=0;i<n;i++) w+=D(1); w+=D(1); for(long long i=0;i<3*b+2;i++) w+="10"; w+="111001";
  long long SZ=1LL<<27; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+w.size(), mn=off, mx=off+w.size()-1; int q=1;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT %lld\n",st); return 0;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<mn) mn=p; if(p>mx) mx=p;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]||p<mx) continue;
    long long a=mn,e=mx; while(a<e&&!tape[a])++a; while(e>a&&!tape[e])--e;
    string s; for(long long i=a;i<=e;i++) s+=char('0'+tape[i]);
    // parse
    const string P="11011", Q="0011111111001001";
    if(s.size()<P.size()+Q.size()+2) continue; if(s.compare(0,5,P)!=0) continue; if(s.compare(s.size()-Q.size(),Q.size(),Q)!=0) continue;
    string m=s.substr(5,s.size()-5-Q.size()); size_t i=0; long long x=0,y=0,z=0;
    while(i+1<m.size()&&m[i]=='0'&&m[i+1]=='1'){i+=2;x++;}
    while(i+1<m.size()&&m[i]=='1'&&m[i+1]=='0'){i+=2;y++;}
    if(!(i+1<m.size()&&m[i]=='1'&&m[i+1]=='1')) continue; i+=2;
    while(i+1<m.size()&&m[i]=='0'&&m[i+1]=='1'){i+=2;z++;}
    if(i!=m.size()) continue;
    printf("n=%d b=%lld step=%lld x=%lld y=%lld z=%lld\n",n,b,st+1,x,y,z); return 0;
  }
  printf("n=%d b=%lld none within %lld\n",n,b,N);
}
