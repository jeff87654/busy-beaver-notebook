# realk2.py K R0 Rd maxcl : chain from the counter exit Kt(0,2,z2,1^(K-2);1;3*R0+2;6) (K = K6), later CLs with Rd.
# R0 = 2124366 (= real mod 2^4 3^2 5^5 7; parked list 12*R0 >> cascade consumption ~K/72), Rd = 324366 (= real mod 450000).
import idle, sys
from chain import chain
N = 61337390949400
K, R0, Rd, mx = map(int, sys.argv[1:5])
a = 0
while a < 14 and (K - 3 - N) % 5**(a + 1) == 0: a += 1
print(f'# K6={K} n=K6-3 agrees with the real n mod 5^{a}; n mod 6 = {(K-3)%6}; R0={R0} Rd={Rd}', flush=True)
chain(f'0,2,z2,1*{K-2};1;{3*R0+2};6', [R0], lambda i, r: Rd, mx, log=lambda s: print(s, flush=True))
