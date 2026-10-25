import re,sys
sys.argv=['x','1']
exec(open('grid.py').read().split('cases=[]')[0].split("which=sys.argv[1]")[0])
def pred(ds,a,b):
    ds=list(ds)
    if a>=1: return (ds,a-1,2*b+2)
    if not any(ds): return ([2]+[0]*(12*b+len(ds)+3),0,0)
    k=0
    while ds[-1]==0: ds.pop(); k+=1
    y1=ds.pop()
    if k==0: return (ds+[y1-1],2*b+2,0)
    return (ds+[y1-1,2*b+2]+[0]*(k-1),0,0)
prev=None;ok=0;bad=0
for line in open(sys.argv[1] if False else 'blank_traj_v1.txt'):
    m=re.match(r'step (\d+) K\((.*?); (\d+); (\d+)\)',line)
    if not m: continue
    ds=[int(x) for x in m.group(2).split(',')] if m.group(2) else []
    cur=(ds,int(m.group(3)),int(m.group(4)))
    if prev is not None:
        if pred(*prev)==cur: ok+=1
        else: bad+=1; print('MISMATCH',prev,cur)
    prev=cur
print('consecutive-config transitions matching the rules:',ok,'mismatches:',bad)
