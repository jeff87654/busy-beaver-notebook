import fext, follow3 as F
from cend import Kt, PAD
s = fext.d2_input()
print(F.fmt_sym(s))
for q, b in [(2, 4), (6, 9), (10, 3)]:
    if (5 * q + 30) % 4:
        print('skip', q); continue
    R1 = (5 * q + 30) // 4
    w = F.word_of(F.inst(s, {'R1': R1, 'R2': 3 * b + 2}))
    t, h, st = Kt([1] * (5 * q + 11) + [2, 4, 21, 4], 1, 3 * b + 2, 6)
    print(q, b, w == t[PAD:h].lstrip('0'))
