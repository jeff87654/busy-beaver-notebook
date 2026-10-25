import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB1LC_0RC0LG_1RD0RD_1LE1LD_1RH0LF_1LG0RA_---1RA_1RD1RH"
pl.set_tm(TM)
ONE = (1,)
def cfg(l=None, lc=0, x=None, xc=0, y=None, yc=0, ytok=None, xtok=None, Ltok=None):
    """D> config: left stream nearest first: 0 0 1^y 0 1^x 0 1^L"""
    yt = ytok if ytok is not None else mkrun(ONE, {y:1} if y else {}, yc)
    xt = xtok if xtok is not None else mkrun(ONE, {x:1} if x else {}, xc)
    Lt = Ltok if Ltok is not None else mkrun(ONE, {l:1} if l else {}, lc)
    return ('D', [0, 0] + yt + [0] + xt + [0] + Lt + [BLANK], [BLANK], '>')
PH = {
 'R1': (cfg('l', 0, 'x', 2, 'y', 0), cfg('l', 0, 'x', 0, 'y', 8)),
 'S6': (cfg('l', 6, None, 1, 'y', 0), cfg('l', 1, 'y', 12, None, 3)),
 'S3': (cfg(None, 3, None, 1, 'y', 0), cfg(None, 0, None, 7, None, 3, Ltok=mkrun(ONE, {'y':1}, 9))),
 'S1': (cfg(None, 1, None, 1, 'y', 0), cfg(None, 0, None, 7, None, 3, Ltok=mkrun(ONE, {'y':1}, 11))),
}
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH]:
        s, t = PH[w]
        drive(w, s, t, maxev=200, verbose=True)
TWO = (1, 1)
def yk(r):  # y = 2k + r
    return mkrun(TWO, {'k': 1}, 0) + [1] * r
def Lk(lc, r):  # ones: 2k + r + lc
    return mkrun(TWO, {'k': 1}, 0) + [1] * (r + lc)
for r in (0, 1):
    for nm, lc0, lc in (('S3', 3, 9), ('S1', 1, 11)):
        PH['%s_%d' % (nm, r)] = (cfg(None, lc0, None, 1, ytok=yk(r)),
                                 cfg(None, 0, None, 7, None, 3, Ltok=Lk(lc, r)))
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a.startswith('S') and '_' in a]:
        s, t = PH[w]
        drive(w, s, t, maxev=200, verbose=True)
def s4_target():
    s = cfg(None, 4, None, 1, 'y', 0)
    c = s
    try:
        while True:
            pl.head(c)
            c = pl.step(c)
    except pl.Stuck:
        pass  # will handle via drive on crossing
    return c
