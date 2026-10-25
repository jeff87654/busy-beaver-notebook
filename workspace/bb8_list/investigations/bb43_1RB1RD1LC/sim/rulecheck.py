# Check Ligocki-notation rules by literal simulation.
# pattern tokens separated by spaces: S | 0^inf | (w)^{e} | d^{e} | literal digits | <X | X>
# S = unknown context: reading it is a failure. 0^inf = blank forever.
import re
from psim import T
U=-1
def expand(pat, env):
    toks=pat.split()
    cells=[]; head=None; state=None; leftinf=None; rightinf=None
    for i,t in enumerate(toks):
        if t in ('S','0^inf'):
            kind = U if t=='S' else 0
            if i==0: leftinf=kind
            else: rightinf=kind
            continue
        m=re.fullmatch(r'<([A-DZ])',t)
        if m: head=len(cells)-1; state=m.group(1); continue
        m=re.fullmatch(r'([A-DZ])>',t)
        if m: head=len(cells); state=m.group(1); continue
        m=re.fullmatch(r'\((\d+)\)\^(.+)',t) or re.fullmatch(r'(\d)\^(.+)',t)
        if m:
            k=eval(m.group(2).strip("{}"),{},env); assert k>=0, (t,k)
            cells += [int(c) for c in m.group(1)]*k; continue
        m=re.fullmatch(r'\((\d+)\)',t)
        if m: t=m.group(1)
        assert re.fullmatch(r'\d+',t), t
        cells += [int(c) for c in t]
    return cells, head, state, leftinf, rightinf
def check(lhs, rhs, env, steps=None, maxsteps=10**7, verbose=False):
    L,h,q,li,ri = expand(lhs,env)
    R,h2,q2,li2,ri2 = expand(rhs,env)
    assert li==li2 and ri==ri2
    pad=maxsteps if maxsteps<5000 else 5000
    # tape as dict
    tape={i:v for i,v in enumerate(L)}
    def rd(p):
        if p in tape: return tape[p]
        return (li if p<0 else ri)
    pos=h; st=ord(q)-65; n=0
    off = h2-h  # unknown; we compare up to translation: RHS head index aligned so contexts align => left context boundary at index 0 in both
    # contexts align: LHS cells occupy [0,len(L)), RHS cells occupy [0,len(R)) with the same left boundary, provided left context is S or 0^inf.
    target=None
    while n<maxsteps:
        if st==ord(q2)-65 and matches(tape,pos,R,h2,li,ri,len(L),rd):
            if steps is not None and n!=steps: return ('wrong steps',n,steps)
            return ('OK',n)
        s=rd(pos)
        if s==U: return ('read unknown context',n)
        w,d,nq=T[(st,s)]
        if nq==25: return ('halt',n)
        tape[pos]=w; pos+=d; st=nq; n+=1
    return ('no match',n)

def norm(cells,head):
    # strip zeros at both ends keeping the head inside
    lo=0; hi=len(cells)-1
    while lo<head and lo<=hi and cells[lo]==0: lo+=1
    while hi>head and hi>=lo and cells[hi]==0: hi-=1
    return tuple(cells[lo:hi+1]), head-lo
def matches(tape,pos,R,h2,li,ri,lenL,rd):
    if li==U: shift=0
    elif ri==U: shift=lenL-len(R)
    else:
        lo=min(list(tape)+[pos]); hi=max(list(tape)+[pos])
        a=norm([rd(p) for p in range(lo,hi+1)],pos-lo)
        lo2=min(0,h2); hi2=max(len(R)-1,h2)
        b=norm([R[p] if 0<=p<len(R) else 0 for p in range(lo2,hi2+1)],h2-lo2)
        return a==b
    if pos!=h2+shift: return False
    lo=min(list(tape)+[shift,pos]); hi=max(list(tape)+[shift+len(R)-1,pos])
    for p in range(lo,hi+1):
        q=p-shift
        want = R[q] if 0<=q<len(R) else (li if q<0 else ri)
        if rd(p)!=want: return False
    return True
