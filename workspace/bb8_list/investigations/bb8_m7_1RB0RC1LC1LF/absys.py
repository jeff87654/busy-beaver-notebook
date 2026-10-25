import sys, itertools
from tr import tm, ST
CELL={'U':'010','S':'100','V':'110'}
def cells(w): return ''.join(CELL[t] for t in w)
def toks(s):
    s=s.rstrip('0')
    res=[];i=0
    while i<len(s):
        t=s[i:i+3]
        m={'010':'U','100':'S','110':'V','1':'1'}.get(t)
        if m is None: m='['+t+']'
        res.append(m); i+=3
    # trailing '1' = S followed by blank
    if res and res[-1]=='1': res[-1]='S'
    return res
def mstep(w,cap=5000000):
    """machine: from G-left config with tokens w (string of 'U','S','V'), run to next G-left visit; return (steps, newtokens) or ('HALT',steps)"""
    s=cells(w)
    tape={i:1 for i,c in enumerate(s) if c=='1'}
    pos=-1;q=6
    for step in range(1,cap+1):
        v=tape.get(pos,0)
        tr=tm[(q,v)]
        if tr is None: return ('HALT',step)
        w_,d,q=tr
        if w_: tape[pos]=1
        else: tape.pop(pos,None)
        pos+=d
        if q==6 and pos<min(tape):
            hi=max(tape)
            ss=''.join(str(tape.get(i,0)) for i in range(pos+1,hi+1))
            return (step,toks(ss))
    return ('CAP',cap)
def pre(i,k,T,Z):
    return 'U'*i+'S'*k+T+Z
def A(i,k): return 'U'+'S'*(i-1)+'U'*(k-1)+'S'+'V'
def B(i,k): return 'U'+'S'*(i-1)+'U'*k+'S'
if __name__=='__main__':
    bad=0
    for i in range(1,7):
        for k in range(1,7):
            for T in 'UV':
                for Z in ['','S','US','VS','SS','UUS']:
                    w=pre(i,k,T,Z)+('S' if True else '')
                    r=mstep(w)
                    exp=(A(i,k) if T=='U' else B(i,k))+Z+'S'
                    if r[0]=='HALT' or ''.join(r[1])!=exp:
                        bad+=1
                        if bad<30: print('MISMATCH',w,'got',r[0],''.join(r[1]) if r[0]!='HALT' else '','exp',exp)
    print('bad',bad)
