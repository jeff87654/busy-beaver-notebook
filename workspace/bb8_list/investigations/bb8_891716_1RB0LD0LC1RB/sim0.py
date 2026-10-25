import sys
TM="1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---"
def parse(tm):
    d={}
    for i,t in enumerate(tm.split('_')):
        for s in (0,1):
            x=t[3*s:3*s+3]
            d[(i,s)]=None if x=='---' else (int(x[0]),x[1],'ABCDEFGH'.index(x[2]))
    return d
def run(tm,N,snap=()):
    d=parse(tm)
    tape={}
    pos=0;q=0
    out=[]
    for n in range(N):
        s=tape.get(pos,0)
        t=d[(q,s)]
        if t is None:
            return n,q,pos,tape,'HALT'
        w,dr,nq=t
        tape[pos]=w
        pos+= 1 if dr=='R' else -1
        q=nq
        if n+1 in snap: out.append((n+1,q,pos,dict(tape)))
    return N,q,pos,tape,out
def show(tape,pos,q):
    lo=min(tape);hi=max(tape)
    lo=min(lo,pos);hi=max(hi,pos)
    s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    return s,pos-lo,'ABCDEFGH'[q]
if __name__=='__main__':
    tm=sys.argv[1] if len(sys.argv)>1 else TM
    for N in [100,200,300,400,600,1000]:
        r=run(tm,N)
        s,p,q=show(r[3],r[2],r[1])
        print(N,q,p,len(s)); print(s[:p]+'['+q+']'+s[p:])
