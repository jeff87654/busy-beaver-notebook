from sim import *
import sys,re
T=parse(M)
def F(k,r,t): return '01011'+'001'*k+'0'+'1'*r+'00'+'1'*t
def parseF(x):
    m=re.fullmatch(r'01011((?:001)*)0(1+)001+',x)
    if not m: return None
    tt=re.fullmatch(r'.*00(1+)',x).group(1)
    return (len(m.group(1))//3,len(m.group(2)),len(tt))
def nxt(st,N=10**7,fam=None):
    tape={i:int(c) for i,c in enumerate(st)};p=0;s=1;lo=0;hi=len(st)-1
    for i in range(N):
        r=T[(s,tape.get(p,0))]
        if r is None: return ('HALT',i)
        tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
        lo=min(lo,p);hi=max(hi,p)
        if p<=lo and s==1:
            x=''.join(str(tape.get(q,0)) for q in range(lo,hi+1))
            f=parseF(x)
            if f: return (f,i+1)
    return None
if __name__=="__main__":
    for t in range(2,8):
        for r in (2,3,4,5,6):
            for k in (0,1,3):
                print(t,r,k,nxt(F(k,r,t)))
