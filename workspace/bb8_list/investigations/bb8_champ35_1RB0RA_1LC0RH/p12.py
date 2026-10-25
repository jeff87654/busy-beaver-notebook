from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
st=('C',[R('T'),1,0,1,1,BLANK],[0,1,0,1,1,0,1,R('J',Z),0,BLANK],'<')
s,c=drive('EXIT4',st,None,maxev=100,verbose=False)
print(show(c))
q,L,Rr,mode=c
print(L[:3],len(L))
def trydrive(cfg,name):
    try:
        s,c=drive(name,cfg,None,maxev=100,verbose=True)
        print(s[-3:]); print(show(c))
    except Halted as e: print('HALTED',e)
# case T=0
L0=L[1:]
trydrive((q,L0,Rr,mode),'T0')
# case T=T'+1
L1=[0,1,R('T',(0,1))]+L[1:]
trydrive((q,L1,Rr,mode),'T1')
