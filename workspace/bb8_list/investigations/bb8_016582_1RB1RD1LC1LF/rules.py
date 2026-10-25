import re
from lit import parse,M
T=parse(M)
def build(kind,a,b=0,k=0):
    d='100'
    if kind=='P': s='0'+d*a+'10'+d*b+'1'*k
    elif kind=='Q': s='0'+d*a+'10'+d*b+'101'+'1'*k
    elif kind=='X': s='0'+d*a+'1'*k
    return s
PR=re.compile(r'^0((?:100)*)10((?:100)*)(1*)$')
QR=re.compile(r'^0((?:100)*)10((?:100)*)101(1*)$')
XR=re.compile(r'^0((?:100)*)(1*)$')
def classify(st):
    m=QR.match(st)
    if m: return ('Q',len(m.group(1))//3,len(m.group(2))//3,len(m.group(3)))
    m=PR.match(st)
    if m: return ('P',len(m.group(1))//3,len(m.group(2))//3,len(m.group(3)))
    m=XR.match(st)
    if m: return ('X',len(m.group(1))//3,len(m.group(2)))
    return ('?',st)
def run(st,maxsteps=10**6):
    """C at position 0 reading st[0]=0; run until state C at new left edge; returns (steps,st,result)"""
    tape={i:int(c) for i,c in enumerate(st)};p=0;s=2;lo=0;n=0
    while n<maxsteps:
        v=tape.get(p,0);r=T[(s,v)]
        if r is None: return n,None,'HALT'
        tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2];n+=1
        if p<lo:
            lo=p
            if s==2: 
                if lo==-1: pass
                return n,''.join(str(tape.get(i,0)) for i in range(lo,max(tape)+1)),classify(''.join(str(tape.get(i,0)) for i in range(lo,max(tape)+1)))
        if p<lo: lo=p
    return n,None,'TIMEOUT'
if __name__=='__main__':
    import itertools
    for kind in 'PQ':
      for a in range(0,7):
        for b in range(0,4):
          for k in range(0,7):
            n,st,res=run(build(kind,a,b,k))
            print(kind,a,b,k,'->',n,res)
    for a in range(0,6):
        for k in range(0,6):
            n,st,res=run(build('X',a,0,k)); print('X',a,k,'->',n,res)
