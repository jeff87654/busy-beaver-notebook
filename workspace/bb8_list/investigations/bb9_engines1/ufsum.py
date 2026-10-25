"""ufsum.py TAG...: categories of runs/ufc_TAG.tsv (literal 2e7 steps from the b=1 start):
HALT; TRANSLATED (an extent grows linearly, >= 0.2 cells/step over the second half); BOUNDED (extent constant over
the last 3/4); SLOW-a (sublinear growth, a = log2 of the growth ratio over the last doubling of time); halting rows
listed."""
import sys, collections, math
for tag in sys.argv[1:]:
    c = collections.Counter(); halts = []
    for l in open(f'runs/ufc_{tag}.tsv'):
        f = l.rstrip().split('\t')
        if f[1] != 'T': c['HALT'] += 1; halts.append(f[0] + ' ' + f[1]); continue
        pts = [tuple(map(int, x.split('/'))) for x in f[2][3:].split()]
        ext = [a + max(b, 0) for a, b in pts]
        if ext[2] - ext[1] > 0.2 * 10_000_000: c['TRANSLATED'] += 1
        elif ext[2] == ext[0]: c['BOUNDED'] += 1
        else:
            a = math.log2(ext[2] / ext[1]) if ext[1] > 0 else 9
            c['SLOW<0.75' if a < 0.75 else 'SLOW>=0.75'] += 1
    print(tag, dict(sorted(c.items())))
    for h in halts: print('   HALT', h)
