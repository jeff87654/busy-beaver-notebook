import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM="1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF"
pl.set_tm(TM)
ONE2 = (1, 1); ONE6 = (1,)*6
R = [V('r')]
A = {'a': 1}; Q = {'q': 1}
def sweepB(cfg):
    q, L, R, mode = cfg
    if q == 'B' and mode == '>' and pl.is_run(R[0]) and R[0][1] in (ONE2, ONE6) and len(R) > 1 and R[1] == 1:
        blk = R[0][1]
        name = 'sweepB2' if blk == ONE2 else 'sweepB6'
        return (('B', pl.norm_side([R[0]] + L), R[1:], '>'), name, name)
    return None
def run(name, cfg, target=None, matchers=(sweepB,)):
    return drive(name, cfg, target, matchers=(sweepB,), maxev=200, verbose=True)
if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'O1':
        run('O1', ('A', [BLANK], [0] + mkrun(ONE2, A) + [1, 0] + R, '>'),
            ('A', [BLANK], [0] + mkrun(ONE2, A, 2) + [1] + R, '>'))
    if which == 'E':
        run('E', ('A', [BLANK], [0] + mkrun(ONE2, A) + [1, 1, 0, 0, 1] + R, '>'),
            ('A', [BLANK], [0, 1, 0] + mkrun((0, 0), A) + [1]*5 + R, '>'))
    Q2={'q':2}
    if which == 'Z4':
        run('Z4', ('A', [BLANK], [0] + mkrun(ONE6, Q) + [1]*4 + [0, 0, 0] + R, '>'),
            ('A', [BLANK], [0, 1] + mkrun((0,0,1), Q2, 1) + [0,0,0,1] + R, '>'))
    if which == 'Z2':
        run('Z2', ('A', [BLANK], [0] + mkrun(ONE6, Q) + [1]*8 + [0, 0, 0] + R, '>'),
            ('A', [BLANK], [0] + [1]*8 + mkrun((0,0,1), Q2) + [0,0,0,1] + R, '>'))
    if which == 'Z0':
        run('Z0', ('A', [BLANK], [0] + mkrun(ONE6, Q) + [1]*6 + [0, 0, 0] + R, '>'), None)
    if which == 'SW':
        P={'p':1}
        run('SW', ('A', [BLANK], [0] + mkrun(ONE2, P) + [1,1, 0, 0, 0] + R, '>'), None)
