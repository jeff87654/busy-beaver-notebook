import engine, rules
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
engine.BIGLEN = 1
engine.TRACE_BIG = engine.deque(maxlen=3000)
try:
    engine.R(s, top=True)
except rules.Unknown as e:
    pass
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
tr = list(engine.TRACE_BIG)
# show the last events with lists shown as their last 12 tokens and length
for item in tr[-70:]:
    kind, ln, info, t = item
    print(kind, ln, info, '|', fmt(t[-12:]))
