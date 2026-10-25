"""s8sum.py: summarise world-mode outputs: per machine escalations (new-max-K count), halting, ones, max K."""
import sys, re
rows = []
for f in sys.argv[1:]:
    for l in open(f):
        if not l.startswith('CAND'): continue
        p = l.split(); m, tag = p[1], p[2]
        d = dict(x.split('=', 1) for x in p[3:] if '=' in x and not x.startswith('|'))
        ks = d['Ks']
        if ':' in ks: esc = int(ks.split(':')[0]); kl = ks.split(':')[1]
        else:
            k = [int(x) for x in ks.split(',') if x]; mx = 0; esc = 0; e = []
            for x in k:
                if x > mx: mx = x; esc += 1; e.append(x)
            kl = ','.join(map(str, e)) + ('+' if len(k) >= 12 else '')
        fin = 'HALT' if ' HALT ' in l else ('MAXS' if ' MAXS' in l else ('WIDE' if 'WIDE' in l else '?'))
        rows.append((esc, fin, int(d['ones']), int(d['maxK']), int(d['cl']), m, tag, kl))
rows.sort(key=lambda r: (-(r[1] == 'HALT'), -r[0], -r[2]))
from collections import Counter
print('total', len(rows), Counter((r[1], min(r[0], 9)) for r in rows))
for r in rows:
    print('%2d %-4s ones=%-7d maxK=%-6d cl=%-4d %s %s K:%s' % r)
