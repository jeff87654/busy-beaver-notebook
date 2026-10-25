# kres.py: the J1..J6 bookkeeping with real tower residues (exact mod M), checking every branch condition.
import idle
from towmod import Rres
M = 5**14 * 2**8 * 3**6 * 7 * 11 * 13
r = Rres(M * 25)           # B and every R_i (2R+4 a tall 2-tower)
MM = M * 25
def div5(x):
    assert x % 5 == 0, x % 5
    return x // 5
K1 = 11
print('B=R mod 5,25,125,3:', r % 5, r % 25, r % 125, r % 3)
assert K1 % 5 == 1 and r % 5 == 1
K2 = div5(27*r + 3*K1 + 10)                 # ETOP1 -> view 0 1 (K2+5) 1*(K2-1), CL X = K2+5
print('K2 mod 5 =', K2 % 5, ' X2=K2+5 mod 3 =', (K2+5) % 3)
n2 = K2 - 1                                 # E01 on 0,1,1^n2
K3 = 12*r + n2 + 5                          # view 0*2 7 1*K3 ; CL X=7
print('K3 mod 5 =', K3 % 5)
K4 = div5(27*r + 3*K3 + 10)                 # needs K3 = 1 mod 5
print('K4 mod 5 =', K4 % 5, ' X4=K4+5 mod 3 =', (K4+5) % 3)
K5 = 12*r + (K4 - 1) + 5
print('K5 mod 5 =', K5 % 5)
K6 = div5(27*r + 3*K5 + 44)                 # ETOP3 needs K5 = 3 mod 5 ; view 0*2 1 7 z2 (K6-12) 1*K6
print('K6 mod 5 =', K6 % 5, ' X6=K6-12 mod 3 =', (K6-12) % 3, ' 6R+12 mod 3 =', (6*r+12) % 3)
n = K6 - 3
print('n = K6-3 mod 5^12*64*81*77 =', n % (5**12*64*81*77), ' (expected 61337390949400)')
print('K6 mod 6*5^10 =', K6 % (6*5**10))
