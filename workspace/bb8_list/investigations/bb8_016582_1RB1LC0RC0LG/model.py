"""Abstract model of the machine on C(L,x,y) = 0^inf 1^L 0 1^x 0 1^y 0 0 D> 0^inf (head in D on the blank right of y).
Rules (each verified by literal simulation in rules_check.py):
  R1: C(L,x+2,y)  -->  C(L,x,y+8)         4y+64 steps
  S6: C(L+6,1,y)  -->  C(L+1,y+12,3)      6y+147
  S3: C(3,1,y)    -->  C(y+9,7,3)         4y+198
  S1: C(1,1,y)    -->  C(y+11,7,3)        4y+204
  S4: C(4,1,y) halts (undefined G0) after 3y+83 steps with y+15 ones.
Start: blank tape --130 steps--> C(1,7,3)."""
import sys
def events(maxevents=10**9):
    t=130;L,x,y=1,7,3;n=0
    while n<maxevents:
        yield (t,L,x,y);n+=1
        if x>=3:
            t+=4*y+64;x-=2;y+=8
        elif L>=6: t+=6*y+147;L,x,y=L-5,y+12,3
        elif L==3: t+=4*y+198;L,x,y=y+9,7,3
        elif L==1: t+=4*y+204;L,x,y=y+11,7,3
        else:
            yield ('HALT',L,t+3*y+83,y+15); return
def run_full():
    t=130;L,x,y=1,7,3
    levels=[]
    while True:
        assert x%2==1 and x>=1
        if x>=3:
            n=(x-1)//2
            t+=n*(4*y+64)+16*n*(n-1);y+=8*n;x=1
        if L>=6: t+=6*y+147;L,x,y=L-5,y+12,3
        elif L==3: levels.append(L);t+=4*y+198;L,x,y=y+9,7,3;print("level end L'=",L%10**6 if L>10**6 else L,file=sys.stderr)
        elif L==1: t+=4*y+204;L,x,y=y+11,7,3;print("L'=",L,file=sys.stderr)
        elif L==4: return t+3*y+83,y+15,x,y
        else: raise Exception("other halt L=%d"%L)
if __name__=="__main__":
    steps,sigma,x,y=run_full()
    print("steps digits",len(str(steps)),"sigma digits",len(str(sigma)))
    import math
    print(str(steps)[:30],str(sigma)[:30], "sigma mod 10^6",sigma%10**6)
