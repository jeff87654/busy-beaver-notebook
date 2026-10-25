import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
pl.set_tm("1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC")
ONE2 = (1, 1); ONE6 = (1,)*6

def sweepC(cfg):
    """C crawl: C> 0 0 (1..1)^n  ->  (1..1)^n C> 0 0  (head reads 0, next cell 0, then the run)."""
    q, L, R, mode = cfg
    if q != 'C':
        return None
    if mode == '>' and len(R) > 3 and R[0] == 0 and R[1] == 0 and pl.is_run(R[2]) and R[2][1] in (ONE2, ONE6):
        run, Lr, rest = R[2], L, R[3:]
    elif mode == '<' and len(L) > 1 and len(R) > 2 and L[0] == 0 and R[0] == 0 and pl.is_run(R[1]) and R[1][1] in (ONE2, ONE6):
        run, Lr, rest = R[1], L[1:], R[2:]
    else:
        return None
    name = 'sweepC2' if run[1] == ONE2 else 'sweepC6'
    return (('C', pl.norm_side([run] + Lr), [0, 0] + rest, '>'), 'follow %s.' % name, name)
sweepC.anytime = True

R = [V('r')]
P = {'p': 1}; J = {'j': 1}
PH = {
 'P2': (('A', [BLANK], [0] + mkrun(ONE2, P) + [1, 1, 1, 1, 0, 0] + R, '>'),
        ('A', [BLANK], [0] + mkrun(ONE2, P) + [1]*9 + R, '>')),
 'R2': (('A', [BLANK], [0] + mkrun(ONE2, P) + [1, 1, 1, 1, 1, 0, 0] + R, '>'),
        ('A', [BLANK], [0, 1, 1, 1, 1, 1, 0] + mkrun(ONE2, P) + [1]*7 + R, '>')),
 'C6': (('A', [BLANK], [0] + mkrun(ONE6, J) + [1]*5 + [0, 1] + R, '>'),
        ('A', [BLANK], [0] + [1]*6 + mkrun((0,0,1,0,0,1), J) + [0,0,1,0,0,0] + R, '>')),
}
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH]:
        s, t = PH[w]
        drive(w, s, t, matchers=(sweepC,), maxev=200, verbose=True)

I = {'i': 1}
PH['P6'] = (('A', [BLANK], [0] + mkrun(ONE6, I) + [1]*6 + [0, 0] + R, '>'),
            ('A', [BLANK], [0] + mkrun(ONE6, I) + [1]*11 + R, '>'))
PH['R6'] = (('A', [BLANK], [0] + mkrun(ONE6, J) + [1]*5 + [BLANK], '>'),
            ('A', [BLANK], [0, 1, 1, 1, 1, 1, 0] + mkrun(ONE6, J) + [1]*7 + [BLANK], '>'))
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'new':
    for w in ('P6', 'R6'):
        s, t = PH[w]
        drive(w, s, t, matchers=(sweepC,), maxev=200, verbose=True)
