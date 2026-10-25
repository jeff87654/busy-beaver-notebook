// bfront MACHINE WORD STATE N EVERY : run; print the tape (run notation) whenever the head is in state B on the blank right end, every EVERY-th time
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1]; long long N=atoll(argv[4]); long long EV=atoll(argv[5]);
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<24; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2]; if(w=="-") w="";
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mx=p-1, mn=p-(long long)w.size(); long long cnt=0;
  for(long long st=0;st<N;st++){
    if(p>mx) mx=p; if(p<mn) mn=p;
    if(q==1 && p>=mx && tape[p]==0){ // B at right end
      bool blankright=true; 
      if(cnt++%EV==0){
        // run notation from mn to p-1
        string out; long long i=mn; while(i<p && tape[i]==0) i++;
        while(i<p){ long long j=i; while(j<p&&tape[j]==1) j++; long long ones=j-i; long long z=0; while(j<p&&tape[j]==0){j++;z++;}
          if(j>=p && z==0) out+=to_string(ones)+". "; else if(z==1) out+=to_string(ones)+" "; else if(z==2) out+=to_string(ones)+"| "; else out+=to_string(ones)+"|"+to_string(z)+" ";
          i=j; }
        printf("%lld: %s\n",st,out.c_str());
      }
    }
    T&t=tm[q][tape[p]]; if(!t.ok){printf("HALT %lld\n",st);return 0;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<10||p>SZ-10){printf("EDGE\n");return 0;}
  }
}
