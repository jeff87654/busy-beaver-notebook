"""Literal run from the blank tape; at every left-end X event (state B, new left minimum, tape 0 0 1^(4m+1) ...) compare with the
abstract rule system R1/R3/R4/R4e (abstract.py)."""
import sys
from abstract import step as astep
TM="1RB0RH_1RC1LE_0LD0RF_---1RE_1LB0LB_1RA0RG_0LC1RF_0LG1LA"
tm={}
for q,part in enumerate(TM.split('_')):
    for b in range(2):
        e=part[b*3:b*3+3]
        tm[(q,b)]=None if e[0]=='-' else (int(e[0]),1 if e[1]=='R' else -1,ord(e[2])-65)
N=int(sys.argv[1])
SZ=1<<22
tape=bytearray(SZ); pos=SZ//2; lo=hi=pos; q=0
cur=None; nev=0; bad=0; last_step=0
def parse():
    # tape right of head: 0 0 1^a 0 1^c1 ... 0 1 ; return (m,W) or None
    s=tape[pos:hi+1].decode('latin1').translate({0:'0',1:'1'}) if False else ''.join('1' if x else '0' for x in tape[pos:hi+1])
    s=s.rstrip('0')
    if not s.startswith('00'): return None
    r=s[2:]
    if not r.startswith('1'): return None
    bl=r.split('0')
    if bl[-1]!='1': return None
    a=len(bl[0])
    if (a-1)%4: return None
    return (a-1)//4, [len(b)-1 for b in bl[1:-1]]
for i in range(1,N+1):
    e=tm[(q,tape[pos])]
    if e is None: print('HALT at',i); break
    w,d,nq=e
    tape[pos]=w; pos+=d; q=nq
    if pos<lo:
        lo=pos
        if q==1:
            r=parse()
            if r is not None:
                if cur is not None:
                    pred=astep(*cur)
                    if pred!=(r[0],r[1]): bad+=1; print('MISMATCH at',i,cur,'pred',pred,'got',r)
                cur=r; nev+=1
    if pos>hi: hi=pos
print('steps',N,'X events',nev,'mismatches',bad,'last',cur if cur is None or len(str(cur))<200 else str(cur)[:200])
