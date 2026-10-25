"""snapshots of a run from a B-form config at given steps.  snap.py LIST:A s1,s2,..  (or s0:ds:n)"""
import sys
from fw import *
from btrace import parse_list
_ts, A = sys.argv[1].rsplit(':', 1)
w, h, q = bword(parse_list(_ts), int(A))
sp = sys.argv[2]
if sp.count(':') == 2:
    s0, ds, n = map(int, sp.split(':')); steps = [s0 + i * ds for i in range(n)]
else:
    steps = [int(x) for x in sp.split(',')]
s = Server(M10, '-', 10 ** 9)
for st in steps:
    r = s.job(w, h, q, st)
    print(show(r[-1])[:int(sys.argv[3]) if len(sys.argv) > 3 else 330], flush=True)
    if r[-1]['kind'] == 'HALT':
        break
s.close()
