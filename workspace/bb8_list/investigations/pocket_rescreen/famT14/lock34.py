"""lock34.py ROW N: blank-tape lockstep of eng34 at a=0 events (A=0)."""
import sys, subprocess
from drv import SIM
from gk import gruns
from rp import dec34, vs, ROWS
import eng34
row = int(sys.argv[1]); N = sys.argv[2]; M = ROWS[row - 1]
p = subprocess.Popen([SIM, M, '1', 'A', '-', '0', N, 'A', '100000000'], stdout=subprocess.PIPE, text=True)
st = None; ok = 0; kinds = {}; mism = None; tail = ''
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] != 'E' or len(s) < 3: tail = l.strip(); continue
    runs, z = gruns(s[2])
    if z != 2: continue
    d = dec34(runs)
    if d is None or d[1] != 0: continue
    cur = (d[0], d[2])
    if st is None:
        if len(cur[0]) >= 2: st = cur; first = (s[1], vs(cur[0]), cur[1])
        continue
    nx = eng34.step(*st)
    strip = lambda d: d[next((i for i, x in enumerate(d) if x != (0, 0)), len(d)):]
    while nx is not None and not strip(nx[0]):   # empty list: not an event; step again
        kinds['empty'] = kinds.get('empty', 0) + 1; nx = eng34.step(nx[0], nx[1])
    if nx is None or (strip(nx[0]), nx[1]) != (strip(cur[0]), cur[1]):
        mism = (s[1], 'exp', None if nx is None else (vs(nx[0])[:60], nx[1]), 'got', (vs(cur[0])[:60], cur[1])); p.kill(); break
    kinds[nx[2]] = kinds.get(nx[2], 0) + 1; ok += 1; st = cur; last = s[1]
print('row', row, 'first', first, 'ok', ok, kinds, 'mism', mism, 'end', tail[:30], 'last', last, vs(st[0])[:80], 'b', st[1] if st[1] < 10**9 else 'big')
