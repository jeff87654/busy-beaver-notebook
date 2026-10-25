# realk.py j m R maxcl : chain from the counter exit Kt(0,2,z2,1^(K-2);1;3R+2;6) with K = K6 in the real class mod 6*5^j
# (rep index m), every CL with accumulator R (R=366 is the real residue mod 18000 = lcm(3600,125)).
import idle, sys
from chain import chain
N = 61337390949400          # real n = K6 - 3 mod 5^12*64*81*77
j, m, R, mx = map(int, sys.argv[1:5])
mod = 6 * 5**j; K = (N + 3) % mod + m * mod
while K < 300: K += mod
print(f'# j={j} m={m} K6={K} (K6 mod 5^{j} = {K % 5**j}) R={R}', flush=True)
chain(f'0,2,z2,1*{K-2};1;{3*R+2};6', [], lambda i, r: R, mx, log=lambda s: print(s, flush=True))
