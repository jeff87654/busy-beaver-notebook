// tcyc: translated-cycler detector on the right end. tcyc MACHINE START_STEP MAX_STEP W
// at every right extension (head p > hi) record (state, suffix tape[hi-W+1..hi]) and min head pos since previous record.
// if a record repeats (same state & suffix) and, since the earlier record, the head never went below (hi_old - W + 1),
// then the machine is a translated cycler (never halts). prints the proof data.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <map>
#include <cstdint>
int nx[16][2], wr[16][2], dr[16][2];
int main(int argc,char**argv){
    const char*M=argv[1]; long long S0=atoll(argv[2]), N=atoll(argv[3]); long long W=atoll(argv[4]); int side=argc>5? (argv[5][0]=='L'?-1:1):1;
    int ns=0; for(const char*t=M;*t;){for(int c=0;c<2;++c){if(t[0]=='-')nx[ns][c]=-1;else{wr[ns][c]=t[0]-'0';dr[ns][c]=(t[1]=='R'?1:-1)*side;nx[ns][c]=t[2]-'A';}t+=3;}++ns;if(*t=='_')++t;}
    long long SZ=1LL<<27; std::string init=argc>6?argv[6]:"";
    auto doinit=[&](std::vector<uint8_t>&TT,long long &pp,int &qq){ pp=SZ/2; qq=0; if(init.size()>2){ qq=init[0]-'A'; std::string b=init.substr(2); if(init[1]=='<'){ for(size_t i=0;i<b.size();++i) TT[pp+1+(long long)i]=b[i]-'0'; } else { for(size_t i=0;i<b.size();++i) TT[pp-(long long)b.size()+(long long)i]=b[i]-'0'; } } };
    std::vector<uint8_t>T(SZ,0); long long p; int q; doinit(T,p,q); long long hi=p+(init.size()>1&&init[1]=='<'?(long long)init.size():0),lo=p-(long long)init.size();
    std::map<std::string,std::pair<long long,long long>> seen; // key -> (step, hi)
    std::vector<std::pair<long long,long long>> minsince; // not used
    long long minpos=p; long long nfail=0;
    for(long long st=0;st<N;++st){
        int c=T[p]; if(nx[q][c]<0){printf("H %lld\n",st);return 0;}
        T[p]=wr[q][c]; p+=dr[q][c]; q=nx[q][c];
        if(p<=1||p>=SZ-2){printf("TAPE\n");return 0;}
        if(p<minpos)minpos=p;
        if(p<lo)lo=p;
        if(p>hi){hi=p;
            if(st<S0) {minpos=p; continue;}
            std::string key(1,'A'+q); key.reserve(W+1);
            for(long long i=hi-W+1;i<=hi;++i) key.push_back('0'+T[i]);
            auto it=seen.find(key);
            if(it!=seen.end()){
                long long hio=it->second.second; long long st0=it->second.first;
                std::vector<uint8_t>T2(SZ,0); long long p2; int q2; doinit(T2,p2,q2); long long mn=1LL<<62;
                for(long long s2=0;s2<st+1;++s2){int c2=T2[p2]; if(nx[q2][c2]<0) break; T2[p2]=wr[q2][c2]; p2+=dr[q2][c2]; q2=nx[q2][c2]; if(s2+1>st0 && p2<mn) mn=p2;}
                if(mn>=hio-W+1) printf("REPEAT state %c steps %lld -> %lld shift %lld  min_head-(hio-W+1)=%lld\n",'A'+q,st0,st+1,hi-hio,mn-(hio-W+1));
                if(mn>=hio-W+1){printf("TRANSLATED-CYCLER proven: period %lld steps, shift %lld, window %lld\n",st+1-st0,hi-hio,W);return 0;}
                seen.clear(); nfail++; if(nfail>2000){puts("GIVEUP");return 0;} continue;
            }
            seen[key]={st+1,hi};
        }
    }
    printf("END\n");
}
