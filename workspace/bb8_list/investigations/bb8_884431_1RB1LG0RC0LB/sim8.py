"""Own literal sim of the actual machine on a growable tape (list), with helpers."""
TM='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
ST='ABCDEFGH'
def parse(tm):
    T=[]
    for ch in tm.split('_'):
        row=[]
        for i in (0,3):
            e=ch[i:i+3]
            row.append(None if e=='---' else (int(e[0]),1 if e[1]=='R' else -1,ST.index(e[2])))
        T.append(row)
    return T
T=parse(TM)
class M:
    def __init__(s,word='',off=0,state='A',pad=64):
        # tape = pad zeros + word + pad zeros ; head at pad+off
        s.t=[0]*pad+[int(c) for c in word]+[0]*pad
        s.p=pad+off; s.q=ST.index(state); s.n=0
    def step(s):
        e=T[s.q][s.t[s.p]]
        if e is None: return False
        w,d,q=e
        s.t[s.p]=w; s.p+=d; s.q=q; s.n+=1
        if s.p<0:
            s.t=[0]*len(s.t)+s.t; s.p+=len(s.t)//2
        elif s.p>=len(s.t):
            s.t=s.t+[0]*len(s.t)
        return True
    def word(s):
        """return (word from first 1, head offset within word (can be negative or beyond))"""
        t=s.t
        lo=0
        while lo<len(t) and t[lo]==0: lo+=1
        hi=len(t)-1
        while hi>lo and t[hi]==0: hi-=1
        return ''.join(map(str,t[lo:hi+1])), s.p-lo
