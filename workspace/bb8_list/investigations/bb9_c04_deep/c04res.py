"""c04res.py K : real residues (mod 5^K) of the C04 quantities after exhaustion #2 (rule P2, n = 12B+25 = 1792 mod 5^5):
   y1 = (3n+9)/5, y2 = (9n-3)/25, y3 = (27n-259)/125, y4 = (81n-152)/625, k3 = (243n-32331)/3125, X = k3+7,
   P = 12 R2 - 10 (parked), and every deep-clear accumulator R = B (mod anything) since 2R+4 is a tall tower of 2s."""
import sys
from towermod import B_mod
K = int(sys.argv[1]); M = 5 ** K
Mn = 5 ** (K + 5)
B = B_mod(Mn); n = (12 * B + 25) % Mn
assert n % 3125 == 1792
def aff(a, b, d):           # (a n + b)/d mod 5^K, exact division in the 5-adic sense
    v = (a * n + b) % (Mn)
    assert v % d == 0
    return (v // d) % M
vals = dict(y1=aff(3, 9, 5), y2=aff(9, -3, 25), y3=aff(27, -259, 125), y4=aff(81, -152, 625), k3=aff(243, -32331, 3125))
vals['B'] = B % M; vals['P'] = (12 * (B % M) - 10) % M
for k, v in vals.items(): print(k, v)
