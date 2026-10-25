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
static string spec_word(const string&spec){ size_t i=0; string w=parse_seq(spec,i); while(!w.empty()&&w.back()=='0') w.pop_back(); return w; }
static void load_tm(const string&ms, T tm[16][2]){ int i=0; stringstream ss(ms); string r; while(getline(ss,r,'_')){ for(int c=0;c<2;c++){string t=r.substr(3*c,3); if(t=="---") tm[i][c]={0,0,0,false}; else tm[i][c]={t[0]-'0',t[1]=='R'?1:-1,t[2]-'A',true};} i++;} }
