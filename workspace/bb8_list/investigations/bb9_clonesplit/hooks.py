"""hooks.py: combine pairstat outputs into the hook table.  usage: python hooks.py ps_blank.tsv ps_stages.tsv"""
import sys, collections
rows = collections.defaultdict(dict)
segs = []
for fn in sys.argv[1:]:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if f[1] == '#END':
            segs.append(f[0]); continue
        lab, X, T, t, c, first = f
        rows[(X, T, t)][lab] = (int(c), int(first))
print('pair\tblank\t' + '\t'.join(s for s in segs if s != 'blank'))
for k in sorted(rows):
    d = rows[k]
    b = d.get('blank')
    cells = [f'{b[0]}@{b[1]}' if b else '-']
    for s in segs:
        if s == 'blank': continue
        v = d.get(s); cells.append(f'{v[0]}@{v[1]}' if v else '.')
    print(f'{k[0]}>{k[1]}:{k[2]}\t' + '\t'.join(cells))
