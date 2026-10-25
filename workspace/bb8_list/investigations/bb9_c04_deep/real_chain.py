"""real_chain.py K : the real (residue-determined) sub-step sequence of C04's level-B cascade.
L0 = 36B+73 (exhaustion #2, n = 12B+25, L0 = 3n-2).  Map: r = L mod 5; r=1: L->(3L+32)/5, r=2: (3L-46)/5,
r=3: (3L-64)/5, r=4: (3L-52)/5, r=0: stop -> next exhaustion with L0' = (3L-100)/5 (n' = (L-25)/5 zero digits).
Residues: B mod 5^K from towermod (2B+4 = 2^^^..3, tall tower of 2s).  Each step costs one 5-adic digit.
Prints the branch sequence per exhaustion and the sub-step counts s_j."""
import sys
sys.path.insert(0, '.')
from towermod import B_mod
K = int(sys.argv[1]) if len(sys.argv) > 1 else 200
MOD = 5 ** K
B = B_mod(MOD)
print('B mod 5 =', B % 5, ' B mod 25 =', B % 25)
L = (36 * B + 73) % MOD
C = {1: 32, 2: -46, 3: -64, 4: -52, 0: -100}
prec = K; exh = 2; seq = []; counts = []
while prec > 1:
    r = L % 5
    seq.append(str(r))
    num = (3 * L + C[r]) % MOD
    assert num % 5 == 0
    L = num // 5; prec -= 1
    MOD //= 5; L %= MOD
    if r == 0:
        counts.append(len(seq) - 1)
        print('exh#%d: %d sub-steps, branches %s' % (exh, len(seq) - 1, ''.join(seq[:-1])))
        exh += 1; seq = []
print('incomplete tail of exh#%d: %s (precision exhausted)' % (exh, ''.join(seq)))
print('sub-step counts:', counts, ' total steps', sum(c + 1 for c in counts), ' exhaustions', len(counts))
