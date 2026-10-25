from fam8 import *
def OddG(cc, mc, ic, tailR, c0=True):
    """1 (11)^(c+cc) [B> 0 1^(4(m+mc)+3) (01)^(i+ic) <tailR>"""
    L=[1]+[1,1]*cc+([run((1,1),'c')] if c0 else [])+[BLANK]
    R=[0,1,1,1]+[1]*(4*mc)+[run((1,1,1,1),'m')]+[0,1]*ic+([run((0,1),'i')] if ic is not None else [])+tailR
    return ('B',norm_side(L),norm_side(R),'>')
if __name__=='__main__':
    import sys
    tail=[0,1,BLANK]
    s=OddG(0,0,1,tail,c0=True)
    t=OddG(1,0,0,tail,c0=True)
    print(pl.show(s)); print(pl.show(t))
    script,end=drive('cyc4',s,t,matchers=[pipe_matcher()],maxev=400,verbose=True)
    s=OddG(1,0,0,tail)
    s=('B',s[1],s[2],'>')
    print('--- final R4')
    script,end=drive('fin4',s,None,matchers=[pipe_matcher()],maxev=400,verbose=True)
