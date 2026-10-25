"""0LA (C14) after stage 21: list [4, 21, 2], a-block at D3, accumulator R (huge): D(0)^2 D(4) D(21) D(2) D(3) D(R) tail."""
import sys
import follow3 as F
from follow3 import Aff, A
M = sys.argv[2] if len(sys.argv) > 2 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH0LJ_---0LA'
one, two = A(1), A(2)
tail = [('D', A(0), A(6)), ('B', (('R', ('1', one), one), ('R', ('0', two), one), ('D', A(0), A(5))), A(7)),
        ('R', ('1', one), one), ('R', ('0', two), one), ('R', ('1', one), one), ('R', ('0', two), one)]
sym = [('D', A(0), A(2)), ('D', A(4), one), ('D', A(21), one), ('D', A(2), one), ('D', A(3), one),
       ('D', Aff(0, {'R': 1}), one)] + tail
for R in [200, 203, 260, 299, 302]:
    w = F.word_of(F.inst(sym, {'R': R}))
    o = F.run_hyb(M, w, int(sys.argv[1]), start='A', canon='A')
    print(R, o['raw'][:400], flush=True)
