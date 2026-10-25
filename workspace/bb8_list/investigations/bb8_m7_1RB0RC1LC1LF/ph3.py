import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
pl.set_tm(M)
Ub=(0,1,0); Sb=(1,0,0); Vb=(1,1,0)
def toks(ts):
    out=[]
    for t in ts: out.extend({'U':Ub,'S':Sb,'V':Vb}[t])
    return out
def run(tok,var,const): return mkrun({'U':Ub,'S':Sb,'V':Vb}[tok],{var:1} if var else {},const)
def ruleAB(T,pi,pk,vi='i',vk='k',verbose=True):
    # start: U^(pi+vi) S^(pk+vk) T l  ; target per A/B with i=pi+vi,k=pk+vk
    st=[0]+run('U',vi,pi)+run('S',vk,pk)+toks(T)+[V('l')]
    # target: U S^(i-1) U^(k-1) [S V | ... ] for A ; U S^(i-1) U^k S for B
    # require pi>=1,pk>=1 so that i-1,k-1 are expressible as var+const
    tg=[0]+toks('U')+run('S',vi,pi-1)+run('U',vk,pk-1 if T=='U' else pk)
    tg+= toks('SV' if T=='U' else 'S')+[V('l')]
    start=('G',[BLANK],st,'>'); target=('G',[BLANK],tg,'>')
    return drive('A' if T=='U' else 'B',start,target,matchers=(),maxev=400,verbose=verbose)
if __name__=='__main__':
    T=sys.argv[1]; pi=int(sys.argv[2]); pk=int(sys.argv[3])
    ruleAB(T,pi,pk)

def ruleC(case,verbose=True):
    if case==3:   # i = I+3, k = K+1 ; target U^(I+1) S V^(K+2) S
        st=[0]+run('U','i',3)+run('S','k',1)+[BLANK]
        tg=[0]+run('U','i',1)+toks('S')+run('V','k',2)+toks('S')+[BLANK]
    else:         # i = 2, k = K+1 ; target U U S V^(K+1) S
        st=[0]+toks('UU')+run('S','k',1)+[BLANK]
        tg=[0]+toks('UUS')+run('V','k',1)+toks('S')+[BLANK]
    start=('G',[BLANK],st,'>'); target=('G',[BLANK],tg,'>')
    return drive('C%d'%case,start,target,matchers=(),maxev=400,verbose=verbose)
