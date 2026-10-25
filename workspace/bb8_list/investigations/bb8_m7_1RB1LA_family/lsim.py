import sys
def parse(tm):
    t={}
    for i,ch in enumerate(tm.split('_')):
        for s in (0,1):
            e=ch[3*s:3*s+3]
            t[(chr(65+i),s)]=None if e=='---' else (int(e[0]),1 if e[1]=='R' else -1,e[2])
    return t
def run(tm,steps,dump_every=None,start=0):
    t=parse(tm)
    tape={}
    pos=0;st='A'
    for n in range(steps):
        s=tape.get(pos,0)
        r=t[(st,s)]
        if r is None:
            return ('HALT',n,st,s,tape,pos)
        w,d,ns=r
        if w: tape[pos]=1
        else: tape.pop(pos,None)
        pos+=d;st=ns
        if dump_every and n>=start and (n+1)%dump_every==0:
            show(tape,pos,st,n+1)
    return ('RUN',steps,st,tape.get(pos,0),tape,pos)
def show(tape,pos,st,n):
    lo=min(list(tape)+[pos]);hi=max(list(tape)+[pos])
    s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    p=pos-lo
    print(n,st,s[:p]+'['+s[p]+']'+s[p+1:])
if __name__=='__main__':
    tm=sys.argv[1];N=int(sys.argv[2]);de=int(sys.argv[3]) if len(sys.argv)>3 else None
    r=run(tm,N,de)
    print(r[:4])
