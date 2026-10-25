from tower import tower_res, chain_depth
from num import M
N = 18101949465600
T2N = tower_res(2 * N)
B = ((T2N - 4) % (2 * N)) // 2
print('B mod N =', B, ' (bb8-ab: 16537583495166)', B == 16537583495166)
for m in (360, 16, 32, 64, 5, 7, 25, 27, 11, 13):
    print('  B mod %d = %d' % (m, B % m))
print('chain depth of M:', chain_depth(M), ' of 2N:', chain_depth(2 * N))
T = tower_res(M)
print('T mod 3,5,8,16,7 =', T % 3, T % 5, T % 8, T % 16, T % 7)
y = (3 * T - 8) % M
print('y = 3T-8: mod 3 %d, mod 5 %d, mod 8 %d' % (y % 3, y % 5, y % 8))
N2 = 54305848396800
tt = tower_res(3 * N2)
for name, val in [('(tau-2)/3?', None)]:
    pass
