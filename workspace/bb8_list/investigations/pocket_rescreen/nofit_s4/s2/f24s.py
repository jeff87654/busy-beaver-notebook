import re,sys
from val import probe
m=sys.argv[1] if len(sys.argv)>1 else '1RB1RA_0LC0RG_1LE1LD_1LC0LB_0RF1RD_1RB1RD_1RE0RH_1RA---'
def c(t): return re.sub(r'(01){2,}',lambda q:'(01)^%d '%(len(q.group(0))//2),t.strip('0'))
def S(n,maxev=200000,maxsteps=2*10**9,verbose=False):
    cf='F 1'+'01'*n+'|0'; tot=0
    for i in range(maxev):
        r=probe(m,'F','R',[cf],maxsteps-tot)[0]
        if r[0]!='S': return (r[0],tot+r[1],i)
        tot+=r[1]
        if r[4].strip('0'): return ('Rjunk',tot)
        g=re.fullmatch(r'0*1((?:01)+)',r[2])
        if g and i>0: return ('S',len(g.group(1))//2,tot,i)
        if verbose and i<verbose: print(i,tot,c(r[2]))
        cf='F '+r[2]+'|'+r[4]
        if tot>=maxsteps: return ('T',tot,i)
    return ('maxev',tot)
if __name__=='__main__':
    for n in range(int(sys.argv[2]),int(sys.argv[3])): print(n,S(n))
