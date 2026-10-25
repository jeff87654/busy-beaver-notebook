# which slots does the Ch cascade use? run Ch j b z literally on M9 and on M11 (rows renamed?) and compare usage
from tm import *
from collections import Counter
M9='1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD'
tm,n=parse(M9)
def W(j,b):
    if j==0: return b+3
    x=2
    for _ in range(b+1): x=W(j-1,x)
    return x
tot=Counter()
for j in range(0,3):
    for b in range(0,4):
        if j==2 and b>2: continue
        # tape: (10)^j 1^(b+1) 0 ; head on the last 0 of (10)^j (or blank cell left of 1s) state H
        tape=[0]*5+[1,0]*j
        pos=len(tape)-1 if j>0 else len(tape)-1
        if j==0: tape=tape  # head at a blank
        tape+= [1]*(b+1)+[0]*3+[1,0,1]   # z = 0 0 1 0 1 marker
        u=Counter()
        target=None
        def cb(T,p,q,s):
            # stop at Ca j W z: state A, left 1^W (10)^j
            if q!=0 or T[p]!=0: return False
            # count ones left
            k=p-1;c=0
            while T[k]==1: c+=1;k-=1
            return c==W(j,b) and s>1
        r=run(tm,tape=tape,pos=pos,q=7,maxs=10**7,usage=u,cb=cb)
        tot+=u
        print(j,b,r[0],r[1],'W=',W(j,b), show(r[2],r[3],r[4],0,None)[:90])
print(sorted(chr(65+k[0])+str(k[1]) for k in tot))
