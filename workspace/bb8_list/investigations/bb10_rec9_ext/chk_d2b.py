import fext, follow3 as F
from cend import Kt, PAD
s = fext.d2_input()
q, b = 2, 4
R1 = (5 * q + 30) // 4
w = F.word_of(F.inst(s, {'R1': R1, 'R2': 3 * b + 2}))
t, h, st = Kt([1] * (5 * q + 11) + [2, 4, 21, 4], 1, 3 * b + 2, 6)
k = t[PAD:h].lstrip('0')
print(w); print(k)
