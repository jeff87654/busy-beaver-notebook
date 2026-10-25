"""lockstep: literal blank-tape run of T (mirrored) vs micro-engine, from first K-config with nonempty ds."""
import sys
from drv import *
from eng import *
M = T2 if '-2' in sys.argv else T1
N = int(sys.argv[1]); maxev = int(sys.argv[2])
evs = []
for L in run('', N, maxev, M, q='A'):
    p = L.split(None, 2)
    if p[0] == 'E':
        r = toruns(p[2]); evs.append((int(p[1]), r))
    else: last = L
K = [(s, from_runs(r)) for s, r in evs if len(r) >= 3]
K = [(s, k) for s, k in K if isinstance(k[1], int) and isinstance(k[2], int) and k[0]]
while len(K[0][1][0]) < 10: K.pop(0)
i0 = 0
st = K[0][1]; ok = 0; mism = None
def micro(ds, a, b):
    if a > 0: return ds, a - 1, b + 2
    return step(ds, a, b)
for s, k in K[1:]:
    st = micro(*st)
    if st is None: mism = ('invalid', s); break
    if (list(st[0]), st[1], st[2]) != (list(k[0]), k[1], k[2]): mism = (s, show(to_runs(*st))[:80], show(to_runs(*k))[:80]); break
    ok += 1
print('K-configs', len(K), 'lockstep ok', ok, 'mismatch', mism, 'last literal', last[:60])
print('first', K[0][0], show(to_runs(*K[0][1])), ' last', K[-1][0], show(to_runs(*K[-1][1]))[:120])
