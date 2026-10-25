"""P2 (the frame-1 exhaustion of X; no E0): [frame 1, D1^7 | m=1 ; r = c+2], t=3  -->+  Kt(1^(4c+10) ++ [7]; 1; 2; 3)
   (frame 11), at the use site c = 3R: Kgx (repeat O 7) [] O R 3 (1 >> const 0) -->+ Kg (repeat O (12R+10) ++ [2]) [] O O 3."""
from common import *
from shapes import *
START = ('B', [1, 0, 0, 1] + list(TB) * 3 + [1, 1] + accr(2, 'c', (0, 1)) + tok(1) + list(Z) * 7 + [1, BLANK],
         [BLANK], '>')
TARGET = ('B', [1, 0, 0, 1] + list(TB) * 3 + [1, 1] + accr(2) + tok(1) + list(Z) * 10 + [run(Z * 4, c=1)] + tok(7)
          + [1, 1, BLANK], [BLANK], '>')
ITEMS = [('XREB2', START, TARGET, dict(splits=0, maxstages=400), ())]
