"""Group 'rf': champion rules with a FREE far side (the cell beyond the borrowed token is l itself, any content).
  R2f : Kt (x+3 :: ds) 1 r t -->+ Kt (x :: ds) (2r+3) 2 t                 (r >= 1, any x, any far side)
  R3f : Kt (1^(k+1) ++ (x+3) :: ds) 1 r t -->+ Kt (1^k ++ (2r+3) :: x :: ds) 1 2 t
  DEC3f = R3f at x = 0 (the counter's last step 3 -> 0; key-31 rho = 3, 4 have a z2 gap beyond the 3)."""
from common import *
from shapes import *


def Kf(acc, atok, rest):
    return ('B', tailpart() + acc + atok + rest + [V('l')], [BLANK], '>')


ITEMS = [
    ('R2f', Kf(accr(0, 'r'), tok(1), tok(3, 'x')), Kf(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x')),
     dict(positive=frozenset(('r',))), ('r',)),
    ('R3f', Kf(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x')),
     Kf(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x')),
     dict(positive=frozenset(('r',))), ('r',)),
]
