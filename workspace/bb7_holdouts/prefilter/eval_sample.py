"""eval_sample.py: pf7 verdicts (pf_sample/s_XX.tsv) against the lead's dlscan2 1% sample (../sample1pct/s_XX.tsv, finished files only)."""
import collections
from pathlib import Path
from analyze import load_pf
H = Path(__file__).resolve().parent
S = H.parent / 'sample1pct'
def done(p): return p.exists() and b'#summary' in open(p, 'rb').read()[-400:]
tot = collections.Counter(); per = collections.Counter(); misses = []
nfiles = 0
for o in sorted(S.glob('s_*.tsv')):
    pfp = H / 'pf_sample' / o.name
    if not (done(o) and done(pfp)): continue
    nfiles += 1
    pf = load_pf(pfp)
    tot['machines'] += len(pf); tot['pass'] += sum(r['verdict'] == 'PASS' for r in pf.values())
    for l in open(o):
        if l.startswith(('#', 'machine')): continue
        x = l.rstrip('\n').split('\t')
        if x[3] == '-': continue
        v = pf[x[0]]['verdict']
        per[(x[3], v)] += 1
        if v != 'PASS': misses.append((x[3], x[0], pf[x[0]]['span'], pf[x[0]]['CT2'], x[4]))
print(f'finished sample files: {nfiles}; machines {tot["machines"]}; pf7 PASS {tot["pass"]} ({100*tot["pass"]/max(1,tot["machines"]):.2f}%)')
for k, v in sorted(per.items()): print(' ', k, v)
for m in misses: print('  MISS', *m)
