"""ana.py [trees/*.tsv]: summarise t12enum leaves.  Prints per-file leaf counts and the interesting leaves:
  HALT2   : HALT (undefined slot read) after >= 1 RSIG (restart), with the halt slot, stages, restart c's, left marks
  RS      : RS3 leaves (3 restarts, no halt) -- restarters
Left marks: 'IN' if lo >= -12 and mw >= -8 at the first RSIG (in-place, as inplace's screen), else 'OUT(lo,mw)'.
Free slots = undefined slots other than the halt slot."""
import sys, glob, re, collections
files = sys.argv[1:] or sorted(glob.glob('trees/*.tsv'))
tot = collections.Counter(); halt2 = []; rs3 = []
for fn in files:
    cnt = collections.Counter()
    for line in open(fn):
        f = line.rstrip('\n').split('\t')
        if len(f) < 6: continue
        M, kind, st, nrs, rss, extra = f
        cnt[kind] += 1
        rsl = [x.split(':') for x in rss.split()]
        if int(nrs) >= 1:
            s1, P1, c1, z1, lo1, mw1 = rsl[0]
            lo1 = int(lo1[2:]); mw1 = int(mw1[2:])
            mark = 'IN' if (lo1 >= -12 and mw1 >= -8) else f'OUT(lo{lo1},mw{mw1})'
            cs = ','.join(f'{x[0]}/{x[2]}' for x in rsl)
            nfree = M.count('---') - (1 if kind == 'HALT' else 0)
            if kind == 'HALT':
                halt2.append((M, extra.split()[0], st, cs, mark, nfree, fn))
            elif kind.startswith('RS'):
                rs3.append((M, cs, mark, M.count('---'), fn))
    tot.update(cnt)
    print(fn, dict(cnt))
print('TOTAL', dict(tot), 'leaves', sum(tot.values()))
print('\nHALT2 (halt after a restart):', len(halt2))
for h in halt2: print('  ', h[0][62:], 'halt', h[1], '@', h[2], 'RS', h[3], h[4], 'free', h[5])
print('\nRS3 restarters:', len(rs3), ' with free slots:', sum(1 for r in rs3 if r[3] > 0), ' OUT:', sum(1 for r in rs3 if r[2] != 'IN'))
if '-v' in sys.argv[0:0] or True:
    for r in rs3:
        if r[3] > 0 or r[2] != 'IN': print('  ', r[0][62:], 'RS', r[1], r[2], 'undef', r[3])
