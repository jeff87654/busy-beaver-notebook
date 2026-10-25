"""Orbit of the family from the blank tape, using the Coq-proved rules.
Phase starts P(1,T,s): after T Psteps the counter is 1^n with n = 18*3^T - 7 = 6j+5, j = 3^(T+1) - 2.
  s = 0: P00, Y4f, Y3f give P(1, 27j+46, 1) = P(1, 3^(T+4) - 8, 1)
  s = 1: P01 gives P(1, 3j+3, 0)        = P(1, 3^(T+2) - 3, 0)
"""
from math import log10
# exact small orbit
f = ('Y3', 0)
seq = []
def succ(f):
    k = f[0]
    if k == 'P':
        _, j, t, s = f
        if t > 0: return ('P', 3*j+4, t-1, s)
        return ('Y4', 3*j+4) if s == 0 else ('P', 1, 3*j+3, 0)
    if k == 'Y4': return ('Y3', 3*f[1]+3)
    if k == 'Y3': return ('P', 1, 3*f[1]+1, 1)
for i in range(8):
    seq.append(f); f = succ(f)
print('first family configurations:', seq)
T1 = 24
T2 = 3**28 - 8
j = 3**(T1+1) - 2
assert 27*j + 46 == T2
print('T1 = %d (s=0), n at end of phase 1 = 18*3^24-7 = %d' % (T1, 18*3**24-7))
print('T2 = 3^28 - 8 = %d (s=1)' % T2)
L = (T2 + 2) * log10(3)
print('T3 = 3^(T2+2) - 3 ~ 10^%.6f  (s=0)' % L)
print('log10 log10 T4 ~ log10(T3) + log10(log10 3) ~ %.6f  (a tower of 3s: tetration growth)' % (L + log10(log10(3))))
