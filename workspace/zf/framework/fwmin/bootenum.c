/* Enumerate 5-state boot tables within distance <= D of Wade's boot (exit = next 5).
   Prints machines that exit within MAXB steps and whose tape tail is >= 11 runs '1' (10)^10 1.
   Output line: changes...  | exit_state exit_read pos lo hi | tape string from lo to hi */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N 5
#define TL (1<<20)
static unsigned char tape[TL];
int W[N][2], Dd[N][2], Nx[N][2];
int wW[N][2]={{1,0},{0,0},{1,0},{0,0},{1,0}};
int wD[N][2]={{1,0},{1,1},{0,1},{0,0},{0,0}}; /* 1=R 0=L */
int wN[N][2]={{1,2},{2,1},{3,4},{4,5},{0,1}}; /* A..E = 0..4, 5 = EXIT */
long MAXB;
int run(int *es,int *er,long *pp,long *plo,long *phi){
  memset(tape,0,TL); long p=TL/2,lo=p,hi=p; int s=0; long st=0;
  while(st<MAXB){int r=tape[p]; if(Nx[s][r]==5){*es=s;*er=r;*pp=p;*plo=lo;*phi=hi;return 1;}
    tape[p]=W[s][r]; p+= Dd[s][r]?1:-1; if(p<lo)lo=p; if(p>hi)hi=p; if(p<=0||p>=TL-1) return 0; s=Nx[s][r]; st++;}
  return 0;}
int tailok(long lo,long hi){ long h=hi; while(h>lo&&!tape[h])h--; /* need (10)^10 1 ending at h, preceded by 0 */
  for(int k=0;k<11;k++){ if(tape[h-2*k]!=1) return 0; if(tape[h-2*k-1]!=0) return 0;} return 1;}
int main(int argc,char**argv){
  int D=atoi(argv[1]); MAXB=atol(argv[2]);
  int keys=10, nopt=2*2*6; long tried=0,out=0;
  int idx[3];
  for(int d=0; d<=D; d++){
    /* iterate combos of d keys */
    int c[3]={0,1,2};
    for(int i=0;i<d;i++)c[i]=i;
    while(1){
      long tot=1; for(int i=0;i<d;i++) tot*=nopt;
      for(long v=0; v<tot; v++){
        memcpy(W,wW,sizeof W); memcpy(Dd,wD,sizeof Dd); memcpy(Nx,wN,sizeof Nx);
        long vv=v; int bad=0;
        for(int i=0;i<d;i++){ int o=vv%nopt; vv/=nopt; int s=c[i]/2,r=c[i]%2;
          int w=o%2, dd=(o/2)%2, n=o/4; if(w==wW[s][r]&&dd==wD[s][r]&&n==wN[s][r]) bad=1;
          W[s][r]=w; Dd[s][r]=dd; Nx[s][r]=n; idx[i]=o;}
        if(bad) continue;
        int ne=0; for(int s=0;s<N;s++)for(int r=0;r<2;r++) if(Nx[s][r]==5) ne++;
        if(ne!=1) continue;
        tried++;
        int es,er; long p,lo,hi;
        if(!run(&es,&er,&p,&lo,&hi)) continue;
        if(!tailok(lo,hi)) continue;
        out++;
        for(int s=0;s<N;s++)for(int r=0;r<2;r++) printf("%d%c%d", W[s][r], Dd[s][r]?'R':'L', Nx[s][r]);
        printf(" %d %d %ld ", es, er, p-lo);
        for(long i=lo;i<=hi;i++) putchar('0'+tape[i]);
        putchar('\n');
      }
      if(d==0) break;
      int i=d-1; while(i>=0 && c[i]==keys-d+i) i--; if(i<0) break; c[i]++; for(int j=i+1;j<d;j++) c[j]=c[j-1]+1;
    }
    fprintf(stderr,"d=%d tried=%ld out=%ld\n",d,tried,out);
  }
  return 0;}
