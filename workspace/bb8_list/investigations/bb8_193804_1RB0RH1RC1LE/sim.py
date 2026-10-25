import sys
TM="1RB0RH_1RC1LE_0LD0RF_---1RE_1LB0LB_1RA0RG_0LC1RF_0LG1LA"
def parse(s):
    t={}
    for q,part in enumerate(s.split('_')):
        for b in range(2):
            e=part[b*3:b*3+3]
            t[(q,b)]=None if e[0]=='-' else (int(e[0]),1 if e[1]=='R' else -1,ord(e[2])-65)
    return t
T=parse(TM)
def run(n, hook=None):
    tape={}
    pos=0;q=0
    for i in range(n):
        b=tape.get(pos,0)
        e=T[(q,b)]
        if e is None:
            return ('HALT',i,q,b,tape)
        w,d,nq=e
        if hook: hook(i,q,pos,tape)
        tape[pos]=w;pos+=d;q=nq
    return ('RUN',n,q,pos,tape)
def show(tape,pos=None,q=None):
    if not tape: return ''
    lo=min(tape);hi=max(tape)
    if pos is not None: lo=min(lo,pos);hi=max(hi,pos)
    s=''
    for p in range(lo,hi+1):
        if p==pos: s+='['+chr(65+q)+']'
        s+=str(tape.get(p,0))
    return s
if __name__=='__main__':
    n=int(sys.argv[1])
    r=run(n)
    print(r[:4])
    print(show(r[4],r[3],r[2]))
