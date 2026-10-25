"""gtr.py M Q N [start] : print run-view of events (raw run lengths, z) from blank tape, events from step>=start, limited count"""
import sys, subprocess
from drv import SIM
from gk import gruns, vshow
m, q, N = sys.argv[1], sys.argv[2], sys.argv[3]; st0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0; lim = int(sys.argv[5]) if len(sys.argv) > 5 else 60
flt = sys.argv[6] if len(sys.argv) > 6 else ''
p = subprocess.Popen([SIM, m, '1', 'A', '-', '0', N, q, '100000000'], stdout=subprocess.PIPE, text=True)
c = 0; prevz = None
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] != 'E' or len(s) < 3:
        print(l.strip()[:100]); continue
    if int(s[1]) < st0: continue
    r, z = gruns(s[2])
    print(s[1], 'z%d' % z, vshow(r)[:150]); c += 1
    if c >= lim: p.kill(); break
