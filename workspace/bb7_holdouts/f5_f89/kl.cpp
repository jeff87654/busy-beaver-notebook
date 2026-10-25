// kl MACHINE MAXSTEPS Q SIDE MODE [TAPE] : at (Q,SIDE) end events print compressed u-token list of tape.
// tokens: maximal (U)^n -> n ; leftover cells shown as '.'(0) or '#'(1).  U given via env U (default 10). side L: left->right; R: right->left reading
// MODE: a = all events; z = only events whose first token after leading zeros is not a number>0 or that follow such; p<k> = every k-th
#include <bits/stdc++.h>
using namespace std; typedef long long ll;
int W[16][2],D[16][2],N[16][2];
void parse(const string&m){ size_t i=0; int q=0; while(i<m.size()){ for(int s=0;s<2;s++){ string t=m.substr(i,3); i+=3;
  if(t[2]=='-'){W[q][s]=1;D[q][s]=1;N[q][s]=-1;} else {W[q][s]=t[0]-'0';D[q][s]=t[1]=='R'?1:-1;N[q][s]=t[2]-'A';}} q++; if(i<m.size()&&m[i]=='_')i++;} }
vector<unsigned char> T; ll pos,lo,hi; int q; string U="10";
void grow(){ ll add=max<ll>(T.size(),1<<16); vector<unsigned char> n(T.size()+2*add,0); memcpy(&n[add],T.data(),T.size()); T.swap(n); pos+=add; lo+=add; hi+=add; }
string dec(char side){
  string s; if(side=='L') for(ll i=lo;i<=hi;i++) s+=char('0'+T[i]); else for(ll i=hi;i>=lo;i--) s+=char('0'+T[i]);
  size_t a=s.find('1'), b=s.rfind('1'); if(a==string::npos) return "(blank)";
  s=s.substr(a,b-a+1); vector<string> tk; size_t i=0; size_t u=U.size();
  while(i<s.size()){ ll n=0; while(s.compare(i,u,U)==0 && i+u<=s.size()){n++; i+=u;} if(n){tk.push_back(to_string(n)); continue;} tk.push_back(s[i]=='0'?".":"#"); i++; }
  // compress repeats of (num .) pairs
  string out; size_t k=0; while(k<tk.size()){ size_t j=k; // try pattern of length 2 repeating
    if(k+3<tk.size() && tk[k+1]=="." && isdigit(tk[k][0])){ size_t r=1; while(k+2*r+1<tk.size() && tk[k+2*r]==tk[k] && tk[k+2*r+1]==".") r++; if(r>=3){ out+="("+tk[k]+" .)^"+to_string(r)+" "; k+=2*r; continue;} }
    out+=tk[k]+" "; k++; }
  return out; }
void init(const string&tp){ T.assign(1<<16,0); pos=1<<15; lo=hi=pos; q=0; if(tp.empty()) return; ll p=pos; bool h=false;
  for(char c:tp){ if(c>='A'&&c<='P'){ q=c-'A'; pos=p; h=true; continue;} T[p]=c-'0'; p++; } lo=1<<15; hi=max<ll>(p-1,pos); }
int main(int argc,char**argv){ parse(argv[1]); ll maxs=atoll(argv[2]); int fq=argv[3][0]-'A'; char fs=argv[4][0]; string mode=argv[5];
  if(getenv("U")) U=getenv("U"); init(argc>6?argv[6]:""); ll ev=0; ll every=1; if(mode[0]=='p') every=atoll(mode.c_str()+1);
  string prev; ll prevst=0; bool wantnext=false;
  for(ll st=0;st<maxs;st++){ int s=T[pos]; if(N[q][s]<0){ printf("HALT %lld state %c\n",st+1,'A'+q); return 0;}
    T[pos]=W[q][s]; pos+=D[q][s]; q=N[q][s]; if(pos<=0||pos>=(ll)T.size()-1) grow();
    char side=0; if(pos<lo){lo=pos;side='L';} else if(pos>hi){hi=pos;side='R';}
    if(side==fs && q==fq){ ev++;
      if(mode=="a" || (mode[0]=='p' && ev%every==0)) { printf("%lld %s\n",st+1,dec(side).c_str()); fflush(stdout);} 
      else if(mode=="z"){ string d=dec(side); bool odd = !(d.size()>2 && isdigit(d[0]) && d.find(" . ")!=string::npos && d.find(" . ")< d.find(' ')+1 && d.compare(d.find(' ')+3,2,". ")!=0);
        if(odd||wantnext){ if(!wantnext) printf("%lld %s\n",prevst,prev.c_str()); printf("%lld %s\n--\n",st+1,d.c_str()); fflush(stdout);} wantnext=odd; prev=d; prevst=st+1; } } }
  printf("LIMIT ev=%lld span=%lld\n",ev,hi-lo+1); return 0; }
