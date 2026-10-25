from fam8 import *
def OddC(cc, mc, tailR, run_c=True):
    """1 (11)^(c+cc) [B> 0 1^(4(m+mc)+3) <tailR>"""
    L=[1]+[1,1]*cc+([run((1,1),'c')] if run_c else [])+[BLANK]
    R=[0,1,1,1]+[1]*(4*mc)+[run((1,1,1,1),'m')]+tailR
    return ('B',norm_side(L),norm_side(R),'>')
if __name__=='__main__':
    tail=[0,1,1,run((1,),'y'),0,V('r')]
    s=OddC(1,0,tail)
    print(pl.show(s))
    script,end=drive('final',s,None,matchers=[pipe_matcher()],maxev=400,verbose=True)
