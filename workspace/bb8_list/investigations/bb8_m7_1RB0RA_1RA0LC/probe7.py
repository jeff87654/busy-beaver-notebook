from batch import *
import itertools, sys
J=int(sys.argv[1]); tv=int(sys.argv[2])
cfgs=[]
for j in range(0,J+1):
    for w in itertools.product([0,1,2],repeat=j):
        for a in (0,1,2):
            for r in (2,5):
                cfgs.append(([tv]+list(w)+[a],r))
res=run(cfgs,tail='111001',N=5000000)
def win(pt,t):
    i=0
    while i<min(len(pt),len(t)) and pt[i]==t[i]: i+=1
    jj=0
    while jj<min(len(pt),len(t))-i and pt[-1-jj]==t[-1-jj]: jj+=1
    return pt[i:len(pt)-jj], t[i:len(t)-jj], i, jj
for t,r,x in res:
    if isinstance(x,tuple):
        a,b,i,jj=win(t,x[1])
        if len(x[1])>40: b=str(x[1][:5])+'..(%d)..'%len(x[1])+str(x[1][-4:])
        print(t,'r=%d'%r,'->',x[2], b if len(x[1])>40 else '%s => %s'%(a,b), 'steps',x[0])
    else: print(t,'r=%d'%r,'->',x)
