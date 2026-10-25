from fam8e import *
if __name__=='__main__':
    tail=[0,1,BLANK]
    s=OddG(1,0,0,tail,c0=True)
    # remove i-run: rebuild
    L=[1,1,1,run((1,1),'c'),BLANK]
    R=[0,1,1,1,run((1,1,1,1),'m')]+tail
    s=('B',norm_side(L),norm_side(R),'>')
    print('--- final R4')
    script,end=drive('fin4',s,None,matchers=[pipe_matcher()],maxev=400,verbose=True)
