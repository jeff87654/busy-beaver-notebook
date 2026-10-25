# kgsumm.py : summary of the template-fitted regrade (kg/grade_*.txt + backref kg/fitted_br*.txt), per slice
import glob, collections, re
br = {}
for f in glob.glob('kg/fitted_br*.txt'):
    for l in open(f):
        m = l.split()[0]; slots = re.findall(r"\('(\w+)', '(\w+)", l)
        br[m] = bool(slots) and all(s[1] == 'UNREACHABLE' for s in slots)
sl = {l.split('\t')[0]: l.split('\t')[1] for l in open('kg/fitted.tsv')}
grid, ver = {}, {}
for f in sorted(glob.glob('kg/grade_0*.txt')):
    for l in open(f):
        p = l.split()
        if p[0] == 'KGRID': grid[p[1]] = p[3]
        elif p[0] == 'KGSKIP': grid[p[1]] = 'SKIP'
        elif p[0] == 'R': ver[p[1]] = (p[3], int([x for x in p if x.startswith('kj=')][0][3:]))
C = collections.Counter()
for m, s in sl.items():
    g = grid.get(m, 'PENDING'); v = ver.get(m, ('PENDING', 0))
    cls = 'UNREACHABLE' if br.get(m) and v[0] != 'HALT' else v[0]
    C[(s, 'grid', g)] += 1; C[(s, 'verdict', cls)] += 1
    if v[0] == 'HALT': C[(s, 'halt', 'after jumps' if v[1] else 'no jump')] += 1
for k in sorted(C): print(f'{C[k]:6d}  {k[0]:7s} {k[1]:8s} {k[2]}')
print('backref UNREACHABLE total', sum(br.values()), 'of', len(br))
