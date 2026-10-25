import time, engine, rules, oracle
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
s = [A] + [1] * 36 + [0, 6]
try:
    r = engine.R(s, top=True)
    print('RESULT', fmt(r))
except rules.Unknown as e:
    print('UNKNOWN', str(e)[:200])
tr = list(engine.TRACE_BIG)
for item in tr[-120:]:
    kind, ln, info, t = item
    # show only the part right of the first 'len' tokens: suffix of the full list of length ln
    print(kind, ln, info, '|', fmt(t))
