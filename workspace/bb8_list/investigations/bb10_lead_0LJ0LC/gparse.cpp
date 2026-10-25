// gparse: literal simulator; at every event "head on a blank right of all 1s, in state G" prints the tape parsed as
//   1 ((10)^n_1 1) ((10)^n_2 1) ... ((10)^n_m 1)        [far end first]
// i.e. the n-list n_1..n_m, or "PARSEFAIL <rle>" if the word does not match.
//   gparse MACHINE MAXSTEPS [TAPE HEAD STATE] [EVERY=1] [MAXEV=1e9]
// TAPE uses tview's syntax subset: tokens w^n or (..)^n, spaces ignored.
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <functional>
#include <cctype>
using namespace std;
static string expand(const string &spec){
    size_t i=0;
    auto num=[&](size_t &k){ long long v=0; while(k<spec.size()&&isdigit((unsigned char)spec[k])) v=v*10+(spec[k++]-'0'); return v; };
    function<string(size_t&)> seq=[&](size_t &k)->string{ string out; while(k<spec.size()&&spec[k]!=')'){ if(spec[k]==' '){++k;continue;} string u; if(spec[k]=='('){++k;u=seq(k);++k;} else u=string(1,spec[k++]); if(k<spec.size()&&spec[k]=='^'){++k; long long r=num(k); string rep; for(long long z=0;z<r;++z) rep+=u; u=rep;} out+=u;} return out; };
    return seq(i);
}
int main(int argc,char**argv){
    if(argc<3){fprintf(stderr,"usage\n");return 2;}
    string m=argv[1]; int n=(m.size()+1)/7; int W[16][2],D[16][2],NX[16][2];
    for(int q=0;q<n;++q)for(int c=0;c<2;++c){const char*x=m.c_str()+7*q+3*c; if(x[0]=='-'||x[2]=='Z'){NX[q][c]=-1;continue;} W[q][c]=x[0]-'0';D[q][c]=x[1]=='R'?1:-1;NX[q][c]=x[2]-'A';}
    long long maxs=atoll(argv[2]);
    string word; long long head=0; int q=0;
    if(argc>5){ word=expand(argv[3]); head=atoll(argv[4]); q=argv[5][0]-'A'; }
    long long every = argc>6? atoll(argv[6]):1; long long maxev = argc>7? atoll(argv[7]):1000000000LL;
    long long size=1<<22; while(size < (long long)word.size()*4+4096) size*=2;
    vector<unsigned char> t(size,0); long long off=size/2;
    for(size_t i=0;i<word.size();++i) t[off+i]=word[i]=='1';
    long long pos=off+head, lo=off, hi=off+(long long)word.size()-1; if(word.empty()){lo=pos;hi=pos;}
    long long steps=0, ev=0, printed=0;
    while(steps<maxs){
        int c=t[pos];
        if(NX[q][c]<0){ long long ones=0; for(long long i=lo;i<=hi;++i) ones+=t[i]; printf("HALT %lld state %c read %d ones %lld\n",steps,'A'+q,c,ones); return 0; }
        t[pos]=W[q][c]; pos+=D[q][c]; q=NX[q][c]; ++steps;
        if(pos<lo) lo=pos; if(pos>hi) hi=pos;
        if(pos<=1||pos>=size-2){ vector<unsigned char> u(2*size,0); for(long long i=0;i<size;++i) u[i+size/2]=t[i]; pos+=size/2; lo+=size/2; hi+=size/2; off+=size/2; t.swap(u); size*=2; }
        if(q==6 && t[pos]==0){
            // right end? all cells right of pos are 0 within [pos+1,hi]
            bool rend=true; for(long long i=pos+1;i<=hi;++i) if(t[i]){rend=false;break;}
            if(!rend) continue;
            ++ev; if(ev%every) continue;
            long long L=lo; while(L<pos && !t[L]) ++L;
            // parse
            string out; bool ok=true; long long i=L;
            if(i>=pos||t[i]!=1) ok=false; else ++i;
            vector<long long> ns;
            while(ok && i<pos){ long long k=0; while(i+1<pos && t[i]==1 && t[i+1]==0){k++; i+=2;} if(i<pos && t[i]==1){ ns.push_back(k); ++i;} else {ok=false;} }
            if(ok){ printf("%lld G %zu |",steps,ns.size()); for(auto v:ns) printf(" %lld",v); printf("\n"); }
            else { printf("%lld G PARSEFAIL |",steps); for(long long j=L;j<pos;++j) putchar('0'+t[j]); printf("\n"); }
            if(++printed>=maxev) return 0;
        }
    }
    printf("END %lld\n",steps); return 0;
}
