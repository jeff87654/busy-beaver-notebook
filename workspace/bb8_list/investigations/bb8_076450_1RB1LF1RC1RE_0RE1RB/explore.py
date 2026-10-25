"""Phase definitions for the planner (machine given by TM; default = main machine)."""
import sys, os
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = os.environ.get('TM', "1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC")
pl.set_tm(TM)
ONE6 = (1,)*6

def sweepC(cfg):
    """C crawl: C> 0 0 (1..1)^n  ->  (1..1)^n C> 0 0  (head reads 0, next cell 0, then the run)."""
    q, L, R, mode = cfg
    if q != 'C':
        return None
    if mode == '>' and len(R) > 3 and R[0] == 0 and R[1] == 0 and pl.is_run(R[2]) and R[2][1] == ONE6:
        run, Lr, rest = R[2], L, R[3:]
    elif mode == '<' and len(L) > 1 and len(R) > 2 and L[0] == 0 and R[0] == 0 and pl.is_run(R[1]) and R[1][1] == ONE6:
        run, Lr, rest = R[1], L[1:], R[2:]
    else:
        return None
    return (('C', pl.norm_side([run] + Lr), [0, 0] + rest, '>'), 'follow sweepC6.', 'sweepC6')
sweepC.anytime = True

R = [V('r')]
I = {'i': 1}; J = {'j': 1}
PH = {
 # P6 : F>0 1^(6i+5) 0 0 r -> F>0 1^(6i+10) r
 'P6': (('F', [BLANK], [0] + mkrun(ONE6, I) + [1]*5 + [0, 0] + R, '>'),
        ('F', [BLANK], [0] + mkrun(ONE6, I) + [1]*10 + R, '>')),
 # C6 : F>0 1^(6j+4) 0 1 r -> F>0 1^5 (001)^(2j+1) 0 0 0 r
 'C6': (('F', [BLANK], [0] + mkrun(ONE6, J) + [1]*4 + [0, 1] + R, '>'),
        ('F', [BLANK], [0] + [1]*5 + mkrun((0,0,1,0,0,1), J) + [0,0,1,0,0,0] + R, '>')),
 # R6 : F>0 1^(6j+4) 0^inf -> F>0 1^4 0 1^(6j+7) 0^inf
 'R6': (('F', [BLANK], [0] + mkrun(ONE6, J) + [1]*4 + [BLANK], '>'),
        ('F', [BLANK], [0, 1, 1, 1, 1, 0] + mkrun(ONE6, J) + [1]*7 + [BLANK], '>')),
}
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH]:
        s, t = PH[w]
        drive(w, s, t, matchers=(sweepC,), maxev=200, verbose=True)
