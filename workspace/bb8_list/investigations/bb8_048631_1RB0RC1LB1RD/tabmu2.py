import random,sys
from randlist import run
random.seed(3)
a=int(sys.argv[1]); M=int(sys.argv[2])
def classify(a,m,u,res):
    a2,l=res
    s=2*m-u
    E=2*a+s+2
    # strip tail 38
    if l and l[-1]==38: l=l[:-1]
    else: return ('??',a2,l)
    if a2*2==E and l==(): return 'P'          # pending (E/2;)
    if a2==3 and l==(E-6,): return 'c3'
    if a2==2 and l==(E-4,): return 'c2'
    if a2==2 and l==(1,E-5): return 'c1'
    return ('other',a2,l,E)
tab={}
for m in range(0,M+1):
    row=[]
    for u in range(0,m+1):
        pos=random.sample(range(m),u)
        P=tuple(1 if i in pos else 2 for i in range(m))
        r=run(a,P+(40,),900000000)
        assert r[0]=='std'
        row.append(classify(a,m,u,r[1]))
    tab[m]=row
import json
json.dump({m:[str(x) for x in row] for m,row in tab.items()},open('tabmu_a%d.json'%a,'w'))
# print compact: for each m, string of class for u=0..m
sym={'P':'P','c3':'3','c2':'2','c1':'1'}
for m in range(M+1):
    print('%2d '%m+''.join(sym.get(x,'?') if isinstance(x,str) else '?' for x in tab[m]))
