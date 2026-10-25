# thr.py: per rule type and j, the set of (even) A values where the engine rule FAILS literally (all 3 siblings)
import sys
from grid import litnext,MS
from f5eng import step,show
def cases(kind,j,A):
    if kind=='B': return [(A,tuple([0]*j+[4,2,0]),-1),(A,tuple([0]*j+[6]),-1),(A,tuple([0]*j+[3]),5)]
    if kind=='M': return [(A,tuple([0]*j+[1]),-1),(A,tuple([0]*j+[1]),7),(A,tuple([0]*j+[1]),1)]
    if kind=='T': return [(A,tuple([0]*j+[0]),-1),(A,tuple([0]*j+[0]),7),(A,tuple([0]*j+[0]),1)]
res={}
for kind in 'BMT':
    for j in list(range(0 if kind!='B' else 1,13))+[20]:
        bad=[]
        for A in range(2,2*j+24,2):
            for st in cases(kind,j,A):
                pred,r=step(st)
                for M,q,side in MS:
                    got=litnext(M,q,side,st,3000000)
                    if got!=pred: bad.append((A,st[2]))
        print(kind,j,'fail A (A,c):',sorted(set(bad)),flush=True)
