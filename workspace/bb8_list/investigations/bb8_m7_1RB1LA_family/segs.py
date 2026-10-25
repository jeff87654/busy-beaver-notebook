import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_fam import *
R = rules2()
D2 = (0, 0) + U + U
DIG = [1] + mkrun((0, 1), {'y': 1}) + T
# segment definitions: name -> (start, target, progress)
def segs():
    S = {}
    # R3A: j = k+1, b = k+r+1;  first pass start PS(z=2k+4, c=2k+2r+5, d=0, tail=DIG); after 2k+2 passes PS(2, 2r+3, 2k+2, tail=DIG)
    S['R3A0'] = (R['R3Am'][0], PSP(2, {'k': 1}, 1, 2, {'k': 1, 'r': 1}, 0, {}, tail=DIG, zb=(0, 0)), True)
    TA = cfgL(bblk({}, 1) + mkrun(D2, {'k': 1}) + [0, 0] + mkrun(U2, {'r': 1}, 2) + digit({'y': 1}) + T)
    S['R3A1'] = (PSP(2, {}, 1, 1, {'r': 1}, 1, {'k': 1}, tail=DIG), TA, False)
    # R3B: j = c+2, b = c+1: first PS(2c+6, 2c+5, 0, tail=DIG) ; after 2c+4 passes PS(2, 1, 2c+4, tail=DIG)
    S['R3B0'] = (R['R3Bm'][0], PSP(3, {'c': 1}, 1, 2, {'c': 1}, 0, {}, tail=DIG, zb=(0, 0)), True)
    S['R3B1'] = (PSP(2, {}, 1, 0, {}, 2, {'c': 1}, tail=DIG), R['R3Bm'][1], False)
    # R3C: j = c+3+m, b = c+1: first PS(2c+2m+8, 2c+5, 0, tail=DIG); after 2c+4 passes PS(2m+4, 1, 2c+4, tail=DIG)
    S['R3C0'] = (R['R3Cm'][0], PSP(4, {'c': 1, 'm': 1}, 1, 2, {'c': 1}, 0, {}, tail=DIG, zb=(0, 0)), True)
    S['R3C1'] = (PSP(2, {'m': 1}, 1, 0, {}, 2, {'c': 1}, tail=DIG, zb=(0, 0)), R['R3Cm'][1], False)
    S['R4_0'] = (R['R4m'][0], PSBP(1, 2, {'c': 1}, 0, {}), True)
    S['R4_1'] = (PSBP(1, 0, {}, 2, {'c': 1}), R['R4m'][1], False)
    return S
if __name__ == '__main__':
    import itertools
    S = segs()
    for nm, (s, t, prog) in S.items():
        vs = sorted({v for side in (s[1], s[2], t[1], t[2]) for tok in side if isinstance(tok, tuple) and tok[0] == 'run' for v, _ in tok[2]} - {'l', 't'})
        bad = 0; tot = 0
        for vals in itertools.product(range(0, 3), repeat=len(vs)):
            v = dict(zip(vs, vals))
            for e in ('y', 'k', 'r', 'c', 'm'): v.setdefault(e, 0)
            tot += 1
            if validate.reaches(s, t, v, max_steps=30000) is None:
                bad += 1
                if bad <= 2: print(nm, 'FAIL', v)
        print(nm, vs, tot, 'cases', bad, 'failures')
