from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
# HOP: head C in mode '<' at first cell of L.  
def hop_start():
    L=[R('T'),1,0,1,1]+[1,0,1]+[R('M',Z)]+U(3,'X')+[1,V('l')]
    Rr=[0,1,0,1,R('j',Z),0,BLANK]
    return ('C',L,Rr,'<')
def hop_target():
    L=[R('T'),1,0,1,1]+[R('M',Z)]+U(3,'X')+[1,V('l')]
    Rr=[0,1,0,1,1,0,1,R('j',Z),0,BLANK]
    return ('C',L,Rr,'<')
s,c=drive('HOP',hop_start(),hop_target(),maxev=100)
print(s)
