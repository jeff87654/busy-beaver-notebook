/* TNF enumeration of 5-state 2-symbol boot machines (A0 = 1RB). The exit is the first undefined
   transition reached. Candidates: exit reached within MAXB steps, tape tail = (10)^10 1 preceded by 0,
   tape stays within +-TB cells. Output: table(10 x "wdn", '-' undefined) exit_s exit_r pos tape */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NS 5
#define TB 600
#define TL (2*TB+3)
long MAXB, nodes=0, cands=0;
typedef struct { signed char w[NS][2], d[NS][2], n[NS][2]; } T;
static void out(T*t,int s,int r,unsigned char*tape,int pos,int lo,int hi){
  int h=hi; while(h>lo&&!tape[h])h--;
  if(h-lo<22) return;
  for(int k=0;k<11;k++){ if(tape[h-2*k]!=1||tape[h-2*k-1]!=0) return; }
  cands++;
  for(int a=0;a<NS;a++)for(int b=0;b<2;b++){ if(t->n[a][b]<0) printf("---"); else printf("%d%c%d",t->w[a][b],t->d[a][b]?'R':'L',t->n[a][b]); }
  printf(" %d %d %d ",s,r,pos-lo); for(int i=lo;i<=hi;i++) putchar('0'+tape[i]); putchar('\n');
}
static void explore(T t,unsigned char*tp,int pos,int s,long steps,int ndef,int maxs,int lo,int hi){
  unsigned char tape[TL]; memcpy(tape,tp,TL);
  nodes++;
  while(1){
    int r=tape[pos];
    if(t.n[s][r]<0){
      out(&t,s,r,tape,pos,lo,hi);
      if(ndef>=2*NS-1) return;
      int lim = maxs+1 < NS-1 ? maxs+1 : NS-1;
      for(int n=0;n<=lim;n++) for(int w=0;w<2;w++) for(int d=0;d<2;d++){
        T u=t; u.w[s][r]=w; u.d[s][r]=d; u.n[s][r]=n;
        explore(u,tape,pos,s,steps,ndef+1, n>maxs?n:maxs, lo,hi);
      }
      return;
    }
    if(steps>=MAXB) return;
    tape[pos]=t.w[s][r]; pos+= t.d[s][r]?1:-1; s=t.n[s][r]; steps++;
    if(pos<1||pos>TL-2) return;
    if(pos<lo)lo=pos; if(pos>hi)hi=pos;
  }
}
int main(int argc,char**argv){
  MAXB=atol(argv[1]);
  T t; memset(&t,-1,sizeof t);
  t.w[0][0]=1; t.d[0][0]=1; t.n[0][0]=1;   /* A0 = 1RB */
  unsigned char tape[TL]; memset(tape,0,TL);
  /* first step done by hand: write 1 at TB+1, move to TB+2 state B */
  tape[TB+1]=1;
  explore(t,tape,TB+2,1,1,1,1,TB+1,TB+2);
  fprintf(stderr,"nodes=%ld cands=%ld\n",nodes,cands);
  return 0;
}
