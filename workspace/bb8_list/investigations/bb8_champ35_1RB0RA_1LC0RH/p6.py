from kk import *
import sys
tail=U(4,'T')
Z=('run',(1,0,1),lin({'K':1}))
start=('G',tail+[1,1]+U(1)+[1]+[Z]+U(3,'X')+[1,V('l')],[BLANK],'>')
# target: K-1 zeros left: need K = K'+1 ; use start with one peeled zero digit
start=('G',tail+[1,1]+U(1)+[1,1,0,1]+[Z]+U(3,'X')+[1,V('l')],[BLANK],'>')
Z2=('run',(1,0,1),lin({'K':1}))
target=('G',U(2)+[1]+U(1)+[1]+U(1)+[1]+[Z2]+U(7,'T')+[1]+U(0,'X')+[1,V('l')],[BLANK],'>')
s,c=drive('R3K',start,target,maxev=300)
