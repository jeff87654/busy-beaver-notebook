# t2summ.py : classify triage2 outputs (forward + reverse lanes, deduplicated)
import glob, collections, re
rows = {}
for f in sorted(glob.glob('t2_out_*.txt') + glob.glob('t2_outr_*.txt')):
    for l in open(f):
        m = l.split()[0]; rows.setdefault(m, l.rstrip('\n'))
sl = {l.split('\t')[0]: l.split('\t')[1] for l in open('../kg/fitted.tsv')}
C = collections.Counter(); ex = {}
for m, l in rows.items():
    if 'NOJUMP' in l or 'MULTISYM' in l: c = l.split()[1]
    else:
        rs = l.split(' || '); last = rs[-1]
        v = re.search(r'R(\d+):(\w+)', last)
        if v.group(2) == 'HALT': c = 'HALT round %s' % v.group(1)
        elif v.group(2) == 'CYCLE': c = 'CYCLE round %s' % v.group(1)
        elif v.group(2) == 'BUDGET' and len(rs) == 3: c = 'new clear every round (3 rounds)'
        else: c = '%s round %s (no further clear)' % (v.group(2), v.group(1))
    C[(sl.get(m, '?'), c)] += 1; ex.setdefault(c, m)
for k in sorted(C): print(f'{C[k]:5d}  {k[0]:7s} {k[1]}')
print(len(rows), 'machines'); [print('  e.g.', c, ex[c]) for c in ex]
