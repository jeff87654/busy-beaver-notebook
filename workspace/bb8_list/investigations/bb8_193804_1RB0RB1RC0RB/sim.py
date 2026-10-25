import sys
M="1RB0RB_1RC0RB_0LD1LF_1RH1LE_0LC0LF_1LG1RE_1LH1LE_0RA---"
def parse(m):
    T={}
    for i,g in enumerate(m.split('_')):
        for s in range(2):
            t=g[3*s:3*s+3]
            T[(chr(65+i),s)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,t[2])
    return T
T=parse(M)
def run(n, cb=None):
    tape={};pos=0;st='A'
    for i in range(n):
        s=tape.get(pos,0)
        tr=T[(st,s)]
        if tr is None: return i,tape,pos,st,True
        if cb: cb(i,tape,pos,st)
        tape[pos]=tr[0];pos+=tr[1];st=tr[2]
    return n,tape,pos,st,False
def show(tape,pos,st):
    lo=min(min(tape),pos);hi=max(max(tape),pos)
    return ''.join((('['+st+']') if p==pos else '')+str(tape.get(p,0)) for p in range(lo,hi+1))
if __name__=="__main__":
    n=int(sys.argv[1])
    r=run(n)
    print(r[0],r[4],show(r[1],r[2],r[3]))
