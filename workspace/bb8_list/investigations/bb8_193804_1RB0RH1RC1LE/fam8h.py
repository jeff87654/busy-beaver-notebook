from fam8 import *
def X_(mc, rest): 
    R=[0,0,1]+[1]*(4*mc)+[run((1,1,1,1),'m')]+rest
    return ('B',norm_side([BLANK]),norm_side(R),'>')
def Odd_(cc, mc, ic, tailR, run_c=True, run_i=True):
    L=[1]+[1,1]*cc+([run((1,1),'c')] if run_c else [])+[BLANK]
    R=[0,1,1,1]+[1]*(4*mc)+[run((1,1,1,1),'m')]+[0,1]*ic+([run((0,1),'i')] if run_i else [])+tailR
    return ('B',norm_side(L),norm_side(R),'>')
T3=[0,1,1,run((1,),'y'),0,V('r')]
T4=[0,1,BLANK]
if __name__=='__main__':
    print('ENT3'); drive('ENT3',X_(0,[0,1,run((0,1),'i')]+T3),Odd_(0,0,1,T3,run_c=False),matchers=[pipe_matcher()],verbose=True)
    print('ENT4'); drive('ENT4',X_(0,[0,1,run((0,1),'i')]+T4),Odd_(0,0,1,T4,run_c=False),matchers=[pipe_matcher()],verbose=True)
    print('EMPTY'); 
    tgt=('B',[BLANK],norm_side([0,0,1,0,1,1,1,1,1,run((1,1,1,1),'m'),0,1,BLANK]),'>')
    drive('EMPTY',X_(0,T4),tgt,matchers=[pipe_matcher()],verbose=True)
