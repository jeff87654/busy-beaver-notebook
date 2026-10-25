import sys, itertools, collections
from shapes import gvisits, rle, fmt
pats=collections.defaultdict(list)
import random
def feed(ds,a,b,maxvis=400,maxsteps=400000):
    vs=gvisits(ds,a,b,maxsteps=maxsteps,maxvis=maxvis)
    for (s1,t1),(s2,t2) in zip(vs,vs[1:]):
        if t1=='HALT' or t2=='HALT': continue
        # common suffix
        i=0
        while i<min(len(t1),len(t2)) and t1[-1-i]==t2[-1-i]: i+=1
        p1=t1[:len(t1)-i]; p2=t2[:len(t2)-i]
        # also include one token of context after
        key=(fmt(rle(p1)),fmt(rle(p2)))
        pats[key].append((s2-s1,len(t1),len(p1)))
for b in range(1,6):
    for j in range(1,6):
        if j==1: ds,a=(1,),1
        else: ds,a=(1,)+(0,)*(j-2)+(1,),0
        feed((1,2),0,b) if False else None
for ds in [(1,),(2,),(1,1),(0,2),(1,0,1),(0,0,1),(2,0,0,1)]:
    for a in (0,1,2):
        for b in (1,2,3,4):
            feed(ds,a,b)
for k,v in sorted(pats.items(),key=lambda kv:-len(kv[1])):
    steps=sorted(set(x[0] for x in v))
    print('%-28s -> %-28s n=%d steps %s'%(k[0],k[1],len(v),steps[:8]))
