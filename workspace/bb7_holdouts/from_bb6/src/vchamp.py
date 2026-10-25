import sys; sys.path.insert(0, '.')
from tm import *
M = parse('1RB1RA_1RC1RZ_1LD0RF_1RA0LE_0LD1RC_1RA0RE')
def LC(n, x):
    s = ''
    for _ in range(n): s = ('111' if x % 2 == 0 else '100') + s; x //= 2
    return s
def S1(len0, a0, m, a, b):
    left = '111011' + LC(len0, a0) + '100' + '10' + '1' * m + LC(a, 0)
    return left, '0' + '11100' + '111' * (1 + b)
L, R = S1(3, 7, 2, 6, 63); target = L + R
def stop(T, p, q, t, lo, hi, off):
    if q != 'D': return False
    a = lo
    while T[a] == 0: a += 1
    b = hi
    while T[b] == 0: b -= 1
    if b - a + 1 != len(target): return False
    s = ''.join(str(T[i]) for i in range(a, b + 1))
    return s == target and p - a == len(L) - 1
r = run(M, maxsteps=10**7, stop=stop)
print(r[0], r[1], 'head offset ok' if r[0] == 'STOP' else '')
