from fam8 import *
tail=[0,1,BLANK]
L=[1,1,1,run((1,1),'c'),BLANK]
R=[0,1,1,1,run((1,1,1,1),'m')]+tail
s=('B',norm_side(L),norm_side(R),'>')
# target: 00 1 0 1 (01)^c 0 1^(4m+5) 0 1 0^inf
R2=[0,0,1,0,1,run((0,1),'c'),0,1,1,1,1,1,run((1,1,1,1),'m'),0,1,BLANK]
t=('B',norm_side([BLANK]),norm_side(R2),'>')
print(pl.show(t))
script,end=drive('fin4',s,t,matchers=[pipe_matcher()],maxev=400,verbose=True)
