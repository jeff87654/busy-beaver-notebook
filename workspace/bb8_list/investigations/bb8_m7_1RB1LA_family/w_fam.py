import sys, os
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
from rules_fam import *
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate
pl.set_tm(TM)

def PS(zc, zv, cc, cv, dc, dv, q='C', tail=None):
    """pass start: head C on a 1, left (head cell first) 1 (10)^c 0^z 1 l ; right 1 (101)^d (just after the head cell)."""
    L = [1] + mkrun((1, 0), cv, cc) + mkrun((0,), zv, zc) + (tail if tail is not None else [1, V('l')])
    Rt = [1] + mkrun((1, 0, 1), dv, dc) + [BLANK]
    return (q, pl.norm_side(L), pl.norm_side(Rt), '<')

def chk(s, t, grid, ms=500000):
    bad = []
    for vals in grid:
        r = validate.reaches(s, t, vals, max_steps=ms)
        if r is None:
            bad.append(vals)
    return bad
if __name__ == '__main__':
    s = PS(0, {'z': 1}, 0, {'c': 1}, 0, {'d': 1})
    t = PS(0, {'z': 1}, 0, {'c': 1}, 1, {'d': 1})
    # shape: z -> z-1 etc. test via substitution: (z,c,d) -> (z-1,c-1,d+1) means s=PS(1+z',1+c',d), t=PS(z',c',d+1)
    s = PS(1, {'z': 1}, 1, {'c': 1}, 0, {'d': 1})
    t = PS(0, {'z': 1}, 0, {'c': 1}, 1, {'d': 1})
    for z in range(0, 6):
        row = []
        for c in range(0, 6):
            ok = [d for d in range(0, 3) if validate.reaches(s, t, {'z': z, 'c': c, 'd': d}) is not None]
            row.append(''.join(map(str, ok)) or '-')
        print('z=%d' % z, ' '.join('%3s' % r for r in row))


def PSP(zc, zv, c1, cpc, cpv, dpc, dpv, q='C', tail=None, zb=(0,)):
    """pass start with the run as c1 single units + pairs (1010) and the deposits as pairs (101101)."""
    L = [1] + mkrun((1, 0), {}, c1) + mkrun((1, 0, 1, 0), cpv, cpc) + mkrun(zb, zv, zc) + (tail if tail is not None else [1, V('l')])
    Rt = [1] + mkrun((1, 0, 1, 1, 0, 1), dpv, dpc) + [BLANK]
    return (q, pl.norm_side(L), pl.norm_side(Rt), '<')

def PSB(cc, cv, dc, dv, q='C'):
    """blank-left pass start (R4): head C on a 1, left (head first) 1 (10)^c then blank ; right 1 (101)^d."""
    L = [1] + mkrun((1, 0), cv, cc) + [BLANK]
    Rt = [1] + mkrun((1, 0, 1), dv, dc) + [BLANK]
    return (q, pl.norm_side(L), pl.norm_side(Rt), '<')

def PSBP(c1, cpc, cpv, dpc, dpv, q='C'):
    L = [1] + mkrun((1, 0), {}, c1) + mkrun((1, 0, 1, 0), cpv, cpc) + [BLANK]
    Rt = [1] + mkrun((1, 0, 1, 1, 0, 1), dpv, dpc) + [BLANK]
    return (q, pl.norm_side(L), pl.norm_side(Rt), '<')
