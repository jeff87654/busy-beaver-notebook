import engine, rules
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
engine.TRACE = engine.deque(maxlen=200000)
try:
    engine.R(s, top=True)
except rules.Unknown as e:
    pass
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
tr = list(engine.TRACE)
print('trace length', len(tr))
# find the last events with length >= 8 and print the final 60 of them plus their position
idx = [i for i, it in enumerate(tr) if it[1] >= 6]
for i in idx[-60:]:
    kind, ln, info, t = tr[i]
    print(i, kind, ln, info, '|', fmt(t))
