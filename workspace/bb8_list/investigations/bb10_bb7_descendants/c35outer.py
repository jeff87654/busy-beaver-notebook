"""Follow a c35m14 G0=0LD rebuilder from its first outer event with a SMALL exact first accumulator R1, so that the big
digit D(2 R1 + 4) is exhausted after a few decrements and the next outer step (the borrow reaching the outer
[D2, 0^(12b+k), D0] block) is reached.  python c35outer.py MACHINE R1 STAGES LOG"""
import sys
import follow2 as f
M, R1, stages, logf = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
A = f.Aff
sym = [('D', A(2), A(1)), ('D', A(1), A(11, {'b': 12})), ('D', A(0), A(1)), ('D', A(2), A(1)), ('D', A(1), A(33)),
       ('D', A(1), A(1)), ('D', A(R1), A(1)), ('D', A(4), A(1))]
f.kword_sym = lambda n, template=None: sym
f.CANON = 'G'
lf = open(logf, 'w')
def log(s):
    lf.write(s + '\n'); lf.flush()
log(f'machine {M} from the first outer event with R1 = {R1}')
try:
    r = f.follow(M, 35, stages, 150_000_000, log, False, None)
    log(f'RESULT {r["result"]} stages={r["stages"]} full_cycles={r["full_cycles"]} history={r["history"]}')
except f.Fail as e:
    log(f'RESULT FAIL {e}')
