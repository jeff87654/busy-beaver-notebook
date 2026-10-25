import sys
exec(open('ev.py').read().split("N=int")[0])
def build(left,right,q='A'):
    """left/right lists of bits, head on first of right. returns state"""
    SZ=1<<16; tape=bytearray(SZ); p=SZ//2
    for i,b in enumerate(reversed(left)): tape[p-1-i]=b
    for i,b in enumerate(right): tape[p+i]=b
    return tape,p,ord(q)-65
def word(tape,p,q,w=None):
    lo=p;hi=p
    idx=[i for i in range(len(tape)) if tape[i]]
    a=min(idx+[p]);b=max(idx+[p])
    return "".join(map(str,tape[a:p]))+"[%s]"%"ABCDEFGH"[q]+"".join(map(str,tape[p:b+1]))
def run_until(tape,p,q,pred,N=10**6):
    for t in range(N):
        if t>0 and pred(tape,p,q): return t,tape,p,q
        r=tb[q*2+tape[p]]
        if r is None: return t,tape,p,q
        tape[p]=r[0]; p+=r[1]; q=r[2]
    return None
