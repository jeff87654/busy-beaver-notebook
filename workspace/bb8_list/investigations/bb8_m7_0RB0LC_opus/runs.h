// run-structure printer: tape -> list of (ones, zeros-after) pairs, printed as tokens, with periodic compression
#include <bits/stdc++.h>
using namespace std;
static string pairtok(long long o,long long z){ string s=to_string(o); if(z==1) return s; if(z==0) return s+"."; if(z==2) return s+"|"; return s+"|"+to_string(z)+"|"; }
static string runs(const vector<uint8_t>&t,long long lo,long long hi){
  vector<string> R;
  long long i=lo;
  while(i<=hi){ long long j=i; while(j<=hi&&t[j]==1)++j; long long o=j-i; long long k=j; while(k<=hi&&t[k]==0)++k; R.push_back(pairtok(o,k-j)); i=k; }
  string out; size_t a=0;
  while(a<R.size()){
    int bestp=0; long long bestc=1;
    for(int p=1;p<=4;p++){ long long c=1; while(a+(c+1)*p<=R.size()){ bool eq=true; for(int q=0;q<p;q++) if(R[a+c*p+q]!=R[a+q]){eq=false;break;} if(!eq)break; ++c; }
      if(c>=2 && c*p>bestc*max(bestp,1) && (c>=3||p==1)){ bestp=p; bestc=c; } }
    if(bestp){ string u; for(int q=0;q<bestp;q++){ if(q) u+=" "; u+=R[a+q]; }
      if(bestp==1 && u.find('|')==string::npos && u.find('.')==string::npos) out+=u+"^"+to_string(bestc)+" "; else out+="("+u+")^"+to_string(bestc)+" ";
      a+=bestc*bestp; continue; }
    out+=R[a]+" "; ++a;
  }
  return out;
}
