import sys, subprocess
from drv import SIM
from gk import gruns
from rp56 import dec, vs, ROWS
import eng56
row = int(sys.argv[1]); N = sys.argv[2]; M = ROWS[row - 1]
p = subprocess.Popen([SIM, M, '1', 'A', '-', '0', N, 'B', '100000000'], stdout=subprocess.PIPE, text=True)
st = None; ok = 0; kinds = {}; mism = None; tail = ''; first = None
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] != 'E' or len(s) < 3: tail = l.strip(); continue
    r, z = gruns(s[2])
    if z != 1: continue
    d = dec(r)
    if d is None or d[1] != 0: continue
    cur = (eng56.norm(d[0]), d[2])
    if st is None: st = cur; first = (s[1], vs(cur[0]), cur[1]); continue
    nx = eng56.step(*st)
    if nx is None or (eng56.norm(nx[0]), nx[1]) != cur:
        mism = (s[1], None if nx is None else (vs(nx[0])[:50], nx[1]), (vs(cur[0])[:50], cur[1])); p.kill(); break
    kinds[nx[2]] = kinds.get(nx[2], 0) + 1; ok += 1; st = cur
print('row', row, 'first', first, 'ok', ok, kinds, 'mism', mism, 'end', tail[:25], 'final', vs(st[0])[:60], st[1])
