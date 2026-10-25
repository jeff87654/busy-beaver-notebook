import sys,subprocess
from f5eng import parse,show
KL=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\f5_f89\kl2.exe'
M='1RB1RE_0LC0LD_1RF0LD_1LE1LB_1RA1RG_1RE---_0RC0RF'
def content(st):
    A,L,c=st
    s='10'*A+'0'+''.join('10'*d+'0' for d in L[:-1])+'10'*L[-1]+'1'
    if c>=0: s+='10'*c+'1'
    return s
def nexts(st,steps=3000000,n=3):
    p=subprocess.run([KL,M,str(steps),'D','L','a','D00'+content(st)],capture_output=True,text=True)
    out=[]
    for l in p.stdout.splitlines():
        out.append(l[:120])
        if len(out)>=n: break
    return out
if __name__=='__main__':
    for s in sys.argv[1:]:
        st=eval(s); print(show(st),'||',' | '.join(nexts(st)))
