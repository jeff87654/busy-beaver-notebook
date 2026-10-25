"""fc14_scan.py TSV...: scan enum12 outputs for far-run counting candidates.
Prints DROP2 rows (>=2 successive kD2 decreases across recorded round starts), DROP1 rows
(one decrease), and a per-file leaf-kind tally.  A real outer counter needs DROP2 with the
same machine re-followed at other K (chk_eat.py / farfol.py)."""
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys

for fn in sys.argv[1:]:
    tally = {}
    hits = []
    for l in open(fn):
        x = l.rstrip('\n').split('\t')
        if len(x) < 4: continue
        M, kind, rss = x[0], x[1], x[3]
        tally[kind] = tally.get(kind, 0) + 1
        if kind not in ('EAT', 'RS', 'NOEND'): continue
        ks, cs, pls = [], [], []
        for e in rss.split():
            f = e.split(':')
            if len(f) != 6: continue
            ks.append(int(f[1])); pls.append(int(f[3])); cs.append(int(f[4]))
        ks0 = [29] + ks   # enum12 runs here all start at K = 29; the first eat is 29 -> ks[0]
        drops = sum(1 for i in range(len(ks0) - 1) if ks0[i + 1] < ks0[i])
        if drops >= 2:
            hits.append(('DROP2', M, ks, cs, pls))
        elif drops == 1:
            hits.append(('DROP1', M, ks, cs, pls))
    print(fn, tally, flush=True)
    for tag, M, ks, cs, pls in hits:
        print(tag, M, 'kD2', ks, 'c/mod14', [(c, c % 14) for c in cs], 'Plen', pls, flush=True)
