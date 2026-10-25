from kk import *
import sys
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
pe=int(sys.argv[1])
Q0=[1,0,0,1,0,0,1,R('J',(0,0,1)),0,1,0,BLANK]
st=('C',[1,1,BLANK],[1,0,1]*pe+[R('t',Z)]+Q0,'<')
try:
    s,c=drive('FIN',st,None,maxev=100,verbose=True)
except Halted as e: print('HALTED',str(e)[:300])
