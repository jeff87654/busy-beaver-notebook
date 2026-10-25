import idle, subprocess, random, sys
from collections import defaultdict
random.seed(int(sys.argv[1])); NC=int(sys.argv[2]); NK=sys.argv[3]
def odd(): return random.choice([1,1,1,1,3,3,5,7,9,11])
def even(): return random.choice([0,0,2,4,6,8])
def phase(S):
    if all(p%2==1 and q%2==1 for p,q in S): return 'O'
    return 'E'
starts=[]
for _ in range(NC):
    k=random.randint(1,6); ph=random.choice('OE')
    if ph=='E': k=max(k,2)
    S=[(odd(),odd()) for _ in range(k)]
    if ph=='E': S[0]=(even(),odd()); S[-1]=(even(),odd())
    for i in range(len(S)-1):
        if random.random()<0.5 and not(ph=='E' and i==0): S[i]=(1,1)
    starts.append(';'.join('%d,%d'%s for s in S))
out=subprocess.run(['./k2k.exe','20000000',NK],input='\n'.join(starts)+'\n',capture_output=True,text=True,creationflags=0x40).stdout
P=lambda s:[tuple(map(int,x.split(','))) for x in s.split(';')]
cur=None; groups=defaultdict(list)
for l in out.split('\n'):
    if l.startswith('IN'): cur=P(l.split()[1])
    elif 'K step' in l:
        nxt=P(l.split(':')[1].strip())
        S=cur; ph=phase(S); x,y=S[-1]
        # classify
        if (ph=='O' and x>=3) or (ph=='E' and x>=2): key=(ph,'acc')
        else:
            i=len(S)-2
            while i>=0 and S[i]==(1,1) and not (ph=='E' and i==0): i-=1
            j=len(S)-2-i
            if i<0: key=(ph,'exhaust')
            else:
                p,q=S[i]
                key=(ph,'donor%s'%('L' if i==0 else 'M'), 'q>=3' if q>=3 else ('q=1,p>=%d'%(3 if p>=3 else p) if q==1 else 'q=%d'%q), 'j=0' if j==0 else 'j>=1')
            groups[key].append((S,nxt,j if key[1]!='acc' and key[1]!='exhaust' else None))
        cur=nxt
for k,v in sorted(groups.items()):
    print(k,len(v))
    for S,N,j in v[:4]: print('    ',S,'->',N)
