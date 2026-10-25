import idle, sys, re
from sim import T
S='ABCDEFG'
def build(segs):
    cells=[]
    for i,(p,q) in enumerate(segs):
        if i: cells+=[1,1]
        cells+=[0,1]*p+[1,0]*q
    return cells
def run(segs, maxs=10**6):
    cells=build(segs); off=10; tape={i+off:c for i,c in enumerate(cells)}
    pos=off+len(cells); tape[pos]=0; tape[pos+1]=1; q=0
    out=[]; lastkind=None
    for s in range(maxs):
        b=tape.get(pos,0); tr=T[(q,b)]
        if tr is None: out.append(('HALT',s)); break
        tape[pos]=tr[0]; pos+=tr[1]; q=tr[2]
        hi=max(tape)+1
        right=''.join(str(tape.get(j,0)) for j in range(pos,hi+1)).rstrip('0')
        # waypoint kinds
        kind=None
        if q==0:
            m=re.fullmatch(r'11((?:01)*)00((?:11)*)',right)
            if m: kind=('Wsep','c=%d'%(len(m.group(1))//2),'n=%d'%(len(m.group(2))//2))
            m=re.fullmatch(r'00((?:11)*)',right)
            if m: kind=('Wre','n=%d'%(len(m.group(1))//2))
            if right=='01' : kind=('K',)
        if q==5:
            m=re.fullmatch(r'((?:01)*)00((?:11)*)',right)
            if m and all(tape.get(j,0)==0 for j in range(min(tape)-2,pos)): kind=('Wb','c+1=%d'%(len(m.group(1))//2),'n=%d'%(len(m.group(2))//2))
        if kind:
            lo=min(k for k,v in tape.items() if v) if any(tape.values()) else pos
            left=''.join(str(tape.get(j,0)) for j in range(min(lo,pos),pos))
            out.append((s,kind,'left='+left[-80:]))
            if kind==('K',): break
    return out
segs=[tuple(map(int,x.split(','))) for x in sys.argv[1].split(';')]
for o in run(segs): print(o)
