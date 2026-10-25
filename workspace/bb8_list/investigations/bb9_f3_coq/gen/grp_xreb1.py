"""P1 (exhaustion #1 of X, the far-left E0 takes K0 = 0RC): Kt(1^11;1;A;0) -->+ [frame 1, D1, D(2A-6), D13, D1^4 | m=1 ; r=2], t=3.
   A = a+5 (a free); at the use site A = 3 Bx + 2, so 2A-6 = 6 Bx - 2 = tokd (2 Bx - 1)."""
from common import *
from shapes import *
START = ('B', [1, 0, 0, 1] + [1, 1] + accr(5, 'a', (0, 1)) + tok(1) + list(Z) * 11 + [1, 1, BLANK], [BLANK], '>')
TARGET = ('B', [1, 0, 0, 1] + list(TB) * 3 + [1, 1] + accr(2) + tok(1) + list(Z) * 4 + tok(13) + tok(4, 'a', (0, 1, 0, 1))
          + tok(1) + [1, BLANK], [BLANK], '>')
ITEMS = [('XREB1', START, TARGET, dict(splits=0, maxstages=400), ())]
