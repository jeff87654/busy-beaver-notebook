import sys
M="1RB1RC_0RC0LB_0RD1RF_1LE1LD_1RC1LG_1LD1RA_1LA0LH_---1LG"
T={}
for i,s in enumerate(M.split('_')):
    for b in (0,1):
        t=s[3*b:3*b+3]
        T[(i,b)]=None if t=='---' else (int(t[0]),t[1],'ABCDEFGH'.index(t[2]))
def run(n,report=()):
    tape={};pos=0;q=0
    out=[]
    for st in range(n):
        v=tape.get(pos,0)
        t=T[(q,v)]
        if t is None: out.append(('HALT',st,pos)); break
        tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
        if q==0 and 0: pass
        if st+1 in report: out.append((st+1,q,pos,dict(tape)))
    return out,tape,pos,q
def show(tape,pos,q):
    lo=min(tape);hi=max(tape)
    s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    return lo,s,pos-lo,'ABCDEFGH'[q]
if __name__=="__main__":
    n=int(sys.argv[1])
    o,t,p,q=run(n)
    print(o[:1] if o else '', show(t,p,q))
