import subprocess
from f68eng import parse
KL=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\f5_f89\kl2.exe'
M='1RB1RE_0LC0LD_1RF0LD_1LE1LB_1RA1RG_1RE---_0RC0RF'
def content(st):
    A,L,c=st
    s='10'*A+'0'+''.join('10'*d+'0' for d in L[:-1])+'10'*L[-1]+'1'
    if c>=0: s+='10'*c+'1'
    return s
def litnext(st,steps=3000000):
    p=subprocess.run([KL,M,str(steps),'D','L','a','D00'+content(st)],capture_output=True,text=True)
    for l in p.stdout.splitlines():
        if l.startswith('HALT'): return 'HALT'
        if l.startswith('LIMIT'): return 'LIMIT'
        a=l.split(None,1)
        if len(a)==2:
            r=parse(a[1])
            if r is not None: return r
    return 'NONE'
