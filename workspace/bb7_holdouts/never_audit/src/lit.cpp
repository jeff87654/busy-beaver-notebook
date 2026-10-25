// lit.cpp (never_audit): plain literal TM simulator for coding discovery, lockstep and exhaustion finding.
// lit ends MACHINE MAXSTEPS STATE(*|A..) SIDE(L|R|*) MAXEV [TAPE]   -- print "step q side RLE" at end events
//   end event = head moves onto a cell outside the visited span.  RLE of the visited span, head marked [Qb].
// lit kx MACHINE MAXSTEPS Q SIDE NZMAX MAXPRINT  -- (Q,SIDE) end events whose tape has <= NZMAX runs of 1s
// lit kv MACHINE MAXSTEPS Q SIDE EVERY [TAPE]  -- v-lists (1-runs split by single 0s, oriented head-last) at (Q,SIDE)
//   end events; prints every EVERY-th event (1 = all) as "step v1 v2 ..." with repeats compressed "x*n".
// lit sig MACHINE MAXSTEPS  -- hash of (side, ones) sequence at end events + used transitions
// lit run MACHINE MAXSTEPS [TAPE]   -- run, print HALT steps ones / LIMIT with final RLE
// TAPE: string of 0/1 with one state letter marking the head (letter placed before the head cell), e.g. "0110C1011"
#include <bits/stdc++.h>
using namespace std; typedef long long ll;
int W[16][2],D[16][2],N[16][2]; int NS;
bool parse(const string&m){ NS=0; size_t i=0; int q=0; while(i<m.size()){ for(int s=0;s<2;s++){ string t=m.substr(i,3); i+=3;
  if(t[2]=='-'){W[q][s]=1;D[q][s]=1;N[q][s]=-1;} else {W[q][s]=t[0]-'0';D[q][s]=t[1]=='R'?1:-1;N[q][s]=t[2]-'A';}} q++; if(i<m.size()&&m[i]=='_')i++;} NS=q; return true;}
vector<unsigned char> T; ll pos,lo,hi; int q;
void grow(){ ll add=max<ll>(T.size(),1<<16); vector<unsigned char> n(T.size()+2*add,0); memcpy(&n[add],T.data(),T.size()); T.swap(n); pos+=add; lo+=add; hi+=add; }
string rle(ll a,ll b){ string s; ll i=a; int runs=0; while(i<=b){ ll j=i; while(j<=b&&T[j]==T[i]&&j!=pos)j++; if(j==i){
      s+="["; s+=char('A'+q); s+=char('0'+T[i]); s+="] "; i++; continue;}
    if(j-i==1) s+=char('0'+T[i]); else { s+=char('0'+T[i]); s+="^"+to_string(j-i);} s+=" "; i=j; if(++runs>200000){s+="...";break;} }
  return s;}
void init(const string&tp){ T.assign(1<<16,0); pos=1<<15; lo=hi=pos; q=0; if(tp.empty()) return; ll p=pos; bool h=false;
  for(char c:tp){ if(c>='A'&&c<='P'){ q=c-'A'; pos=p; h=true; continue;} T[p]=c-'0'; p++; } if(!h) pos=1<<15; lo=1<<15; hi=max<ll>(p-1,pos); }
string vl(char side){ // v-list of visited span oriented so the head side is last
  vector<ll> v; ll cur=0; bool started=false; int zeros=0;
  auto feed=[&](int c){ if(c==1){ if(started&&zeros>=1){ v.push_back(cur); for(int z=1;z<zeros;z++) v.push_back(0); cur=0;} started=true; zeros=0; cur++; } else { if(started) zeros++; } };
  if(side=='R') for(ll i=lo;i<=hi;i++) feed(T[i]); else for(ll i=hi;i>=lo;i--) feed(T[i]);
  if(started) v.push_back(cur);
  int tz=zeros-1;
  string s; size_t i=0; while(i<v.size()){ size_t j=i; while(j<v.size()&&v[j]==v[i]) j++; s+=" "+to_string(v[i]); if(j-i>1) s+="*"+to_string(j-i); i=j; }
  s+=" |"+to_string(tz); return s; }
int main(int argc,char**argv){ string mode=argv[1]; parse(argv[2]); ll maxs=atoll(argv[3]);
  if(mode=="ends"){ int fq=argv[4][0]=='*'?-1:argv[4][0]-'A'; char fs=argv[5][0]; ll maxev=atoll(argv[6]); init(argc>7?argv[7]:"");
    ll ev=0; for(ll st=0;st<maxs;st++){ int s=T[pos]; if(N[q][s]<0){ printf("HALT %lld\n",st+1); return 0;}
      T[pos]=W[q][s]; pos+=D[q][s]; q=N[q][s]; if(pos<=0||pos>=(ll)T.size()-1) grow();
      char side=0; if(pos<lo){lo=pos;side='L';} else if(pos>hi){hi=pos;side='R';}
      if(side && (fq<0||fq==q) && (fs=='*'||fs==side)){ printf("%lld %c %c %s\n",st+1,'A'+q,side,rle(lo,hi).c_str()); if(++ev>=maxev) return 0; } }
    printf("LIMIT\n"); return 0; }
  if(mode=="kx"){ int fq=argv[4][0]-'A'; char fs=argv[5][0]; ll nzmax=atoll(argv[6]), maxp=atoll(argv[7]); init("");
    ll runs=0, ev=0, pr=0; auto st1=[&](ll i){ return (T[i]==1 && T[i-1]==0)?1:0; };
    for(ll st=0;st<maxs;st++){ int s=T[pos]; if(N[q][s]<0){ printf("HALT %lld\n",st+1); return 0;}
      if(W[q][s]!=s){ runs-=st1(pos)+st1(pos+1); T[pos]=W[q][s]; runs+=st1(pos)+st1(pos+1); }
      pos+=D[q][s]; q=N[q][s]; if(pos<=1||pos>=(ll)T.size()-2) grow();
      char side=0; if(pos<lo){lo=pos;side='L';} else if(pos>hi){hi=pos;side='R';}
      if(side==fs && q==fq){ ev++; if(runs<=nzmax && pr<maxp){ pr++; printf("%lld %c %c %s\n",st+1,'A'+q,side,rle(lo,hi).c_str()); fflush(stdout);} } }
    printf("LIMIT ev=%lld runs=%lld span=%lld\n",ev,runs,hi-lo+1); return 0; }
  if(mode=="kv"){ int fq=argv[4][0]-'A'; char fs=argv[5][0]; ll every=atoll(argv[6]); init(argc>7?argv[7]:"");
    ll ev=0; for(ll st=0;st<maxs;st++){ int s=T[pos]; if(N[q][s]<0){ printf("HALT %lld\n",st+1); return 0;}
      T[pos]=W[q][s]; pos+=D[q][s]; q=N[q][s]; if(pos<=0||pos>=(ll)T.size()-1) grow();
      char side=0; if(pos<lo){lo=pos;side='L';} else if(pos>hi){hi=pos;side='R';}
      if(side==fs && q==fq){ if(ev%every==0) printf("%lld%s\n",st+1,vl(side).c_str()); ev++; } }
    printf("LIMIT ev=%lld\n",ev); return 0; }
  if(mode=="sig"){ init(""); ll ones=0; unsigned long long h1=1469598103934665603ULL,h2=h1; int used[16][2]={{0}}; ll ev=0; ll st;
    for(st=0;st<maxs;st++){ int s=T[pos]; used[q][s]=1; if(N[q][s]<0){ break;}
      ones+=W[q][s]-s; T[pos]=W[q][s]; pos+=D[q][s]; q=N[q][s]; if(pos<=0||pos>=(ll)T.size()-1) grow();
      int side=0; if(pos<lo){lo=pos;side=1;} else if(pos>hi){hi=pos;side=2;}
      if(side){ ev++; h1=(h1^(unsigned long long)(ones*4+side))*1099511628211ULL; h2=(h2^(unsigned long long)(ones*4+3-side))*1099511628211ULL; } }
    string u; for(int a=0;a<NS;a++)for(int b=0;b<2;b++) u+=used[a][b]?'1':'0';
    printf("%s %016llx %lld %lld %s %s\n", argv[2], min(h1,h2), ev, ones, u.c_str(), st<maxs?"HALT":"RUN"); return 0; }
  if(mode=="run"){ init(argc>4?argv[4]:""); for(ll st=0;st<maxs;st++){ int s=T[pos]; if(N[q][s]<0){ ll ones=0; for(ll i=lo;i<=hi;i++) ones+=T[i]; printf("HALT %lld ones=%lld\n",st+1,ones+1-T[pos]); return 0;}
      T[pos]=W[q][s]; pos+=D[q][s]; q=N[q][s]; if(pos<=0||pos>=(ll)T.size()-1) grow(); if(pos<lo)lo=pos; if(pos>hi)hi=pos; }
    printf("LIMIT %s\n", rle(lo,hi).c_str()); return 0; }
}
