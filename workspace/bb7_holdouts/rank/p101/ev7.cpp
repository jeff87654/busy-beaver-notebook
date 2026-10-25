// ev7 MACHINE MAXSTEPS : mirrored machine from blank tape (state A); at each event (state B on a blank right of every 1)
// computes the block list (blocks of 1s at spacing 2, gaps>=2). Prints non-R1 events as "E step nR1skipped b1 g1 b2 ...",
// where an R1 event is: same list except last-but-one block -1 and last block +2 (or merge when that block was 1).
// Ends with "HALT step" or "END step".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
using namespace std;
int main(int argc,char**argv){
    const char*M=argv[1]; long long maxs=atoll(argv[2]);
    int W[7][2],D[7][2],N[7][2];
    for(int q=0;q<7;q++)for(int c=0;c<2;c++){const char*t=M+q*7+c*3; if(t[0]=='-'){N[q][c]=-1;continue;}
        W[q][c]=t[0]-'0'; D[q][c]=(t[1]=='R')?-1:1; /*mirrored*/ N[q][c]=t[2]-'A';}
    const long long SZ=1LL<<27; vector<unsigned char> T(SZ,0);
    long long p=SZ/2, mn=p, mx=p-1; int q=0;
    vector<long long> prev, cur; long long skipped=0;
    for(long long st=0;st<maxs;st++){
        if(p<=2||p>=SZ-2){printf("TAPE %lld\n",st);return 0;}
        int c=T[p];
        if(N[q][c]<0){printf("HALT %lld\n",st);return 0;}
        int w=W[q][c]; T[p]=w;
        if(w){ if(mn>mx){mn=mx=p;} else {if(p<mn)mn=p; if(p>mx)mx=p;} }
        p+=D[q][c]; q=N[q][c];
        if(q!=1||T[p]!=0||p<=mx) continue;
        while(mx>mn && !T[mx]) mx--;
        if(p<=mx) continue;
        while(mn<mx && !T[mn]) mn++;
        cur.clear(); cur.push_back(1); long long last=-1;
        for(long long i=mn;i<=mx;i++) if(T[i]){ if(last>=0){ long long g=i-last-1; if(g==1) cur.back()++; else {cur.push_back(g); cur.push_back(1);} } last=i; }
        bool r1=false; size_t n=cur.size();
        if(!prev.empty()){
            if(prev.size()==n && n>=3 && cur[n-1]==prev[n-1]+2 && cur[n-3]==prev[n-3]-1 && cur[n-2]==prev[n-2]){
                r1=true; for(size_t i=0;i+3<n;i++) if(cur[i]!=prev[i]){r1=false;break;}
            }
        }
        if(r1) skipped++;
        else { printf("E %lld %lld",st+1,skipped); for(auto x:cur) printf(" %lld",x); printf("\n"); skipped=0; }
        prev.swap(cur);
    }
    printf("END %lld\n",maxs); return 0;
}
