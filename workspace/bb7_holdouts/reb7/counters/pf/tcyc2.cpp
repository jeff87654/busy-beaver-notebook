// tcyc2: translated-cycler detector (hash-based, low memory). tcyc2 MACHINE S0 N W SIDE [INIT|INITFILE]
// records at each right-extension (after S0) a 64-bit hash of (state, last W cells). On a hash repeat between
// extension events i0 < j with head min position over (i0, j] >= hi_i0 - W + 1, the run is a translated cycler.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <unordered_map>
#include <cstdint>
int nx[16][2], wr[16][2], dr[16][2];
int main(int argc,char**argv){
    const char*M=argv[1]; long long S0=atoll(argv[2]), N=atoll(argv[3]); long long W=atoll(argv[4]); int side=argc>5?(argv[5][0]=='L'?-1:1):1;
    int ns=0; for(const char*t=M;*t;){for(int c=0;c<2;++c){if(t[0]=='-')nx[ns][c]=-1;else{wr[ns][c]=t[0]-'0';dr[ns][c]=(t[1]=='R'?1:-1)*side;nx[ns][c]=t[2]-'A';}t+=3;}++ns;if(*t=='_')++t;}
    long long SZ=1LL<<28; std::vector<uint8_t>T(SZ,0); long long p=SZ/2; int q=0; long long hi=p, lo=p;
    if(argc>6){ std::string init=argv[6]; FILE*fi=fopen(argv[6],"r"); if(fi){std::string a; int ch; while((ch=fgetc(fi))!=EOF) if(ch!=10&&ch!=13) a.push_back((char)ch); fclose(fi); init=a;}
        q=init[0]-'A'; std::string b=init.substr(2);
        if(init[1]=='<'){ for(size_t i=0;i<b.size();++i) T[p+1+i]=b[i]-'0'; hi=p+(long long)b.size(); }
        else { for(size_t i=0;i<b.size();++i) T[p-(long long)b.size()+i]=b[i]-'0'; lo=p-(long long)b.size(); } }
    std::unordered_map<uint64_t,long long> rec; // hash -> event index
    std::vector<long long> evhi, evstep, segmin; long long curmin=p;
    std::unordered_map<uint64_t,long long> recL; std::vector<long long> evlo, evstepL, segmax; long long curmax=p;
    for(long long st=0;st<N;++st){
        int c=T[p]; if(nx[q][c]<0){printf("H %lld\n",st);return 0;}
        T[p]=wr[q][c]; p+=dr[q][c]; q=nx[q][c];
        if(p<=1||p>=SZ-2){printf("TAPE %lld\n",st);return 0;}
        if(p<curmin)curmin=p; if(p>curmax)curmax=p;
        if(p<lo){lo=p; if(st>=S0){
            uint64_t h=1469598103934665603ULL; h^=(uint64_t)q+77; h*=1099511628211ULL;
            for(long long i=lo;i<lo+W;++i){h^=T[i]; h*=1099511628211ULL;}
            long long j=evlo.size(); evlo.push_back(lo); evstepL.push_back(st+1); segmax.push_back(curmax); curmax=p;
            auto it=recL.find(h);
            if(it!=recL.end()){ long long i0=it->second; long long mx=-1; for(long long k=i0+1;k<=j;++k) if(segmax[k]>mx) mx=segmax[k];
                if(mx<=evlo[i0]+W-1){printf("TRANSLATED-CYCLER(left): period %lld steps (%lld->%lld), shift %lld, window %lld, margin %lld\n",evstepL[j]-evstepL[i0],evstepL[i0],evstepL[j],evlo[i0]-lo,W,evlo[i0]+W-1-mx);return 0;} }
            recL[h]=j; } else curmax=p; }
        if(p>hi){hi=p;
            if(st<S0){curmin=p; continue;}
            uint64_t h=1469598103934665603ULL; h^=(uint64_t)q; h*=1099511628211ULL;
            for(long long i=hi-W+1;i<=hi;++i){h^=T[i]; h*=1099511628211ULL;}
            long long j=evhi.size(); evhi.push_back(hi); evstep.push_back(st+1); segmin.push_back(curmin); curmin=p;
            auto it=rec.find(h);
            if(it!=rec.end()){
                long long i0=it->second; long long mn=1LL<<62;
                for(long long k=i0+1;k<=j;++k) if(segmin[k]<mn) mn=segmin[k];
                if(mn>=evhi[i0]-W+1){printf("TRANSLATED-CYCLER: period %lld steps (%lld->%lld), shift %lld, window %lld, margin %lld\n",evstep[j]-evstep[i0],evstep[i0],evstep[j],hi-evhi[i0],W,mn-(evhi[i0]-W+1));return 0;}
            }
            rec[h]=j;
            if(evhi.size()>50000000){puts("MEM");return 0;}
        }
    }
    printf("END\n");
}
