import idle
"""cmp.py LIST PREFIX W1 W2 ...: per machine of LIST ("name machine"), the runs runs/<PREFIX><W>/<name>.txt side by side,
plus flags: M8EQ (zeros == M8's zeros in that world and |ones - M8 ones| <= 2), M8PRE (zeros start with M8's zeros and
continue), SAME (identical zeros in all worlds where B does not enter: compared after dropping the B-linear 2nd entry
is NOT done; plain equality), ups per world.  Output tsv on stdout."""
import sys
from summ import parse, comp
lst, pre, ws = sys.argv[1], sys.argv[2], sys.argv[3:]
M8 = {w: parse('runs/%s/m8.txt' % w.replace(pre, '')) for w in ws}
CTL = {'F': '../bb9_redir/runs/m8_F.txt', 'W2': 'runs/W2/m8.txt', 'W3': 'runs/W3/m8.txt'}
M8 = {w: parse(CTL[w]) for w in ws}
for l in open(lst):
    n, m = l.split()[:2]
    ds = [parse('runs/%s%s/%s.txt' % (pre, w, n)) for w in ws]
    flags = []
    for w, d in zip(ws, ds):
        if d is None: flags.append('-'); continue
        mz = M8[w]['zs']; f = ''
        if d['zs'] == mz and d['ones'] and abs(int(d['ones']) - int(M8[w]['ones'])) <= 2: f = 'M8EQ'
        elif len(d['zs']) > len(mz) and d['zs'][:len(mz)] == mz: f = 'M8PRE'
        flags.append(f or '.')
    zz = [tuple(d['zs']) for d in ds if d]
    same = 'SAME' if len(zz) == len(ws) and len(set(zz)) == 1 else ('same-out' if len(set(d['out'] for d in ds if d)) == 1 else 'DIFF')
    cells = ['-' if d is None else '%s|%s|u%d|t%d|%s' % (d['out'], d['ones'], d['ups'], d['t'], comp(d['zs'])) for d in ds]
    print('\t'.join([n, m, same, ','.join(flags)] + cells))
