"""Conv / Fin phases for b = b'+1 >= 1:  ENT (K -> loop head), LOOP (one full iteration), EXT (last C1 step)."""
import sys
from ph891 import *
RBc = mkrun((1, 0), {'c': 1}) + [BLANK]            # (10)^c BLANK
def mk(name, startcfg, Lj, Lj1, ext_target):
    # ENT target: the stuck configuration reached from startcfg
    script, stuck = drive(name + '_probe', startcfg, None, matchers=(), maxev=400, verbose=False)
    PH['ENT_' + name] = (startcfg, stuck)
    PH['LOOP_' + name] = (('C', Lj('j'), [1, 0] + RBc, '>'), ('C', Lj1, RBc, '>'))
    PH['EXT_' + name] = (('C', Lj('c'), [1, 0, BLANK], '>'), ext_target)
    return stuck

Lconv = lambda j: [1, 1, 1] + Srun('n') + [0] + Srun(j) + [1, 1, 1, BLANK]
Lconv1 = [1, 1, 1] + Srun('n') + [0] + Srun('j', 1) + [1, 1, 1, BLANK]
st = mk('Conv', cfg(S + Arun('b', 1) + Srun('n', 1) + [1, BLANK]), Lconv, Lconv1,
        cfg(Srun('n', 2) + [0, 1] + Srun('c', 1) + [BLANK]))
print('Conv X0:', pl.show(st))
Lfin = lambda j: [1, 1] + Srun('m') + Arun(j) + [0, 1, 0, 1, 1, BLANK]
Lfin1 = [1, 1] + Srun('m') + Arun('j', 1) + [0, 1, 0, 1, 1, BLANK]
st = mk('Fin', cfg(S + Arun('b', 1) + Srun('m', 1) + [BLANK]), Lfin, Lfin1,
        cfg(Srun('m', 1) + Arun('c', 3) + [1, BLANK]))
print('Fin X0:', pl.show(st))

if __name__ == '__main__':
    for w in sys.argv[1:]:
        s, t = PH[w]
        drive(w, s, t, matchers=(), maxev=400, verbose=True)
