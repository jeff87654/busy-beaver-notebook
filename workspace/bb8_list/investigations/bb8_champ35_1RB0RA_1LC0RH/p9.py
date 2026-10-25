from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
# ENTRY: start (K=M+1 zeros)
def entry():
    st=('G',[R('T')]+[1,1]+U(1)+[1]+[1,0,1]+[R('M',Z)]+U(3,'X')+[1,V('l')],[BLANK],'>')
    # c-config M, j=1
    L=[R('T'),1,0,1,1]+[R('M',Z)]+U(3,'X')+[1,V('l')]
    tg=('C',L,[0,1,0,1,1,0,1,0,BLANK],'<')
    return st,tg
st,tg=entry()
s,c=drive('ENTRY',st,tg,maxev=100)
print(s)
# EXIT: from c-config M=0, j=J+1
L=[R('T'),1,0,1,1]+U(3,'X')+[1,V('l')]
st=('C',L,[0,1,0,1,1,0,1,R('J',Z),0,BLANK],'<')
# target: tail U(2),1,U(1),1,U(1),1, zeros^J , digit T+3 units, X
tg=('G',U(2)+[1]+U(1)+[1]+U(1)+[1]+[R('J',Z)]+U(3,'T')+[1]+U(0,'X')+[1,V('l')],[BLANK],'>')
s,c=drive('EXIT',st,tg,maxev=100)
print(s)
