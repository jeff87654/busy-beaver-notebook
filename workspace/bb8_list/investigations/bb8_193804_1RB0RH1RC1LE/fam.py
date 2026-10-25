"""Family X(a; cs): head in B at the left end of the tape, tape = 0^inf B> 0 0 1^a 0 1^c1 0 ... 0 1^ck 0 1 0^inf."""
import sys
from sim import T
OFF=0
def build(a,cs):
    s='00'+'1'*a
    for c in cs: s+='0'+'1'*c
    s+='01'
    return s
def parse(s):
    # s: tape right of head (head cell included as first char) -> (a, cs) or None
    s=s.rstrip('0')
    if not s.startswith('00') : return None
    r=s[2:]
    if not r.startswith('1'): return None
    blocks=r.split('0')
    if blocks[-1]!='1': return None
    bl=[len(b) for b in blocks]
    return bl[0], tuple(bl[1:-1])
def next_X(a,cs,N=10**7, kind='X'):
    """simulate from X(a;cs); return ('X',(a',cs'),steps) at next X event, ('HALT',steps,state) or ('TIMEOUT',..)"""
    s=build(a,cs)
    tape={i:int(ch) for i,ch in enumerate(s)}
    pos=0;q=1
    lo=0
    for i in range(1,N+1):
        b=tape.get(pos,0);e=T[(q,b)]
        if e is None: return ('HALT',i,chr(65+q),b)
        w,d,nq=e
        tape[pos]=w;pos+=d;q=nq
        if pos<lo:
            lo=pos
            if q==1:
                # new left end in state B; check everything left is blank (true since new min), parse right
                hi=max(tape)
                s2=''.join(str(tape.get(p,0)) for p in range(pos,hi+1))
                r=parse(s2)
                if r is not None:
                    return ('X',r,i)
    return ('TIMEOUT',)
if __name__=='__main__':
    a=int(sys.argv[1]);cs=tuple(int(x) for x in sys.argv[2:])
    print(next_X(a,cs))
