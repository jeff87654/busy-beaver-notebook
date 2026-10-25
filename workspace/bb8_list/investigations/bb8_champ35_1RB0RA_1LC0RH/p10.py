from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
# R4 entry with n=M+1 zeros, b-run empty after rounds
st=('G',[R('T')]+[1,1]+U(1)+[1]+[1,0,1]+[R('M',Z)]+[BLANK],[BLANK],'>')
tg=('C',[R('T'),1,0,1,1]+[R('M',Z)]+[BLANK],[0,1,0,1,1,0,1,0,BLANK],'<')
s,c=drive('ENTRY4',st,tg,maxev=100)
print(s)
