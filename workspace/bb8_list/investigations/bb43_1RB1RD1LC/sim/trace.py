# trace.py "<left word>" <state><headsym> "<right word>" maxsteps  -- prints every step; blanks beyond
import sys
from psim import T
L=[int(c) for c in sys.argv[1].replace(' ','')]; q=ord(sys.argv[2][0])-65; h=int(sys.argv[2][1]); R=[int(c) for c in sys.argv[3].replace(' ','')]
n=int(sys.argv[4]); pad=40
tape=[0]*pad+L+[h]+R+[0]*pad; pos=pad+len(L)
for st in range(n+1):
    s=''.join(str(x) for x in tape[:pos])+'['+'ABCDZ'[q]+str(tape[pos])+']'+''.join(str(x) for x in tape[pos+1:])
    print(st, s.strip('0') if False else s[pad-8:])
    if q==25: break
    w,d,nq=T[(q,tape[pos])]; tape[pos]=w; pos+=d; q=nq
    if nq==25: print('HALT'); break
