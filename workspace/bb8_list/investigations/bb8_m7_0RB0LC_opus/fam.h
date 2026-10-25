// family parser for B-frontier tapes: Q | list segment = D(t1)..D(tk) (10)^r 1^h | tail segments (pure 1-runs)
#include "spec.h"
struct Fam { bool ok=false; string Q; long long gap=0; vector<long long> toks; long long r=0, h=0; vector<long long> tail; };
static string compress_list(const vector<long long>&v){ string s; size_t i=0; while(i<v.size()){ size_t j=i; while(j<v.size()&&v[j]==v[i])++j; if(!s.empty()) s+=","; s+=to_string(v[i]); if(j-i>1) s+="^"+to_string(j-i); i=j; } return s; }
static Fam parse_fam(const vector<uint8_t>&t,long long lo,long long hi){
  Fam f; // lo..hi = first1..last1
  // find segments separated by >=2 zeros, from the right
  long long e=hi; vector<long long> tail;
  while(true){
    // segment ending at e: go left until a 00 or lo-1
    long long s=e; bool has0=false;
    while(s-1>=lo && !(t[s-1]==0 && s-2>=lo && t[s-2]==0) ){ if(t[s-1]==0) has0=true; --s; if(s-1>=lo && t[s-1]==0 && (s-2<lo || t[s-2]==0)) break; }
    // now [s..e] is the segment (may start with ... ) ; s is first cell after zeros
    while(s<=e && t[s]==0) ++s;
    has0=false; for(long long k=s;k<=e;k++) if(!t[k]) {has0=true;break;}
    if(!has0){ tail.push_back(e-s+1); long long z=s-1; if(z<lo) return f; while(z>=lo&&t[z]==0) --z; if(z<lo) return f; e=z; continue; }
    // list segment [s..e]
    long long h=0; while(e-h>=s && t[e-h]==1) ++h;
    long long ee=e-h; // t[ee]==0
    vector<long long> toks; long long cur=0; long long k=s;
    while(k<=ee){ if(t[k]==1 && k+1<=ee && t[k+1]==0){ cur++; k+=2; } else if(t[k]==1){ toks.push_back(cur); cur=0; k+=1; } else return f; }
    f.ok=true; f.toks=toks; f.r=cur; f.h=h; reverse(tail.begin(),tail.end()); f.tail=tail;
    long long qe=s-1; while(qe>=lo&&t[qe]==0) --qe; f.Q = qe>=lo? runs(t,lo,qe) : string(""); f.gap = qe>=lo? (s-1-qe) : 0;
    return f;
  }
}
static string fam_str(const Fam&f){ if(!f.ok) return "?"; string s="Q["+f.Q+"] g="+to_string(f.gap)+" T["+compress_list(f.toks)+"] r="+to_string(f.r)+" h="+to_string(f.h)+" tail["+compress_list(f.tail)+"]"; return s; }
