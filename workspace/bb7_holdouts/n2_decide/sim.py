import idle, sys
M="1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA"
def parse(m):
    T={}
    for i,r in enumerate(m.split('_')):
        for c in range(2):
            t=r[3*c:3*c+3]
            T[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
    return T
T=parse(M)
def run(steps,show_every=None,kmom=False):
    tape={};pos=0;q=0
    out=[]
    for s in range(steps):
        b=tape.get(pos,0)
        tr=T[(q,b)]
        if tr is None: print("HALT",s);return
        if kmom and q==0:
            out.append((s,pos,dict(tape)))
        tape[pos]=tr[0];pos+=tr[1];q=tr[2]
    return out,tape,pos,q
def show(tape,pos,q):
    lo=min(list(tape)+[pos]);hi=max(list(tape)+[pos])
    return ''.join(('['+'ABCDEFG'[q]+']' if i==pos else '')+str(tape.get(i,0)) for i in range(lo,hi+1)), lo
if __name__=="__main__":
    n=int(sys.argv[1])
    tape={};pos=0;q=0
    for s in range(n):
        b=tape.get(pos,0);tr=T[(q,b)]
        if tr is None: print("HALT",s);break
        tape[pos]=tr[0];pos+=tr[1];q=tr[2]
        if q==0 and s>n-int(sys.argv[2]):
            st,lo=show(tape,pos,q);print(s,lo,st)
