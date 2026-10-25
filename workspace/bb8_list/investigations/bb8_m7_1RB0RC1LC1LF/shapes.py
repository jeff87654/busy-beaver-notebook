import sys, itertools, collections
from tr import tm, ST, word
def gvisits(ds,a,b,maxsteps=3000000,maxvis=100000):
    w=word(ds,a,b)[::-1]
    tape={i:1 for i,c in enumerate(w) if c=='1'}
    pos=-1;q=6
    out=[]
    for step in range(1,maxsteps+1):
        s=tape.get(pos,0)
        tr=tm[(q,s)]
        if tr is None:
            out.append((step,'HALT'));return out
        w_,d,q=tr
        if w_: tape[pos]=1
        else: tape.pop(pos,None)
        pos+=d
        if q==6 and pos<min(tape):
            hi=max(tape)
            s_=''.join(str(tape.get(i,0)) for i in range(pos+1,hi+1))
            out.append((step,toks(s_)))
            if len(out)>=maxvis: return out
    return out
def toks(s):
    s=s.rstrip('0')
    res=[];i=0
    while i<len(s):
        t=s[i:i+3]
        m={'010':'U','100':'S','110':'V','1':'1'}.get(t)
        if m is None:
            m=('[%s]'%t)
        res.append(m); i+=3
    return res
def rle(t):
    out=[]
    for k,g in itertools.groupby(t):
        n=len(list(g)); out.append((k,n))
    return out
def fmt(r):
    return ' '.join(k if n==1 else '%s^%d'%(k,n) for k,n in r)
if __name__=='__main__':
    ds=eval(sys.argv[1]);a=int(sys.argv[2]);b=int(sys.argv[3])
    for st,t in gvisits(ds,a,b,maxvis=int(sys.argv[4]) if len(sys.argv)>4 else 60):
        print(st, fmt(rle(t)) if t!='HALT' else t)
