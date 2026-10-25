import sys, os, itertools
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import validate
pl.set_tm(TM)
R = rules()
bad = 0; n = 0
def chk(nm, vals):
    global bad, n
    s, t = R[nm]
    r = validate.reaches(s, t, vals, max_steps=200000)
    n += 1
    if r is None:
        bad += 1; print('FAIL', nm, vals)
for k, r_, y in itertools.product(range(0, 5), range(0, 5), range(0, 3)): chk('R3Am', {'k': k, 'r': r_, 'y': y})
for c, y in itertools.product(range(0, 8), range(0, 3)): chk('R3Bm', {'c': c, 'y': y})
for c, m, y in itertools.product(range(0, 5), range(0, 5), range(0, 3)): chk('R3Cm', {'c': c, 'm': m, 'y': y})
for c in range(0, 8): chk('R4m', {'c': c})
for a, b in itertools.product(range(0, 4), range(0, 5)): chk('R1m', {'a': a, 'b': b})
print('checked', n, 'bad', bad)
