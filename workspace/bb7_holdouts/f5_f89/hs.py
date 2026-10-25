# random small token configs -> which halt (first exploration of halting patterns)
import sys,random,subprocess
from mt import tape,KL
M=sys.argv[1]; N=int(sys.argv[2]); random.seed(int(sys.argv[3]) if len(sys.argv)>3 else 1)
halts={}
for it in range(N):
    A=random.choice([2,4,6,8,10,1,3,5])
    n=random.randint(0,4)
    tok=[str(A)]
    for i in range(n):
        tok.append(random.choice(['.','.','.','#']))
        d=random.choice([0,0,1,2,3,4])
        if d: tok.append(str(d))
    tok.append(random.choice(['.','']) ); tok.append('#')
    t=' '.join(x for x in tok if x)
    p=subprocess.run([KL,M,'200000','D','L','a',tape(t)],capture_output=True,text=True)
    out=p.stdout.splitlines()
    if out and out[-1].startswith('HALT'):
        halts[t]=out[-3:]
for t,o in sorted(halts.items()): print(t,' ||| ',' | '.join(x[:80] for x in o))
print(len(halts),'halts of',N)
