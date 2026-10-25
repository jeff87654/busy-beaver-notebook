"""sig.py: per machine: event counts per state Q (3e6 steps), z histogram for best Q, shape signature (first 400 events, numbers->#) -> sig.tsv"""
import sys, subprocess, hashlib, re
from collections import Counter
sys.path.insert(0, '.')
from drv import SIM
from gk import gruns
ms = [l.split()[0] for l in open('roots1043.txt')]
out = open('sig.tsv', 'w')
for i, m in enumerate(ms):
    best = None
    for q in 'ABCDEFGH':
        r = subprocess.run([SIM, m, '1', 'A', '-', '0', '3000000', q, '3000'], capture_output=True, text=True).stdout.splitlines()
        ev = [l.split(None, 2) for l in r if l.startswith('E ') and len(l.split(None, 2)) == 3]
        if best is None or len(ev) > len(best[1]): best = (q, ev, r[-1] if r else '')
    q, ev, last = best
    zs = Counter(); shp = []
    for e in ev[:400]:
        runs, z = gruns(e[2]); zs[z] += 1; shp.append(re.sub(r'\d+', '#', ' '.join(map(str, runs[-3:]))))
    sig = hashlib.md5('|'.join(shp).encode()).hexdigest()[:8]
    out.write('%s\t%s\t%d\t%s\t%s\t%s\n' % (m, q, len(ev), dict(zs), sig, last[:40])); out.flush()
