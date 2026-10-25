// g0ctx MACHINE RUNSPEC N : histogram of local contexts when G reads 0 (window -6..+8 around head, plus distance to right end of tape)
#include "runs.h"
struct T{int w,d,n;bool ok;};
static string parse_tok(const string& t){ size_t bar=t.find('|'); string o=t, z="1"; bool dot=false;
  if(!t.empty()&&t.back()=='.'){ o=t.substr(0,t.size()-1); dot=true; }
  else if(bar!=string::npos){ o=t.substr(0,bar); string rest=t.substr(bar+1); if(rest.empty()) z="2"; else { z=rest.substr(0,rest.size()-1);} }
  string r(atoll(o.c_str()),'1'); if(!dot) r+=string(atoll(z.c_str()),'0'); return r; }
static void skipws(const string&s,size_t&i){ while(i<s.size()&&s[i]==' ')++i; }
static string parse_seq(const string&s,size_t&i){ string out; skipws(s,i);
  while(i<s.size()&&s[i]!=')'){ string unit;
    if(s[i]=='('){ ++i; unit=parse_seq(s,i); ++i; }
    else { size_t j=i; while(j<s.size()&&s[j]!=' '&&s[j]!='^'&&s[j]!=')')++j; unit=parse_tok(s.substr(i,j-i)); i=j; }
    long long k=1; if(i<s.size()&&s[i]=='^'){ ++i; size_t j=i; while(j<s.size()&&isdigit(s[j]))++j; k=atoll(s.substr(i,j-i).c_str()); i=j; }
    for(long long c=0;c<k;c++) out+=unit; skipws(s,i); }
  return out; }
int main(int argc,char**argv){
  string ms=argv[1]; string spec=argv[2]; long long N=atoll(argv[3]); int watch=argc>4? argv[4][0]-'A' : 6; int wsym=argc>5?atoi(argv[5]):0;
  size_t ii=0; string w=parse_seq(spec,ii); while(!w.empty()&&w.back()=='0') w.pop_back();
  int q=1;
  T tm[16][2]; {int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;}}
  long long SZ=1LL<<30; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+(long long)w.size(), mn=off, mx=p; map<string,pair<long long,long long>> H;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(!t.ok){ printf("HALT at step %lld\n",st); break; }
    if(q==watch&&c==wsym){ string s; for(int d=-6;d<=8;d++){ if(d==0) s+='['; s+=char('0'+tape[p+d]); if(d==0) s+=']'; }
      long long b=mx; while(b>p&&!tape[b])--b; s+="  dR="+to_string(b-p>20?20:b-p); auto&e=H[s]; if(!e.first) e.second=st; e.first++; }
    tape[p]=t.w; p+=t.d; q=t.n; if(p<mn) mn=p; if(p>mx) mx=p;
  }
  for(auto&kv:H) printf("%10lld first@%lld  %s\n",kv.second.first,kv.second.second,kv.first.c_str());
}
