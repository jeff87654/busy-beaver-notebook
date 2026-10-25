import idle
"""h003_orbit.py: real top-level orbit of h003 in 5-adic arithmetic.  K0 = 12B+27, B = R = R_* (stable tower residue).
Branch rules fitted from F/W2/W3 (all data points exact):  K=1: (9K+60R+36)/5 ; K=4: (3K+60R-2)/5 ; K=3: (3K+60R+16)/5 ;
K=0,2: exit (cascade + endgame).  Precision drops one 5-adic digit per step.  Also replays the fake worlds as a check."""
from towres import Rstar
RULE = {1: (9, 36), 4: (3, -2), 3: (3, 16)}
def orbit(K, R, mod=None, maxn=200):
    out = [K]
    while True:
        r = K % 5
        if r not in RULE or len(out) > maxn: return out, r
        a, c = RULE[r]; num = a * K + 60 * R + c; assert num % 5 == 0
        K = num // 5
        if mod: mod //= 5; K %= mod; R %= mod
        out.append(K)
for name, B in [('F', 6), ('W2', 66), ('W3', 366)]:
    print(name, orbit(12 * B + 27, 366))
P = 5 ** 60
Rs = Rstar(P * 16 * 9) % P
o, r = orbit((12 * Rs + 27) % P, Rs, mod=P)
print('real: %d tops before exit, exit residue %d; residues:' % (len(o), r), [k % 5 for k in o])
