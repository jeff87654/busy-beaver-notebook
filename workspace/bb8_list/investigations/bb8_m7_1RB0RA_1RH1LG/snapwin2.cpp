// snapwin MACHINE word state N1 N2 : print raw bit string of tape for each B-at-frontier snapshot with step in [N1,N2]; at the end print final tape info
#include <bits/stdc++.h>
using namespace std;
struct T{int w,d,n;bool ok;};
int main(int argc,char**argv){
  string ms=argv[1];
  T tm[8][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<29; vector<uint8_t> tape(SZ,0); long long p=SZ/2; int q=argv[3][0]-'A';
  string w=argv[2]; long long N1=atoll(argv[4]),N2=atoll(argv[5]); long long stride=argc>6?atoll(argv[6]):1; long long cnt=0; string lastsnap,lastsnap2;
  for(size_t i=0;i<w.size();i++) tape[p-w.size()+i]=w[i]-'0';
  long long mn=p-w.size(),mx=p;
  for(long long st=0;st<N2;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld state %c head %lld ones: ", st, 'A'+q, p-SZ/2); long long ones=0; for(long long i=mn;i<=mx;i++) ones+=tape[i]; printf("%lld span %lld\n",ones,mx-mn+1); 
       for(long long i=mn;i<=mx;i++) putchar('0'+tape[i]); putchar('\n'); return 0;}
    tape[p]=t.w; if(t.w){ mn=min(mn,p); mx=max(mx,p);} 
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(st<N1) continue;
    if(q!=1||tape[p]) continue;
    while(mx>=p && !tape[mx]) --mx; 
    if(mx>=p) continue;
    while(mn<p && !tape[mn]) ++mn;
    cnt++; if(stride<0){ lastsnap2=lastsnap; lastsnap=to_string(st+1)+" "; for(long long i=mn;i<p;i++) lastsnap.push_back('0'+tape[i]); continue;} if(cnt%stride) continue;
    printf("%lld ", st+1); for(long long i=mn;i<p;i++) putchar('0'+tape[i]); putchar('\n');
  }
  if(stride<0){ printf("%s
%s
",lastsnap2.c_str(),lastsnap.c_str()); }
  printf("end state %c head %lld mn %lld mx %lld\n",'A'+q,p-SZ/2,mn-SZ/2,mx-SZ/2);
}
