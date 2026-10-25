import sys
TM=sys.argv[1] if len(sys.argv)>1 else "1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
def parse(tm):
    t={}
    for i,c in enumerate(tm.split('_')):
        for s in (0,1):
            e=c[3*s:3*s+3]
            t[(i,s)]=None if e=='---' else (int(e[0]),1 if e[1]=='R' else -1,ord(e[2])-65)
    return t
def run(tm,n,cb=None):
    t=parse(tm); tape={}; pos=0; st=0
    for k in range(n):
        s=tape.get(pos,0); e=t[(st,s)]
        if e is None: return ('halt',k,tape,pos,st)
        if cb: cb(k,tape,pos,st)
        w,d,ns=e; tape[pos]=w; pos+=d; st=ns
    return ('run',n,tape,pos,st)
def show(tape,pos,st):
    if not tape: return ''
    lo=min(min(tape),pos); hi=max(max(tape),pos)
    s=''
    for i in range(lo,hi+1):
        c=str(tape.get(i,0))
        if i==pos: c='['+'ABCDEFGH'[st]+']'+c
        s+=c
    return s
if __name__=='__main__':
    N=int(sys.argv[2]) if len(sys.argv)>2 else 400
    r=run(TM,N)
    print(r[0],r[1]); print(show(r[2],r[3],r[4]))
