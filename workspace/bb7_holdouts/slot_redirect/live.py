"""live.py FILE: count rows by number of undefined slots whose state is entered by some transition (or is A for A0)."""
import sys, collections
c = collections.Counter()
for l in open(sys.argv[1]):
    m = l.split()[0]; st = m.split('_')
    tgt = {t[2] for s in st for t in (s[:3], s[3:]) if t != '---'}
    und = [(i, j) for i, s in enumerate(st) for j in (0, 1) if s[3*j:3*j+3] == '---']
    live = [(i, j) for i, j in und if chr(65 + i) in tgt or (i == 0 and j == 0)]
    c[(len(und), len(live))] += 1
for k in sorted(c): print('undefined', k[0], 'live', k[1], c[k])
