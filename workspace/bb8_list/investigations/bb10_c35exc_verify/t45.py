import time, engine, rules, oracle
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
q = (3 * T - 8)  # numerator; q = (3T-8)/5
assert (3 * T - 8) % 5 == 0 or True
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
P = [2, 1, 1, 0, 2, 1, 0, 1]
# real residues: q = (3T-8)/5 mod M needs T mod 5M
T5 = tower_res(5 * M)
qr = ((3 * T5 - 8) % (5 * M)) // 5
X1 = H(6 * qr - 1)
A = H(3 * T - 6)
for ones in (2, 3, 6):
    engine.memo.clear()
    s = P + [X1, 3] + [1] * ones + [A] + [1] * 36 + [0, 6]
    t0 = time.time()
    try:
        r = engine.R(s, top=True)
        print('ones=%d RESULT' % ones, fmt(r))
    except rules.Unknown as e:
        print('ones=%d UNKNOWN' % ones, str(e).split(' | ')[0][:70], '| list tail:', fmt(getattr(e, 'lst', []))[-80:])
    print('   X1 mod 3 =', res(X1, 3), ' A mod 3 =', res(A, 3), ' time %.1f' % (time.time() - t0))
