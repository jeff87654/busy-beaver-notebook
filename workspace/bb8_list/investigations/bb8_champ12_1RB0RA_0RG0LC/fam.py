# literal simulator + family (right end, state B) tools for the champ12 machines
import sys
M1='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE'
M2='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE'
def parse_tm(s):
    tm={}
    for i,r in enumerate(s.split('_')):
        for c in (0,1):
            t=r[3*c:3*c+3]
            tm[(i,c)]=None if t=='---' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
    return tm
P='11';U='10';S='111001'
def word(ds,a,b):
    w=P
    for d in ds: w+=U*(3*d+1)+'1'
    w+=U*(3*a+1)+'1'
    w+=U*(3*b+2)+S
    return w
def parse_word(w):
    """w: tape string left of head (head on blank right of w). return (ds,a,b) or None"""
    if not w.endswith(S) or not w.startswith(P): return None
    x=len(w)-len(S); z=len(P); runs=[]
    while True:
        k=0
        while x-2>=z and w[x-2:x]==U: x-=2; k+=1
        runs.append(k)
        if x==z: break
        if x-1<z or w[x-1]!='1': return None
        x-=1
    if len(runs)<2: return None
    b=runs[0]-2
    if b<0 or b%3: return None
    b//=3
    ds=[]
    for r in runs[1:]:
        if r<1 or (r-1)%3: return None
        ds.append((r-1)//3)
    a=ds[0]; ds=ds[1:][::-1]
    return ds,a,b
class Sim:
    def __init__(s,tm,tape='',pos=None,q=0,size=1<<20):
        s.tm=tm; s.n=size; s.t=bytearray(size); s.p=size//2; s.q=q; s.steps=0
        base=s.p-len(tape)
        for i,ch in enumerate(tape): s.t[base+i]=ord(ch)-48
        s.p=s.p
    def run(s,N,stop_on=None):
        tm=s.tm;t=s.t;p=s.p;q=s.q;st=0
        while st<N:
            r=tm[(q,t[p])]
            if r is None: s.p=p;s.q=q;s.steps+=st;return 'HALT'
            w,d,nq=r; t[p]=w; p+=d; q=nq; st+=1
            if p<8 or p>s.n-8: s.p=p;s.q=q;s.steps+=st;return 'EDGE'
            if stop_on is not None and q==stop_on[0] and t[p]==0:
                s.p=p;s.q=q;s.steps+=st;return 'STOP'
        s.p=p;s.q=q;s.steps+=st;return 'N'
    def left_word(s):
        t=s.t
        hi=s.p
        # require nothing right of p
        j=s.n-1
        while j>hi and not t[j]: j-=1
        if j>hi: return None
        lo=0
        while lo<hi and not t[lo]: lo+=1
        return ''.join(chr(48+t[i]) for i in range(lo,hi))
def next_cfg(tm,ds,a,b,N=2000000):
    w=word(ds,a,b)
    s=Sim(tm,w,q=1)
    total=0
    while total<N:
        r=s.run(N-total, stop_on=(1,))
        if r=='HALT': return 'HALT',s.steps
        if r=='N' or r=='EDGE': return 'TIMEOUT',s.steps
        lw=s.left_word()
        if lw is not None:
            pr=parse_word(lw)
            if pr: return pr,s.steps
        total=s.steps
    return 'TIMEOUT',s.steps
if __name__=='__main__':
    tm=parse_tm(M1)
    print(next_cfg(tm,[],0,1))
