"""Planner runs (symbolic execution mirroring busycoq's [execute]) for the raw phase lemmas."""
import sys
import planner8 as P
import pext
TM = "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---"
P.set_tm(TM)
BL = P.BLANK

def run(blk, v):
    return [('run', tuple(blk), ((v, 1),))]

def m_tloop(cfg):
    """Tloop: (0 >> [1;0]^^m *> [1;1;1]^^k *> l) {{B}}> const 0 -->* (0 >> [1;0]^^m *> [1;0;1;0;1;0]^^k *> l) {{B}}> const 0,
    m concrete (pairs of cells), k a single variable."""
    q, L, R, mode = cfg
    if q != 'B' or mode != '>' or R[0] != BL or L[0] != 0:
        return None
    i = 1; mc = 0
    while i + 1 < len(L) and L[i] == 1 and L[i + 1] == 0:
        mc += 1; i += 2
    if not (i < len(L) and P.is_run(L[i]) and L[i][1] == (1, 1, 1) and len(L[i][2]) == 1 and L[i][2][0][1] == 1):
        return None
    k = L[i][2][0][0]
    newL = [0] + [1, 0] * mc + [('run', (1, 0, 1, 0, 1, 0), L[i][2])] + L[i + 1:]
    return ('B', P.norm_side(newL), R, '>'), 'follow (Tloop %s %d).' % (k, mc), 'Tloop k=%s m=%d' % (k, mc)
m_tloop.anytime = True

X = [1, 1, 1, 0, 1, 1, 1, 0]            # tape 0111 0111, stream order (nearest the head first)
H5 = [0, 1, 0, 1, 0]                    # tape 01010 next to the head
N34 = [1, 1] + run((1, 1, 1), 'k') + [1, 1]      # 1^(3k+4)
N33 = [1, 1, 1] + run((1, 1, 1), 'k')            # 1^(3k+3)   (layout chosen so the planner never needs to peel)
N32 = [1, 1] + run((1, 1, 1), 'k')               # 1^(3k+2)
def B010(c): return [0, 1, 0] * c
def Bcfg(L): return ('B', L, [BL], '>')
def Ycfg(R): return ('A', [BL], [0] + R + [BL], '>')

PH = {}
# name: (start, target, matchers)
PH['T1'] = (Bcfg([0] + run((1, 0), 'm') + [1, 1, 1, P.V('l')]),
            Bcfg([0] + run((1, 0), 'm') + [1, 0, 1, 0, 1, 0, P.V('l')]))
ONES6 = lambda c: [1] * c + run((1, 1, 1, 1, 1, 1), 'k')
YR = lambda c: [0, 1] * c + run((0, 1, 0, 1, 0, 1), 'k')
PH['P0raw'] = (Bcfg(H5 + N33 + X + B010(3) + [P.V('l')]), Bcfg(H5 + ONES6(28) + X + [P.V('l')]))
PH['P1raw'] = (Bcfg(H5 + N34 + X + B010(5) + [P.V('l')]), Bcfg(H5 + ONES6(47) + X + [P.V('l')]))
PH['P2raw'] = (Bcfg(H5 + N32 + X + [P.V('l')]), Bcfg(H5 + ONES6(16) + [0, P.V('l')]))
PH['Q0raw'] = (Bcfg(H5 + N33 + [0] + B010(5) + [P.V('l')]), Bcfg(H5 + ONES6(33) + X + [P.V('l')]))
PH['Q1raw'] = (Bcfg(H5 + N34 + [0] + B010(6) + [P.V('l')]), Bcfg(H5 + ONES6(43) + X + [P.V('l')]))
PH['EP0p2raw'] = (Bcfg(H5 + N34 + X + [1, 1, BL]), Ycfg(YR(19)))
PH['EQ0p1raw'] = (Bcfg(H5 + N34 + [0] + [1, BL]), Ycfg(YR(9)))
PH['EQ1p1raw'] = (Bcfg(H5 + N34 + [0] + B010(1) + [1, BL]), Ycfg(YR(16)))
PH['EQ5p2raw'] = (Bcfg(H5 + N34 + [0] + B010(5) + [1, 1, BL]), Bcfg(H5 + ONES6(41) + X + B010(1) + [1, BL]))
PH['Y0raw'] = (Ycfg(run((0, 1, 0, 1, 0, 1), 'k') + [0, 1] * 6),
               Bcfg([0, 1, 0, 1, 0, 1, 1, 1, 0] + B010(4) + run((0, 1, 0, 0, 1, 0), 'k') + [1, 1, BL]))
PH['Y1raw'] = (Ycfg(run((0, 1, 0, 1, 0, 1), 'k') + [0, 1] * 7),
               Bcfg([0, 1, 0, 1, 0, 1, 1, 1, 0] + B010(5) + run((0, 1, 0, 0, 1, 0), 'k') + [1, BL]))

def is_canon_B(cfg):
    q, L, R, mode = cfg
    return q == 'B' and mode == '>' and R[0] == BL and L[:5] == H5 and any(P.is_run(t) for t in L[5:8])

if __name__ == '__main__':
    names = sys.argv[1:] or list(PH)
    for nm in names:
        start, tgt = PH[nm]
        try:
            script, end = P.drive(nm, start, tgt, matchers=[m_tloop, pext.m_sweep], maxev=400, verbose=True)
            print('  END:', P.show(end))
        except Exception as e:
            print('  EXC', e)
