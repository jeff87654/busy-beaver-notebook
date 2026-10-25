import engine, rules
from num import H, M, res, is_huge
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
for Ar in (0, 1, 2, 12345, 99991):
    engine.memo.clear()
    A = H(3 * 10**20 + Ar)
    try:
        engine.R([A] + [1] * 36 + [0, 6], top=True); print(Ar, 'RESULT?')
    except rules.Unknown as e:
        print('A res %d (mod3 %d):' % (Ar, res(A, 3)), fmt(e.lst)[-70:], ' tokens', len(e.lst))
