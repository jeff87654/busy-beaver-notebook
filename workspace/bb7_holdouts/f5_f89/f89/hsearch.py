# literal search: which small K-configs (any digit parity) halt within 2e6 steps
import itertools,subprocess,os,collections
from run import tape,KL,M
env=dict(os.environ,U='01',NEV='0')
res=collections.Counter(); halts=[]
for L in range(1,5):
    for digs in itertools.product(range(0,8),repeat=L):
        p=subprocess.run([KL,M,'2000000','D','L','z',tape(list(digs))],capture_output=True,text=True,env=env)
        out=p.stdout
        odd=all(x%2 for x in digs)
        if 'HALT' in out:
            st=out.split('HALT')[1].split()[0]; halts.append((digs,int(st))); res[('HALT',odd)]+=1
        else: res[('NOHALT',odd)]+=1
print(res)
import json; json.dump(halts,open('hsearch.json','w'))
print('odd halting configs:',[h for h in halts if all(x%2 for x in h[0])][:10])
print('sample halts:',sorted(halts,key=lambda h:-h[1])[:8])
print('halt digit patterns (first even position):',collections.Counter(next(i for i,x in enumerate(d) if x%2==0) for d,_ in halts))
