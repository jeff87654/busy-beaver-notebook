"""Raw-bit literal trace from a K configuration: python trace2.py TM ds a b SHAPE from to"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'neighbors_family_tools'))
import kfam
from tmlit import ST
tm = sys.argv[1]
ds = tuple(int(x) for x in sys.argv[2].split(',') if x != '')
a, b = int(sys.argv[3]), int(sys.argv[4])
q, suf = sys.argv[5].split(','); kfam.set_shape(q, suf)
lo_s, hi_s = int(sys.argv[6]), int(sys.argv[7])
s = kfam.kstart(tm, ds, a, b)
base = s.pos
def raw():
    t = s.tape; L = base - 30; H = base + 14
    return ''.join(('[%s%d]' % (ST[s.state], t[i])) if i == s.pos else str(t[i]) for i in range(L, H))
while s.steps <= hi_s:
    if s.steps >= lo_s: print('%4d %s' % (s.steps, raw()))
    if not s.step(): print('HALT'); break
    if kfam.parse_at(s) is not None: print('%4d %s K %r' % (s.steps, raw(), kfam.parse_at(s))); break
