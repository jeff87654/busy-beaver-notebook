"""chainsym.py K : symbolic (5-adic) run of the C04 exhaustion chains on the REAL n = 12B+25, using the decoded map
   L == 1,2,3,4 (mod 5): L -> (3L + 32, -46, -64, -52)/5 ;  L == 0: stop, z = (L-30)/5 zeros behind digit z+8
   chain #2: L0 = 3n-2 ; chain #3 (after the J3 clear of that near list): L0 = 3(z+1)-5.  Each step consumes one 5-adic
   digit; prints the residue path until a stop or until the known digits run out."""
import sys
from towermod import B_mod
K = int(sys.argv[1]); M = 5 ** K
B = B_mod(M); n = (12 * B + 25) % M
C = {1: 32, 2: -46, 3: -64, 4: -52}
def chain(L, prec, name):
    steps = 0
    while prec > 1:
        r = L % 5
        if r == 0:
            z = ((L - 30) % 5 ** prec) // 5; prec -= 1
            print('%s: stop after %d steps, z known mod 5^%d' % (name, steps, prec)); return z % 5 ** prec, prec
        L = ((3 * L + C[r]) % 5 ** prec) // 5; prec -= 1; steps += 1
    print('%s: %d steps, digits exhausted (no stop yet)' % (name, steps)); return None, 0
z2, p = chain((3 * n - 2) % M, K, 'chain #2 (real n)')
if z2 is not None:
    z3, p3 = chain((3 * (z2 + 1) - 5) % 5 ** p, p, 'chain #3 (real k3)')
    k = 4
    while z3 is not None and p3 > 1:
        z3, p3 = chain((3 * (z3 + 1) - 5) % 5 ** p3, p3, 'chain #%d' % k); k += 1
