from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
st=('G',[R('T')]+[1,1]+U(1)+[1,BLANK],[BLANK],'>')
try:
    s,c=drive('N0',st,None,maxev=100,verbose=True)
    print(s)
except Halted as e: print('HALTED',str(e)[:300])
