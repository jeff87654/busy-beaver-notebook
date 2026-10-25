"""glock2.py M Q FJSON N [maxev]: blank-tape lockstep at a=0 events vs geng; reports first decoded a=0 state, matches, R4 count"""
import sys, subprocess
from drv import SIM, show
from gk import gruns
import json
import geng2 as G
enc, dec, macro = G.enc, G.dec, G.macro
M, Q = sys.argv[1], sys.argv[2]; F = json.loads(sys.argv[3]); sys.argv[3:4] = ['x', 'x', 'x']
N = sys.argv[6]; maxev = sys.argv[7] if len(sys.argv) > 7 else '50000000'
p = subprocess.Popen([SIM, M, '1', 'A', '-', '0', N, Q, maxev], stdout=subprocess.PIPE, text=True)
st = None; ok = 0; r4 = 0; mism = None; first = None; tail = ''; lastst = None
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] != 'E' or len(s) < 3: tail = l.strip(); continue
    runs, z = gruns(s[2])
    if z != F['z']: continue
    d = dec(F, runs)
    if d is None or d[1] != 0 or len(d[0]) < 2: continue
    if st is None: st = d; first = (s[1], show(enc(F, *d))); continue
    if mism: continue
    if not (st[0] and st[0][-1][0] > 0) and all(v == 0 for v, _ in st[0]): r4 += 1
    nst = macro(F, *st)
    if nst is None or (nst[0], nst[2]) != (d[0], d[2]):
        mism = (s[1], 'engine', None if nst is None else show(enc(F, *nst))[:90], 'literal', show(runs)[:90]); p.kill(); break
    st = nst; ok += 1; lastst = s[1]
print('first', first, '| ok', ok, 'R4', r4, '| mism', mism, '| end', tail[:50], '| last', lastst, show(enc(F, *st))[:100] if st else '')
