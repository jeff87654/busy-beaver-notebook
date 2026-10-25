"""lf34.py ROW 'DS' b N : lockstep eng34 vs literal from a given a=0 state; prints kinds sequence summary and final state."""
import sys, subprocess
from drv import SIM
from gk import gruns, gword
from rp import dec34, vs, ROWS, parse
import eng34
row = int(sys.argv[1]); ds = parse(sys.argv[2]); b = int(sys.argv[3]); N = sys.argv[4]; M = ROWS[row - 1]
runs = [2 * v + m for v, m in ds] + [0, 2 * b + 2]
w = gword(runs, 2)
p = subprocess.Popen([SIM, M, '1', 'A', w, str(len(w)), N, 'A', '100000000'], stdout=subprocess.PIPE, text=True)
strip = lambda d: d[next((i for i, x in enumerate(d) if x != (0, 0)), len(d)):]
st = (ds, b); ok = 0; seq = []; mism = None; tail = ''
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] != 'E' or len(s) < 3: tail = l.strip(); continue
    r, z = gruns(s[2])
    if z != 2: continue
    d = dec34(r)
    if d is None or d[1] != 0: continue
    cur = (d[0], d[2])
    nx = eng34.step(*st)
    while nx is not None and not strip(nx[0]): seq.append('empty'); nx = eng34.step(nx[0], nx[1])
    if nx is None or (strip(nx[0]), nx[1]) != (strip(cur[0]), cur[1]):
        mism = (s[1], None if nx is None else (vs(nx[0])[:50], nx[1]), (vs(cur[0])[:50], cur[1])); p.kill(); break
    if not seq or seq[-1] != nx[2]: seq.append(nx[2])
    ok += 1; st = cur
print('ok', ok, 'mism', mism, 'end', tail[:25], '| kinds:', ' '.join(seq[-12:]), '| final', vs(st[0])[:60], st[1] if st[1] < 10**12 else 'big')
