// rend MACHINE RUNSPEC N D : collect (state, window of cells [last1-D-4 .. last1+3], head offset) whenever head >= last1 - D; also check internal 000
#include "spec.h"
int main(int argc,char**argv){
  string ms=argv[1]; string w=spec_word(argv[2]); long long N=atoll(argv[3]); int D=atoi(argv[4]);
  T tm[16][2]; load_tm(ms,tm);
  long long SZ=1LL<<28; vector<uint8_t> tape(SZ,0); long long off=SZ/2; for(size_t i=0;i<w.size();i++) tape[off+i]=w[i]-'0';
  long long p=off+(long long)w.size(); int q=1; long long last1=off+w.size()-1; while(!tape[last1])--last1; long long first1=off; while(!tape[first1])++first1;
  map<string,pair<long long,long long>> H; long long z3=0;
  for(long long st=0;st<N;st++){
    int c=tape[p]; T&t=tm[q][c];
    if(p>=last1-D){ string s; s+=char('A'+q); s+=' '; for(long long k=last1-D-4;k<=last1+3;k++){ if(k==p) s+='['; s+=char('0'+tape[k]); if(k==p) s+=']'; } auto&e=H[s]; if(!e.first) e.second=st; e.first++; }
    if(!t.ok){ printf("HALT at step %lld\n",st); break; }
    tape[p]=t.w;
    if(t.w==1){ if(p>last1) last1=p; if(p<first1) first1=p; }
    else if(p==last1){ while(!tape[last1]) --last1; }
    else if(p==first1){ while(!tape[first1]) ++first1; }
    if(t.w==0 && p>first1 && p<last1){ // check for new internal 000 around p
      for(long long k=p-2;k<=p;k++) if(k>first1 && k+2<last1 && !tape[k]&&!tape[k+1]&&!tape[k+2]){ if(z3<10) printf("internal 000 at step %lld pos rel last1 %lld\n",st,k-last1); z3++; break; } }
    p+=t.d; q=t.n;
    if(p<100||p>SZ-100){printf("EDGE\n");return 0;}
  }
  printf("internal000 events: %lld ; distinct right-end contexts: %zu\n",z3,H.size());
  for(auto&kv:H) printf("%12lld %12lld  %s\n",kv.second.first,kv.second.second,kv.first.c_str());
}
