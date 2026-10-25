import re
from absgrid import pred
cf=[]
for l in open('blank_traj.txt'):
    m=re.match(r'step (\d+) K\(([^;]*); (\d+); (\d+)\)',l)
    if m:
        ds=[int(x) for x in m.group(2).split(',')] if m.group(2) else []
        cf.append((int(m.group(1)),ds,int(m.group(3)),int(m.group(4))))
bad=0
for (s1,d1,a1,b1),(s2,d2,a2,b2) in zip(cf,cf[1:]):
    toks=[3*d+1 for d in d1]+[3*a1+1]; r=3*b1+2
    p=pred(toks,r)
    exp=([3*d+1 for d in d2]+[3*a2+1],3*b2+2)
    if p!=exp: bad+=1; print('MISMATCH',s1,s2,p,exp)
print(len(cf),'configs; consecutive pairs checked',len(cf)-1,'mismatches',bad)
