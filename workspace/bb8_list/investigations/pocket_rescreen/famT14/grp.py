import sys, subprocess, hashlib, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drv import SIM
from cmp import comp
rows = [l.split()[0] for l in open('rows16.txt') if l.strip()]
N = int(sys.argv[1]); Q = sys.argv[2] if len(sys.argv) > 2 else 'B'
for i, m in enumerate(rows):
    out = {}
    for q in 'ABCDEFGH':
        r = subprocess.run([SIM, m, '1', 'A', '-', '0', str(N), q, '3000000'], capture_output=True, text=True).stdout.splitlines()
        ev = [l for l in r if l.startswith('E')]
        out[q] = (len(ev), r[-1][:60])
    best = max(out, key=lambda q: out[q][0])
    last = out[best][1]
    r = subprocess.run([SIM, m, '1', 'A', '-', '0', str(N), best, '3000000'], capture_output=True, text=True).stdout.splitlines()
    ev = [l.split(None, 2) for l in r if l.startswith('E') and len(l.split(None, 2)) == 3]
    sig = hashlib.md5(' '.join(e[2] for e in ev[:3000]).encode()).hexdigest()[:8]
    print(i + 1, m, 'evq', best, 'nev', len(ev), 'sig', sig, '|', comp(ev[-1][2])[:90] if ev else '', '|', r[-1][:40])
