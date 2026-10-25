"""summarize.py: final per-row status over stages A, B, B2 (latest stage wins) -> final.tsv + counts."""
import glob, collections, os
fin = {}
for st in ('outA', 'outB', 'outB2'):
    for f in sorted(glob.glob(f'{st}/*.tsv') + glob.glob(f'{st}/*.tsv.tmp')):
        for l in open(f):
            p = l.rstrip('\n').split('\t')
            if len(p) > 6 and '_' in p[0]: fin[p[0]] = (st, p)
pf = set(l.strip() for l in open('../pool_pf7_multi.txt'))
c = collections.Counter(); reach = []
for m, (st, p) in fin.items():
    lg = float(p[3]); dec = int(lg)
    c[(p[2], dec, 'pf7' if m in pf else 'fail')] += 1
    if p[2] == 'HALT': reach.append((float(p[5]), m, p[6], p[7], st))
with open('final.tsv', 'w') as o:
    for m, (st, p) in fin.items(): o.write(m + '\t' + st + '\t' + '\t'.join(p[1:]) + '\n')
print('rows', len(fin))
for k in sorted(c): print(*k, c[k])
reach.sort()
with open('reachers.tsv', 'w') as o:
    for r in reach: o.write(f'{r[1]}\t{r[2]}\t{r[0]:.6e}\t{r[3]}\t{r[4]}\t{"pf7" if r[1] in pf else "fail"}\n')
print('reachers', len(reach))
dc = collections.Counter(int(__import__('math').log10(r[0])) for r in reach); print('by decade', sorted(dc.items()))
