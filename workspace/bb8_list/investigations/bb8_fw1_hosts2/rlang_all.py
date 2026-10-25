import idle, json, collections
from rlang import halts
from fam import BASES
R=[r for r in map(json.loads,open('bf.jsonl')) if r['res'] in ('NONSTD-after-ABS','BLANK-T','ABS-NOTM')]
bh={}
for nm in ('B1','B2','B3','B4'):
    bh[nm]=set(h[0] for h in halts(BASES[nm][0],nm))
    print('base',nm,'halting cfgs',len(bh[nm]),flush=True)
cnt=collections.Counter()
for r in R:
    H=halts(r['m'],r['base']); new=[h for h in H if h[0] not in bh[r['base']]]
    k='NEWHALT' if new else 'nohalt-beyond-base'
    cnt[(r['base'],r['res'],k)]+=1
    if new: print(r['base'],r['res'],r['m'],len(new),new[:3],flush=True)
for k,v in sorted(cnt.items()): print(k,v)
