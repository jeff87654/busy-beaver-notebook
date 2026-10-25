import sys
from tr import *
def kword(n,b):
    D=lambda m:'10'*m+'1'
    return '11'+D(1)*(n+1)+'10'*(3*b+2)+'111001'
def run_find(word, targets, maxs):
    t=parse(M); tp={}; 
    for i,ch in enumerate(word): tp[i]=int(ch)
    p=len(word); q=1; hi=len(word)-1; lo=0
    found={}
    for st in range(maxs):
        c=tp.get(p,0); tr=t[(q,c)]
        if tr is None: found['HALT']=st; break
        tp[p]=tr[0]; p+=tr[1]; q=tr[2]
        if p>hi: hi=p
        if p<lo: lo=p
        if q==1 and p>=hi and tp.get(p,0)==0:
            # snapshot: build string without leading/trailing zeros
            s=''.join(str(tp.get(i,0)) for i in range(lo,hi+1)).strip('0')
            for name,tg in targets.items():
                if name not in found and s==tg: found[name]=st+1
        if len(found)==len(targets): break
    return found
for n in range(0,5):
    for b in range(0,4):
        tg={'M2':'10'*(6*b+4)+'0'+'111'+'001'*(n+3)}
        print(n,b,run_find(kword(n,b),tg,60000+20000*b))
