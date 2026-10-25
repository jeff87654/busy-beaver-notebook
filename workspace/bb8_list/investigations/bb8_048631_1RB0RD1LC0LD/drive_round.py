import sys, time
import planner9 as P
import fam9 as F
from planner9 import C
name = sys.argv[1]
if name == 'RA':
    start = F.PA(C(1, z=1), C(8, y=1), C(4, x=1))
elif name == 'RB':
    start = F.PB(C(1, z=1), C(7, y=1), C(2, x=1))
elif name == 'RC':
    start = F.PC(C(1, z=1), C(9, y=1), C(1, x=1))
tgtname = sys.argv[2] if len(sys.argv) > 2 else None
tgt = None
if tgtname:
    tgt = eval('F.' + tgtname)
t = time.time()
try:
    script, end = P.drive(name, start, tgt, matchers=[F.m_TL], maxev=20000, verbose=False, maxlit=int(sys.argv[3]) if len(sys.argv) > 3 else 400000)
    print('END', P.show(end))
    print('ops', len(script), 'literal', sum(o[1] for o in script if o[0] == 'steps'), 'time %.1f' % (time.time() - t))
except RuntimeError as e:
    print('ERR', e)
