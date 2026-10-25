"""gfit.py M Q N : record blank-tape events, grid-search geng2 params maximizing a=0-event lockstep; print best few."""
import sys, subprocess, itertools, json
from drv import SIM
from gk import gruns
import geng2 as G
M, Q, N = sys.argv[1], sys.argv[2], sys.argv[3]
p = subprocess.Popen([SIM, M, '1', 'A', '-', '0', N, Q, '5000000'], stdout=subprocess.PIPE, text=True)
EV = []; tail = ''
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] == 'E' and len(s) == 3: EV.append((int(s[1]),) + gruns(s[2]))
    else: tail = l.strip()
zs = sorted(set(e[2] for e in EV))
def score(F):
    st = None; ok = 0; r4 = 0
    for stp, runs, z in EV:
        if z != F['z']: continue
        d = G.dec(F, runs)
        if d is None or d[1] != 0 or len(d[0]) < 3: continue
        if st is None: st = d; continue
        if all(v == 0 for v, _ in st[0]): r4 += 1
        n = G.macro(F, *st)
        if n is None or (n[0], n[2]) != (d[0], d[2]): return ok, r4, stp
        st = n; ok += 1
    return ok, r4, None
res = []
for z, A0, B0, dl, c2, c3, a3, c4, dt in itertools.product(zs, [0, 1, 2], [0, 1, 2, 3, 4], [0, 1], [0, 1, 2, 3], [-2, -1, 0, 1, 2], [1, 2, 3], [-1, 0, 1, 2], [0, 1]):
    F = dict(z=z, A0=A0, B0=B0, dl=dl, c2=c2, c3=c3, a3=a3, c4=c4, droptop=dt)
    sc = score(F)
    if sc[0] > 3: res.append((sc, F))
res.sort(key=lambda x: -x[0][0])
print('events', len(EV), 'end', tail[:40])
for sc, F in res[:4]: print(sc, json.dumps(F))
