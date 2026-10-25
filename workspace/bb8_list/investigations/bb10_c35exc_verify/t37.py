import engine, rules
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
try:
    engine.R(s, top=True)
except rules.Unknown as e:
    print('stopped:', str(e)[:80])
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
print('top-level events:', len(engine.TRACE_TOP))
for kind, name, a, b in engine.TRACE_TOP:
    print(name, '|', fmt(a), '\n   ->', fmt(b))
