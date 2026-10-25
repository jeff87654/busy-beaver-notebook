/* TNF enumeration of 5-state boot machines (A0=1RB), exit = first undefined transition reached.
   Per-depth tape buffers (copy only the used span), Brent-style cycler pruning, tape bound +-TB.
   Candidate: exit reached within MAXB steps and tape tail = 0 (10)^10 1.  Usage: boottnf2 MAXB MINGAPHINT */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NS 5
#define TB 700
#define TL (2*TB+3)
long MAXB, nodes=0, cands=0;
typedef struct { signed char w[NS][2], d[NS][2], n[NS][2]; } T;
static unsigned char buf[12][TL], ck[12][TL];
static void out(T*t,int s,int r,unsigned char*tape,int pos,int lo,int hi){
  int h=hi; while(h>lo&&!tape[h])h--;
  if(h-lo<22) return;
  for(int k=0;k<11;k++){ if(tape[h-2*k]!=1||tape[h-2*k-1]!=0) return; }
  cands++;
  for(int a=0;a<NS;a++)for(int b=0;b<2;b++){ if(t->n[a][b]<0) printf("---"); else printf("%d%c%d",t->w[a][b],t->d[a][b]?'R':'L',t->n[a][b]); }
  printf(" %d %d %d ",s,r,pos-lo); for(int i=lo;i<=hi;i++) putchar('0'+tape[i]); putchar('\n'); fflush(stdout);
}
static void explore(T t,unsigned char*tp,int pos,int s,long steps,int ndef,int maxs,int lo,int hi,int dep){
  unsigned char *tape=buf[dep]; memcpy(tape+lo,tp+lo,hi-lo+1);
  int olo=lo, ohi=hi;
  nodes++;
  int cs=-1,cp=0,clo=0,chi=0; long nextck=steps+32;
  while(1){
    int r=tape[pos];
    if(t.n[s][r]<0){
      out(&t,s,r,tape,pos,lo,hi);
      if(ndef<2*NS-1){
        int lim = maxs+1 < NS-1 ? maxs+1 : NS-1;
        for(int n=0;n<=lim;n++) for(int w=0;w<2;w++) for(int d=0;d<2;d++){
          T u=t; u.w[s][r]=w; u.d[s][r]=d; u.n[s][r]=n;
          explore(u,tape,pos,s,steps,ndef+1, n>maxs?n:maxs, lo,hi,dep+1);
        }
      }
      break;
    }
    if(steps>=MAXB) break;
    if(steps==nextck){ memcpy(ck[dep]+lo,tape+lo,hi-lo+1); cs=s; cp=pos; clo=lo; chi=hi; nextck=steps*2; }
    else if(s==cs && pos==cp && lo==clo && hi==chi && memcmp(ck[dep]+lo,tape+lo,hi-lo+1)==0) break;
    tape[pos]=t.w[s][r]; pos+= t.d[s][r]?1:-1; s=t.n[s][r]; steps++;
    if(pos<1||pos>TL-2) break;
    if(pos<lo)lo=pos; if(pos>hi)hi=pos;
  }
  memset(tape+lo,0,hi-lo+1);
  (void)olo;(void)ohi;
}
int main(int argc,char**argv){
  MAXB=atol(argv[1]);
  T t; memset(&t,-1,sizeof t);
  t.w[0][0]=1; t.d[0][0]=1; t.n[0][0]=1;
  static unsigned char tape[TL];
  tape[TB+1]=1;
  explore(t,tape,TB+2,1,1,1,1,TB+1,TB+2,0);
  fprintf(stderr,"nodes=%ld cands=%ld\n",nodes,cands);
  return 0;
}
