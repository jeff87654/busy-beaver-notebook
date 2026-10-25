import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
pl.set_tm("1RB1LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RC1LG_---0LH_1RA1LF")
ONE2 = (1, 1); ONE6 = (1,)*6

def sweepB(cfg):
    q, L, R, mode = cfg
    if q == 'B' and mode == '>' and pl.is_run(R[0]) and R[0][1] in (ONE2, ONE6) and len(R) > 1 and R[1] == 1:
        blk = R[0][1]
        name = 'sweepB2' if blk == ONE2 else 'sweepB6'
        return (('B', pl.norm_side([R[0]] + L), R[1:], '>'), name, name)
    return None

def at_left_A0(cfg):
    q, L, R, mode = cfg
    return q == 'A' and mode == '>' and L == [BLANK] and R[0] == 0

def run(name, cfg, target=None):
    # drive until stuck or target; use stop_at to detect left A0 when no target
    script, end = drive(name, cfg, target, matchers=(sweepB,), maxev=200, verbose=True,
                        stop_at=None)
    return script, end

R = [V('r')]
A = {'a': 1}; Q = {'q': 1}
if __name__ == '__main__':
    import sys
    which = sys.argv[1]
    if which == 'O1':
        run('O1', ('A', [BLANK], [0] + mkrun(ONE2, A) + [1, 0] + R, '>'),
            ('A', [BLANK], [0] + mkrun(ONE2, A, 2) + [1] + R, '>'))
    if which == 'E':
        run('E', ('A', [BLANK], [0] + mkrun(ONE2, A) + [1, 1, 0, 1, 1] + R, '>'),
            ('A', [BLANK], [0, 1, 0] + mkrun((0, 0), A) + [1]*5 + R, '>'))
    if which == 'Z4':
        run('Z4', ('A', [BLANK], [0] + mkrun(ONE6, Q) + [1,1,1,1,0,0] + R, '>'),
            ('A', [BLANK], [0, 1,1,1,1, 0,1,1] + mkrun((0,1,1,0,1,1), Q) + [0, 0, 1] + R, '>'))
    if which == 'Z0':
        run('Z0', ('A', [BLANK], [0] + mkrun(ONE6, Q) + [1,1,1,1,1,1,0,0] + R, '>'),
            ('A', [BLANK], [0, 1, 0, 0, 1,1,1,1,1] + mkrun((0,1,1,0,1,1), Q) + [0, 0, 1] + R, '>'))
    if which == 'Z2':
        run('Z2', ('A', [BLANK], [0] + mkrun(ONE6, Q) + [1,1,0,0] + R, '>'),
            ('G', [BLANK], [0] + mkrun((1,1,0,1,1,0), Q) + [1,1,0,0,1] + R, '>'))
