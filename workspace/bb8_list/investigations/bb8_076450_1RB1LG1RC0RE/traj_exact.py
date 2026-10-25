"""Independent check of the reset trajectory using pow(.,.,mod) with exactly known K3."""
from math import log10
N0 = 10
assert N0 % 6 == 4; K1 = (N0 - 1)//3            # reset 0: S(10,0,0) -> S(4,3,1)
N1 = (14*4**K1 - 2)//3; assert N1 == 298 and N1 % 6 == 4
K2 = (N1 - 1)//3; assert K2 == 99               # reset 1 -> S(4,99,2)
N2 = (14*4**K2 - 2)//3; assert (14*4**K2 - 2) % 3 == 0
print('N2 =', N2, ' N2 mod 6 =', N2 % 6)
assert N2 % 6 == 4
K3 = (N2 - 1)//3                                  # reset 2 -> S(4,K3,3)
print('K3 =', K3, ' (%d digits), K3 mod 27 = %d' % (len(str(K3)), K3 % 27))
MOD = 2 * 3**8
P = pow(4, K3, 3*MOD)
N3m = ((14*P - 2) % (3*MOD)) // 3                 # N3 mod MOD
assert (14*P - 2) % 3 == 0
print('N3 mod 6 =', N3m % 6)
assert N3m % 6 == 0
K4m = ((N3m - 6) // 3) % (MOD // 3)               # K4 mod 2*3^7
print('K4 mod 3 =', K4m % 3, ' K4 mod 2 =', K4m % 2)
P4 = pow(4, K4m % 3 + 3, 27)   # 4^K4 mod 27 needs K4 mod 9; use K4m (mod 2*3^7 covers 9)
P4 = pow(4, K4m % 9 + 9, 27)
N4m9 = ((44*P4 - 2) % 27) // 3                    # N4 mod 9
print('N4 mod 3 =', N4m9 % 3, '-> N4 mod 6 =', {0:0,1:4,2:2}[N4m9 % 3])
# sizes
L4 = log10(4)
lK3 = log10(K3)
log10_K4 = log10(14/9) + K3*L4       # K4 ~ (14/9) 4^K3
print('log10 K3 = %.6f' % lK3)
print('log10 log10 K4 = %.6f' % (log10(K3*L4) ))
print('sigma ~ (88/9) 4^K4 ;  log10 log10 log10 sigma ~ %.4f' % (log10(log10_K4) ))
