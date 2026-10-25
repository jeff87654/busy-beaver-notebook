// tshape MACHINE RUNSPEC N [maxlen] : start from a run-spec tape, head in B on the blank right of the word;
// print the run structure at B-frontier snapshots whenever the SHAPE (numbers -> #) changes; also the first/last of each shape run.
// RUNSPEC: space separated tokens: "o" (o ones + one 0), "o|" (o ones + 00), "o|z|" (o ones + z zeros), "o." (o ones, no zero),
//          "X^k" (k copies of token X), "(A B ...)^k" (group repeated).  The word is trimmed of trailing zeros; head = len(word)+1? no: head on the cell right after the last char.
#include "runs.h"
struct T{int w,d,n;bool ok;};
static void expand(const string& s, size_t& i, string& out);
static string parse_tok(const string& t){ // single token without ^
  size_t bar=t.find('|'); string o=t, z="1"; bool dot=false;
  if(!t.empty()&&t.back()=='.'){ o=t.substr(0,t.size()-1); dot=true; }
  else if(bar!=string::npos){ o=t.substr(0,bar); string rest=t.substr(bar+1); if(rest.empty()) z="2"; else { z=rest.substr(0,rest.size()-1);} }
  string r(atoll(o.c_str()),'1'); if(!dot) r+=string(atoll(z.c_str()),'0'); return r; }
static void skipws(const string&s,size_t&i){ while(i<s.size()&&s[i]==' ')++i; }
static string parse_seq(const string&s,size_t&i){ string out; skipws(s,i);
  while(i<s.size()&&s[i]!=')'){
    string unit;
    if(s[i]=='('){ ++i; unit=parse_seq(s,i); if(s[i]!=')'){fprintf(stderr,"bad spec\n");exit(2);} ++i; }
    else { size_t j=i; while(j<s.size()&&s[j]!=' '&&s[j]!='^'&&s[j]!=')')++j; unit=parse_tok(s.substr(i,j-i)); i=j; }
    long long k=1; if(i<s.size()&&s[i]=='^'){ ++i; size_t j=i; while(j<s.size()&&isdigit(s[j]))++j; k=atoll(s.substr(i,j-i).c_str()); i=j; }
    for(long long c=0;c<k;c++) out+=unit; skipws(s,i); }
  return out; }
static string shape(const string&r){ string s; bool num=false; for(char c:r){ if(isdigit(c)){ if(!num) s+='#'; num=true;} else {s+=c; num=false;} } return s; }
int main(int argc,char**argv){
  string ms=argv[1]; string spec=argv[2]; long long N=atoll(argv[3]); size_t maxlen=argc>4?atoll(argv[4]):400;
  size_t ii=0; string w=parse_seq(spec,ii); while(!w.empty()&&w.back()=='0') w.pop_back();
  int q=1;
  T tm[16][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<30; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+(long long)w.size(), mn=off, mx=p; long long cnt=0; string prevshape, prevline;
  printf("start %s\n",runs(tape,off,off+w.size()-1).c_str());
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b;
      if(!prevline.empty()) printf("%s\n",prevline.c_str());
      printf("HALT at step %lld state %c head %lld (rel to right end %lld) | %s\n",st,'A'+q,p-off,p-b,runs(tape,a,b).c_str()); return 0;}
    tape[p]=t.w; p+=t.d; q=t.n; if(p<mn) mn=p; if(p>mx) mx=p;
    if(p<100||p>SZ-100){printf("EDGE %lld\n",st);return 0;}
    if(q!=1||tape[p]) continue;
    if(p<mx) continue;
    ++cnt; long long a=mn,b=mx; while(a<b&&!tape[a])++a; while(b>a&&!tape[b])--b;
    string r=runs(tape,a,b); string sh=shape(r);
    char buf[64]; snprintf(buf,64,"%lld [%lld] ",st+1,cnt);
    string line=string(buf)+(r.size()>maxlen? r.substr(0,maxlen/2)+" ... "+r.substr(r.size()-maxlen/2):r);
    if(sh!=prevshape){ if(!prevline.empty()&&prevline!="#") printf("  %s\n",prevline.c_str()); printf("%s\n",line.c_str()); prevline="#"; }
    else prevline=line;
    prevshape=sh;
  }
  if(!prevline.empty()&&prevline!="#") printf("  %s\n",prevline.c_str());
  printf("done N=%lld cnt=%lld\n",N,cnt);
}
