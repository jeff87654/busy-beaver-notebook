from kk import *
import sys
k=int(sys.argv[1]); pe=int(sys.argv[2])
tail=U(pe,'T')
digs=[(1,None)]*k+[(3,'X')]
start=('G',tail+[1,1]+U(1)+[1]+sum([U(*d)+[1] for d in digs],[])+[V('l')],[BLANK],'>')
tdigs=[(1,None)]*(k-1)+[(7-4+pe,'T'),(0,'X')]
target=('G',U(2)+[1]+U(1)+[1]+U(1)+[1]+sum([U(*d)+[1] for d in tdigs],[])+[V('l')],[BLANK],'>')
s,c=drive('R3k%d'%k,start,target,maxev=300)
