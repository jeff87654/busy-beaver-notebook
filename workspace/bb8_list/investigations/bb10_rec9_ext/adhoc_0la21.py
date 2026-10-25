"""0LA (C14) stage-21 input, built by hand from the log: D(0)^2 D(4) D(21) D(2) D(2R2-2) D(2) D(1)^2 D(1) D(R24) tail7."""
import sys, os
import follow3 as F
from follow3 import Aff, A
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH0LJ_---0LA'
one, two = A(1), A(2)
tail = [('D', A(0), A(6)), ('B', (('R', ('1', one), one), ('R', ('0', two), one), ('D', A(0), A(5))), A(7)),
        ('R', ('1', one), one), ('R', ('0', two), one), ('R', ('1', one), one), ('R', ('0', two), one)]
sym = [('D', A(0), A(2)), ('D', A(4), one), ('D', A(21), one), ('D', A(2), one), ('D', Aff(-2, {'X': 2}), one),
       ('D', A(2), one), ('D', one, A(2)), ('D', one, one), ('D', Aff(0, {'R': 1}), one)] + tail
for X, R in [(200, 200), (203, 260), (209, 299)]:
    w = F.word_of(F.inst(sym, {'X': X, 'R': R}))
    o = F.run_hyb(M, w, int(sys.argv[1]) if len(sys.argv) > 1 else 2000000000, start='A', canon='A')
    print(X, R, o['raw'][:400], flush=True)
