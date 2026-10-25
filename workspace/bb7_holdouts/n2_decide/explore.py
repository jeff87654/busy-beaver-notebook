import idle, subprocess, random, sys
from collections import defaultdict
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 1)
def oddv(): return random.choice([1,1,1,3,3,5,7,9])
def evenv(): return random.choice([0,0,2,4,6])
starts=[]
for _ in range(150):
    k=random.randint(1,5)
    ph=random.choice('OE')
    segs=[]
    for i in range(k-1):
        segs.append((oddv() if (ph=='O' or i>0) else evenv(), oddv()))
    segs.append(((oddv() if ph=='O' else evenv()), oddv()))
    if random.random()<0.5:
        for i in range(len(segs)-1):
            if random.random()<0.6: segs[i]=(1,1) if (ph=='O' or i>0) else segs[i]
    starts.append(';'.join('%d,%d'%s for s in segs))
inp='\n'.join(starts)+'\n'
out=subprocess.run(['./k2k.exe','50000000','25'],input=inp,capture_output=True,text=True,creationflags=0x40).stdout
cur=None; trans=[]; bad=[]
for l in out.split('\n'):
    if l.startswith('IN'): cur=l.split()[1]
    elif 'K step' in l:
        nxt=l.split(':')[1].strip()
        if 'IRREG' in nxt: bad.append((cur,nxt)); cur=None; continue
        if cur: trans.append((cur,nxt))
        cur=nxt
    elif l.strip(): bad.append((cur,l.strip()[:200])); cur=None
def P(s): return [tuple(map(int,x.split(','))) for x in s.split(';')]
def ab(v): return str(v) if v<=3 else ('e' if v%2==0 else 'o')
shapes=defaultdict(list)
for a,b in trans:
    A=P(a);B=P(b)
    i=0
    while i<min(len(A),len(B))-1 and A[i]==B[i]: i+=1
    sa=A[i:]; sb=B[i:]
    key=('L' if i==0 else 'M')+' '+' '.join('(%s,%s)'%(ab(p),ab(q)) for p,q in sa)
    shapes[key].append((sa,sb))
for k,v in sorted(shapes.items()):
    print(k, len(v), '   e.g.', v[0][0],'->',v[0][1], '|', v[-1][0],'->',v[-1][1])
print('BAD',len(bad))
for x in bad[:20]: print(x)
