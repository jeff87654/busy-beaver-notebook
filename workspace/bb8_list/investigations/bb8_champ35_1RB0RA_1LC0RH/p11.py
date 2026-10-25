from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
st=('C',U(4,'T')+[1,0,1,1,BLANK],[0,1,0,1,1,0,1,R('J',Z),0,BLANK],'<')
try:
    s,c=drive('EXIT4',st,None,maxev=100)
    print(s)
except Halted as e:
    print('HALTED',e)
