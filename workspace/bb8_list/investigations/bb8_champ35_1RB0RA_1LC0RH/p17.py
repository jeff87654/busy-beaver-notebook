from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
L0=[1,0,1]
def hop(vl):
    st=('C',[R('T'),1,0,1,1]+[1,0,1]+[R('M',Z),vl],[0,1,0,1,R('j',Z),0,BLANK],'<')
    tg=('C',[R('T'),1,0,1,1]+[R('M',Z),vl],[0,1,0,1,1,0,1,R('j',Z),0,BLANK],'<')
    return st,tg
for vl in (V('l'),):
    st,tg=hop(vl); s,c=drive('HOP',st,tg,maxev=50,verbose=False); print('HOP ok',s[-1])
st=('G',[R('T')]+[1,1]+U(1)+[1,1,0,1]+[R('M',Z),V('l')],[BLANK],'>')
tg=('C',[R('T'),1,0,1,1]+[R('M',Z),V('l')],[0,1,0,1,1,0,1,0,BLANK],'<')
s,c=drive('ENTRY',st,tg,maxev=50,verbose=False); print('ENTRY ok',s[-1])
st=('G',[R('T')]+[1,1]+U(1)+[1,1,0,1]+[R('M',Z),V('l')],[BLANK],'>')
