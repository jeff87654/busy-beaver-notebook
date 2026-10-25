"""gfit2.py M Q N : record blank-tape events (<=N steps), grid-search geng2 params (no R4 params) by a=0-event lockstep."""
import sys, subprocess, itertools, json
from drv import SIM
from gk import gruns
import geng2 as G
M, Q, N = sys.argv[1], sys.argv[2], sys.argv[3]
p = subprocess.Popen([SIM, M, '1', 'A', '-', '0', N, Q, '3000000'], stdout=subprocess.PIPE, text=True)
EV = []
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] == 'E' and len(s) == 3: EV.append((int(s[1]),) + gruns(s[2]))
from collections import Counter
zc = Counter(e[2] for e in EV)
def score(F):
    st = None; ok = 0; r4 = 0
    for stp, runs, z in EV:
        if z != F['z']: continue
        d = G.dec(F, runs)
        if d is None or d[1] != 0 or len(d[0]) < 2: continue
        if st is None: st = d; first = stp; continue
        if all(v == 0 for v, _ in st[0]): r4 += 1
        n = G.macro(F, *st)
        if n is None or (n[0], n[2]) != (d[0], d[2]): return ok, r4, stp
        st = n; ok += 1
    return ok, r4, None
res = []
for z in [z for z, _ in zc.most_common(2)]:
    for A0, B0, dl, c2, c3, a3 in itertools.product([0, 1, 2], [0, 1, 2, 3], [0, 1], [0, 1, 2, 3], [-2, -1, 0, 1, 2], [1, 2, 3]):
        F = dict(z=z, A0=A0, B0=B0, dl=dl, c2=c2, c3=c3, a3=a3, c4=0, droptop=0)
        sc = score(F)
        if sc[0] > 3: res.append((sc, F))
res.sort(key=lambda x: -x[0][0])
print('events', len(EV), 'z', dict(zc))
for sc, F in res[:5]: print(sc, json.dumps(F))
