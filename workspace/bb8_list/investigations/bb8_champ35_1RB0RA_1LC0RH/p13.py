from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
Q0=[1,0,0,1,0,0,1,R('J',(0,0,1)),0,1,0,BLANK]
# final T=0 case with symbolic t
st=('C',[1,1,BLANK],[R('t',Z)]+Q0,'<')
try:
    s,c=drive('FIN',st,None,maxev=100,verbose=True)
    print(s)
except Halted as e: print('HALTED',e)
# TLOOP
st=('C',[0,1,R('T',(0,1)),1,1,BLANK],[R('t',Z)]+Q0,'<')
tg=("C",[R("T",(0,1)),1,1,BLANK],[1,0,1,1,0,1,R('t',Z)]+Q0,'<')
try:
    s,c=drive('TLOOP',st,tg,maxev=100,verbose=True)
    print(s)
except Halted as e: print('HALTED',e)
