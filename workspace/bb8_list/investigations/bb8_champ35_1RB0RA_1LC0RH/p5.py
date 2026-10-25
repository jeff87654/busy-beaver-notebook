from kk import *
import sys
k=int(sys.argv[1])
tail=U(4,'T')
# start after rounds: tail, b-run empty (just seps), a-run (01)^1, then k zero digits, then digit (X+3)
digs=[(1,None)]*k+[(3,'X')]
start=('G',tail+[1,1]+U(1)+[1]+sum([U(*d)+[1] for d in digs],[])+[V('l')],[BLANK],'>')
# target
tdigs=[(1,None)]*(k-1)+[(7,'T'),(0,'X')]
target=('G',U(2)+[1]+U(1)+[1]+U(1)+[1]+sum([U(*d)+[1] for d in tdigs],[])+[V('l')],[BLANK],'>')
s,c=drive('R3k%d'%k,start,target,maxev=300)
