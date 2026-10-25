"""summ.py DIR: one line per follower log: leaf suffix | jumps | outcome | zeros head | max k | cycle"""
import sys, os, re, subprocess
from collections import Counter
D = sys.argv[1]; rows = []
for f in sorted(os.listdir(D)):
    if not f.startswith('L_'): continue
    s = open(os.path.join(D, f)).read(); m = f[2:-4]
    J = [l for l in s.splitlines() if l.startswith('J')]
    out = next((l for l in s.splitlines() if l.startswith(('HALT', 'STOP', 'NOJ1'))), 'RUN-LIMIT')
    z = next((l[7:] for l in s.splitlines() if l.startswith('zeros')), '')
    ks = [int(x) for x in re.findall(r'k=(\d+)', s)]
    rows.append((m[28:], len(J), ' '.join(out.split()[:2]), z[:70], max(ks) if ks else 0))
for r in rows: print('%s | J=%d | %s | %s | maxk=%d' % r)
print(Counter(r[2] for r in rows))
