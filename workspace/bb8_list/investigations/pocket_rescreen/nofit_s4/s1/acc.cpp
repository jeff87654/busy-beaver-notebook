// acc MACHINE MIRROR(0/1) MAXEVENTS Q PRE A MID B DA DB MINY   (PRE/MID may be -)
// Literal simulation (machine mirrored if MIRROR=1, so the accelerated side is always L), with acceleration:
// at an event (state Q, head on leftmost visited cell, blank) where the tape right of head reads PRE A^x B^y T with y>=MINY,
// jump k=y-MINY+1 bouncer passes: x+=DA*k, y+=DB*k (DB must be -1). Prints each acceleration: "ACC n x y | tail(compressed,<=300 chars)",
// and HALT. Steps are not counted during jumps (only literal steps). Tape is a deque-like vector with origin shift.
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int W[16][2], M[16][2], N_[16][2];
void parse(const string&s,bool mir){size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W[q][b]=-1;M[q][b]=0;N_[q][b]=-1;} else {W[q][b]=s[i]-'0';M[q][b]=(s[i+1]=='R'?1:-1)*(mir?-1:1);N_[q][b]=s[i+2]-'A';} i+=3;}
 q++; if(i<s.size()&&s[i]=='_')i++;}}
string comp(const string& t){ string o; size_t i=0,n=t.size();
 while(i<n){ int bp=0,bk=0; size_t bc=0;
  for(int p=1;p<=12&&i+p<=n;p++){ size_t k=1; while(i+(k+1)*p<=n && t.compare(i+k*p,p,t,i,p)==0)k++; if(k>=3 && k*p>bc){bc=k*p;bp=p;bk=k;} }
  if(bk>=3 && bc>=6){ string blk=t.substr(i,bp); o+=(bp==1?blk:"("+blk+")")+"^"+to_string(bk)+" "; i+=bc; } else { o+=t[i]; i++; } } return o;}
int main(int argc,char**argv){ SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 bool mir=atoi(argv[2]); parse(argv[1],mir); long long maxev=atoll(argv[3]); int Q=argv[4][0]-'A';
 string PRE=argv[5],A=argv[6],MID=argv[7],B=argv[8]; long long DA=atoll(argv[9]),DB=atoll(argv[10]),MINY=atoll(argv[11]); if(MID=="-")MID="";
 if(PRE=="-")PRE="";
 vector<unsigned char> tp(1<<22,0); long long p=1<<21, mn=p, mx=p; int q=0; long long steps=0, nacc=0;
 auto at=[&](long long i)->unsigned char&{ if(i<0||i>=(long long)tp.size()){ fprintf(stderr,"tape\n"); exit(1);} return tp[i]; };
 while(nacc<maxev){
  int s=tp[p]; if(W[q][s]<0){ long long ones=0; for(long long x=mn;x<=mx;x++)ones+=tp[x]; printf("HALT literal_steps %lld ones %lld span %lld\n",steps,ones,mx-mn+1); return 0;}
  tp[p]=W[q][s]; p+=M[q][s]; q=N_[q][s]; steps++; if(p<mn)mn=p; if(p>mx)mx=p;
  if(p<4||p+8>(long long)tp.size()){ // grow
    long long add=tp.size(); vector<unsigned char> nt(tp.size()*2,0); copy(tp.begin(),tp.end(),nt.begin()+add/2); p+=add/2;mn+=add/2;mx+=add/2; tp.swap(nt); }
  if(q==Q && p==mn && tp[p]==0){
    long long i=p; bool ok=true; for(char c:PRE){ if(i>mx+1||tp[i]!=c-'0'){ok=false;break;} i++; }
    if(!ok) continue;
    long long x=0,y=0; auto match=[&](long long j,const string&w){ for(size_t k=0;k<w.size();k++) if(j+(long long)k>mx||tp[j+k]!=w[k]-'0') return false; return true; };
    while(match(i,A)){x++;i+=A.size();} if(!match(i,MID)) continue; i+=MID.size(); while(match(i,B)){y++;i+=B.size();}
    if(getenv("DBG")) fprintf(stderr,"ev %lld x %lld y %lld\n",steps,x,y);
    if(y<MINY) continue;
    long long k=y-MINY+1; long long nx=x+DA*k, ny=y+DB*k;
    string tail; for(long long j=i;j<=mx;j++) tail+=char('0'+tp[j]); while(!tail.empty()&&tail.back()=='0')tail.pop_back();
    long long newlen=PRE.size()+nx*A.size()+MID.size()+ny*B.size()+tail.size();
    long long need=p+newlen+16; if(need>=(long long)tp.size()){ vector<unsigned char> nt(need*2,0); copy(tp.begin(),tp.end(),nt.begin()); tp.swap(nt);} 
    long long j=p+PRE.size(); for(long long t=0;t<nx;t++)for(char c:A)tp[j++]=c-'0'; for(char c:MID)tp[j++]=c-'0'; for(long long t=0;t<ny;t++)for(char c:B)tp[j++]=c-'0';
    for(char c:tail)tp[j++]=c-'0'; for(long long z=j;z<=mx;z++)tp[z]=0; mx=max(j,p);
    nacc++; string ct=comp(tail); if(ct.size()>300) ct=ct.substr(0,300)+"..."; printf("ACC %lld lsteps %lld x %lld y %lld k %lld | %s\n",nacc,steps,x,y,k,ct.c_str()); fflush(stdout);
  }
 }
}
