"""Reset recurrence of W(0, M) -> ... -> W(0, M') with M' = 12*2^M - 5, and magnitudes."""
from math import log10
M = [3]
M.append(12 * 2**3 - 5)
M.append(12 * 2**M[1] - 5)
for r, v in enumerate(M):
    print('M%d = %d' % (r, v))
# during phase r (counter starting at W(0, M_r)): after t digit steps, j_t = 2^(t+1) - 2; ones = 6j+5 + (M_r - t)
L3 = M[2] * log10(2) + log10(12)
print('log10 M3 = %.6e' % L3)
print('phase starting at W(0,M2): j after t steps = 2^(t+1)-2, i.e. about 0.30103*t decimal digits')
# pipeline: 33,133 digits at 40 CPU-s
print('33,133 digits <-> t = %.3e of the %.3e digit steps in that phase' % (33133 / log10(2), M[2]))
