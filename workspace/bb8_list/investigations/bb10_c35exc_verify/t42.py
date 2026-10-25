import engine, rules
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
engine.TRACE = engine.deque(maxlen=300000)
try:
    engine.R(s, top=True)
except rules.Unknown as e:
    pass
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
tr = list(engine.TRACE)
start = max(i for i, it in enumerate(tr) if it[1] == 6 and it[2] == 'S2')  # Q(2) S2
print('start index', start, 'total', len(tr))
prev = None; run_len = 0
for i in range(start, len(tr)):
    kind, ln, info, t = tr[i]
    key = (ln, info)
    if ln <= 5:
        if key == prev:
            run_len += 1; last = (i, kind, ln, info, t); continue
        if run_len > 0:
            print('   ... x%d, last:' % run_len, last[0], last[1], last[2], last[3], '|', fmt(last[4]))
        run_len = 0
    print(i, kind, ln, info, '|', fmt(t))
    prev = key
