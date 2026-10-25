"""Reset recurrence W(0, M) -> ... -> W(0, M') with M' = 12*2^M - 5, and magnitudes (both machines)."""
from math import log10
M = [9]
M.append(12 * 2**M[0] - 5)
M.append(12 * 2**M[1] - 5)
lM2 = log10(12) + M[1] * log10(2)
print('M0 = %d, M1 = %d' % (M[0], M[1]))
print('M2 = 12*2^6139 - 5 has %d decimal digits (log10 M2 = %.4f)' % (len(str(M[2])), lM2))
print('log10 M3 ~ M2*log10(2) = 10^%.4f, i.e. M3 ~ 10^10^%.1f; M4 ~ 10^10^10^%.1f (tower of 2s)' % (lM2 + log10(log10(2)), lM2 + log10(log10(2)), lM2 + log10(log10(2))))
print('phase r (from W(0,M_r)): after t digit steps j_t = 2^(t+1)-2, i.e. about 0.30103*t decimal digits')
for dg, cpu in ((9291, 2), (17617, 10), (32862, 40)):
    print('%6d digits at %2d CPU-s <-> t = %.4g digit steps of the ~10^%.1f in phase 2' % (dg, cpu, dg / log10(2), lM2))
