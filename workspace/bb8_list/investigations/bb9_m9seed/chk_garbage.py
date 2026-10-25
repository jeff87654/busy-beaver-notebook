# does Ch j b z -> Ca j W z need the whole left side blank, or only a few zeros?
from tm import *
M9='1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD'
tm,n=parse(M9)
def W(j,b):
    if j==0: return b+3
    x=2
    for _ in range(b+1): x=W(j-1,x)
    return x
for gap in range(0,5):
  for j in (1,2):
    for b in (0,1,2):
        G=[1,1,0,1]  # garbage
        tape=G+[0]*gap+[1,0]*j
        pos=len(tape)-1
        tape+=[1]*(b+1)+[0]+[1,0,1]
        minpos=[10**9]
        def cb(T,p,q,s):
            minpos[0]=min(minpos[0],p)
            if q!=0 or T[p]!=0: return False
            k=p-1;c=0
            while T[k]==1: c+=1;k-=1
            return c==W(j,b) and T[p+1]==1 and T[p+2]==0 and T[p+3]==1 and s>1
        r=run(tm,tape=tape,pos=pos,q=7,maxs=10**6,cb=cb)
        ok = r[0]=='CB' and all(r[2][i]==G[i] for i in range(4))
        print('gap',gap,'j',j,'b',b,r[0],'garbage intact' if ok else 'BROKEN','min head pos',minpos[0]-len(G))
