from fam8 import *
def Odd(kc, mc, ic, rest):
    """1^(k+kc) [B> 0 1^(4(m+mc)+3) (01)^(i+ic) <rest>"""
    L=[1]*kc+[run((1,),'k')]+[BLANK]
    R=[0,1,1,1]+[1]*(4*mc)+[run((1,1,1,1),'m')]+[0,1]*ic+[run((0,1),'i')]+rest
    return ('B',norm_side(L),norm_side(R),'>')
if __name__=='__main__':
    tail=[0,1,1,run((1,),'y'),0,V('r')]
    s=Odd(0,0,1,tail); t=Odd(2,0,0,tail)
    print(pl.show(s)); print(pl.show(t))
    script,end=drive('cyc',s,t,matchers=[pipe_matcher()],maxev=400,verbose=True)
