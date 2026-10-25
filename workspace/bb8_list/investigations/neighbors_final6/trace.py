"""Print the literal trace from a K configuration (shape F,0 or B,01) until the next K configuration.
   python trace.py TM ds a b [F,0] [every]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'neighbors_family_tools'))
import kfam
from tmlit import ST
tm = sys.argv[1]
ds = tuple(int(x) for x in sys.argv[2].split(',') if x != '')
a, b = int(sys.argv[3]), int(sys.argv[4])
if len(sys.argv) > 5 and ',' in sys.argv[5]:
    q, suf = sys.argv[5].split(','); kfam.set_shape(q, suf)
s = kfam.kstart(tm, ds, a, b)
print(0, s.show())
while True:
    if not s.step():
        print('HALT', s.steps, s.show()); break
    print(s.steps, s.show())
    r = kfam.parse_at(s)
    if r is not None:
        print('K', r); break
    if s.steps > 3000: break
