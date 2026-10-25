"""Rule configurations for 1RB0LD_0LC1RB_..._1LD--- (orientation R: structure left of the head, head B on the blank right).
F(W,b) = P u2^b (0 u^d)_{d in W, nearest first} T on the left stream, b' = 2b+1 units of u = (0,1) (stream order)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
TM = os.environ.get('TM', "1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
Q = 'B'
P = [1, 1, 0, 0, 1]          # suffix 011 (nearest first 1,1,0) then one unit (0,1)
U = (0, 1)
U2 = (0, 1, 0, 1)
T = [0, V('t')]

def cfgL(toks):
    return (Q, pl.norm_side(toks), [BLANK], '>')

def bblk(cnt, c=0):
    return mkrun(U2, cnt, c)

def digit(cnt, c=0):
    return [0] + mkrun(U, cnt, c)

def rules():
    out = {}
    # R1: F(S a :: t) b -> F(a :: t) (S b)
    out['R1m'] = (cfgL(P + bblk({'b': 1}) + digit({'a': 1}, 1) + T), cfgL(P + bblk({'b': 1}, 1) + digit({'a': 1}) + T))
    D2 = (0,) + U + U
    Z = (0,)
    # R3A: b = k+1+r, j = k+1 zero digits:  F(0^(k+1) ++ S y :: t) (k+1+r) -> F(2^k ++ [2r+2, y] ++ t) 1
    out['R3Am'] = (cfgL(P + bblk({'k': 1, 'r': 1}, 1) + mkrun(Z, {'k': 1}, 1) + digit({'y': 1}, 1) + T),
                   cfgL(P + bblk({}, 1) + mkrun(D2, {'k': 1}) + digit({'r': 2}, 2) + digit({'y': 1}) + T))
    # R3B: b = S c, j = c+2:  F(0^(c+2) ++ S y :: t) (S c) -> F(2^c ++ [y+3] ++ t) 1
    out['R3Bm'] = (cfgL(P + bblk({'c': 1}, 1) + mkrun(Z, {'c': 1}, 2) + digit({'y': 1}, 1) + T),
                   cfgL(P + bblk({}, 1) + mkrun(D2, {'c': 1}) + digit({'y': 1}, 3) + T))
    # R3C: b = S c, j = c+3+m:  F(0^(c+3+m) ++ S y :: t) (S c) -> F(2^(S c) ++ 0^m ++ S y :: t) 1
    out['R3Cm'] = (cfgL(P + bblk({'c': 1}, 1) + mkrun(Z, {'c': 1, 'm': 1}, 3) + digit({'y': 1}, 1) + T),
                   cfgL(P + bblk({}, 1) + mkrun(D2, {'c': 1}, 1) + mkrun(Z, {'m': 1}) + digit({'y': 1}, 1) + T))
    # R4: b = S c: F(0^j) (S c) -> F(2^(S c)) 1
    out['R4m'] = (cfgL(P + bblk({'c': 1}, 1) + [0, BLANK]),
                  cfgL(P + bblk({}, 1) + mkrun(D2, {'c': 1}, 1) + [BLANK]))
    return out

if __name__ == '__main__':
    pl.set_tm(TM)
    import engine
    names = sys.argv[1:] or list(rules())
    for nm in names:
        s, t = rules()[nm]
        print(nm, pl.show(s), '=>', pl.show(t))
        tree = engine.explore(s, t)
        print('\n'.join(engine.describe(tree)))
