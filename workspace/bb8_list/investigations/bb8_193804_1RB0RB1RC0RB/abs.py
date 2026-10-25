# abstract H-event system: left string l (nearest head last), right digit list ds (head on first sep 0)
import re, sys
def step(l, ds):
    d=ds
    if d[0]==3 and len(d)>1 and d[1]>=1: return 'R1', l+'0', [3,d[1]-1]+d[2:]
    if d[0]==3 and len(d)>1 and d[1]==0: return 'R2', l+'01', [0,1]+d[2:]
    if d[0]==0 and len(d)>2 and d[1]==3 and d[2]>=1: return 'R4', l+'01', [3,d[2]-1]+d[3:]
    if d[0]==0 and len(d)>2 and d[1]==1:
        m=re.search(r'0001((01)*)$',l)
        if not m: return 'STUCK-L', l, ds
        k=len(m.group(1))//2
        if k%2: return 'STUCK-ODD', l, ds
        mm=k//2; lp=l[:m.start()]
        if d[2]>=1: return 'R3', lp, [3]*(mm+2)+[d[2]-1]+d[3:]
        else: return 'R5', lp+'1', [0]+[3]*(mm+1)+[1]+d[3:]
    return 'STUCK', l, ds
def enc(l,ds):
    # tape string with head marker
    r=''.join('0'+'1'*x for x in ds)
    return l, r
if __name__=="__main__":
    l='0'*10+'1'; ds=[0,0,3,3,3,1,0,0,0]
    pass
