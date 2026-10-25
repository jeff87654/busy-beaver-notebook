from fam import next_X
# value semantics: w = c-1 ; a = beta+1
def tonum(W,beta): return beta+1, tuple(w+1 for w in W)
def fromnum(a,cs): return a-1, tuple(c-1 for c in cs)
import sys
for k in range(0,5):
    for y in (0,1,2):
        for beta in (0,4,8):
            W=(0,)*k+(y+1,)
            a,cs=tonum(W,beta)
            r=next_X(a,cs,N=10**6)
            if r[0]=='X':
                print('beta',beta,'W',W,'->',fromnum(*r[1]),r[2])
            else: print('beta',beta,'W',W,'->',r)
