"""Follow c35m14 machine 1LI0LC/0LD0RH/0LJ1RI/---0LA from its first event with a small exact first accumulator."""
import sys
from fractions import Fraction as Fr
import follow2 as f
M, R1, stages, logf = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
A = f.Aff
sym = [('D', A(2), A(1)), ('D', A(1), A(2)), ('D', A(0), A(1)), ('D', A(2), A(1)), ('D', A(1), A(1)), ('D', A(0), A(1)),
       ('D', A(1), A(1)), ('D', A(Fr(39, 5), {'b': Fr(36, 5)}), A(1)), ('D', A(1), A(Fr(24, 5), {'b': Fr(36, 5)})),
       ('D', A(0), A(1)), ('D', A(2), A(1)), ('D', A(1), A(35)), ('D', A(1), A(1)), ('D', A(R1), A(1)), ('D', A(4), A(1))]
f.kword_sym = lambda n, template=None: sym
f.CANON = 'G'
lf = open(logf, 'w')
def log(s):
    lf.write(s + '\n'); lf.flush()
log(f'machine {M} from its first event with R1 = {R1}')
try:
    r = f.follow(M, 35, stages, 150_000_000, log, False, None)
    log(f'RESULT {r["result"]} stages={r["stages"]} full_cycles={r["full_cycles"]} history={r["history"]}')
except f.Fail as e:
    log(f'RESULT FAIL {e}')
