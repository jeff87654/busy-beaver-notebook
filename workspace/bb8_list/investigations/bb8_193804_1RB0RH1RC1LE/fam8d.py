from fam8 import *
from fam8c import OddC
def Xfin(rest, mode='>'):
    # X' : 0^inf B> 0 0 1 (01)^{c} 0 1 1 1 1 1 (1111)^m ...
    R=[0,0,1,run((0,1),'c'),0,1,1,1,1,1,run((1,1,1,1),'m')]+rest
    return ('B',norm_side([BLANK]),norm_side(R),'>')
if __name__=='__main__':
    tail=[0,1,1,run((1,),'y'),0,V('r')]
    s=OddC(1,0,tail)
    t=Xfin([0,1,run((1,),'y'),0,V('r')])
    print(pl.show(s)); print(pl.show(t))
    script,end=drive('final',s,t,matchers=[pipe_matcher()],maxev=400,verbose=True)
