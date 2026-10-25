"""Rule configurations for 1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LB (and variants), orientation R:
structure left of the head, head D on the blank right of everything.
F(W,b): left stream (nearest the head first) = (0101)^(b+1) , then for each digit d of W (nearest first): 0 0 (01)^d, then t.
Tape (left to right): ... (10)^d2 00 (10)^d1 00 (10)^a 00 (10)^(2b+2) D>."""
import sys, os
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
TM = os.environ.get('TM', "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LB")
Q = 'D'
U = (0, 1)
U2 = (0, 1, 0, 1)
T = [0, 0, V('t')]

def cfgL(toks):
    return (Q, pl.norm_side(toks), [BLANK], '>')

def bblk(cnt, c=0):
    return mkrun(U2, cnt, c)

def digit(cnt, c=0):
    return [0, 0] + mkrun(U, cnt, c)

def rules():
    out = {}
    D2 = (0, 0) + U + U            # a digit 2
    Z = (0, 0)
    # R1: F(S a :: t) b -> F(a :: t) (S b)
    out['R1m'] = (cfgL(bblk({'b': 1}, 1) + digit({'a': 1}, 1) + T), cfgL(bblk({'b': 1}, 2) + digit({'a': 1}) + T))
    # R3A: j zero digits (j = k+1 >= 1, counting a), b >= j:  b = j + r
    #   F(0^j ++ S y :: t) b -> F(2^(j-1) ++ [2(b-j+2), y] ++ t) 0      (b is "ours": units 2b+2)
    # R3B: j = b+1:  F(0^j ++ S y :: t) b -> F(2^b ++ [y+3] ++ t) 0
    # R3C: j >= b+2: F(0^j ++ S y :: t) b -> F(2^(b+1) ++ 0^(j-b-2) ++ S y :: t) 0
    # R4:  b >= 1:   F(0^j) b -> F(2^(b+1)) 0
    return out

if __name__ == '__main__':
    pl.set_tm(TM)
    import engine
    names = sys.argv[1:] or list(rules2())
    for nm in names:
        s, t = rules2()[nm]
        print(nm, pl.show(s), '=>', pl.show(t))
        tree = engine.explore(s, t)
        print('\n'.join(engine.describe(tree)))

# ---- R3 / R4 rule configurations (added)
def rules2():
    out = rules()
    D2 = (0, 0) + U + U            # a digit 2
    Z = (0, 0)
    # R3A: j = k+1 zero digits, b = k+1+r:   F(0^(k+1) ++ S y :: t) (k+1+r) -> F(2^k ++ [2r+4, y] ++ t) 0
    out['R3Am'] = (cfgL(bblk({'k': 1, 'r': 1}, 2) + mkrun(Z, {'k': 1}, 1) + digit({'y': 1}, 1) + T),
                   cfgL(bblk({}, 1) + mkrun(D2, {'k': 1}) + digit({'r': 2}, 4) + digit({'y': 1}) + T))
    # R3B: j = c+2, b = c+1:  F(0^(c+2) ++ S y :: t) (c+1) -> F(2^(c+1) ++ [y+3] ++ t) 0
    out['R3Bm'] = (cfgL(bblk({'c': 1}, 2) + mkrun(Z, {'c': 1}, 2) + digit({'y': 1}, 1) + T),
                   cfgL(bblk({}, 1) + mkrun(D2, {'c': 1}, 1) + digit({'y': 1}, 3) + T))
    # R3C: j = c+3+m, b = c+1:  F(0^(c+3+m) ++ S y :: t) (c+1) -> F(2^(c+2) ++ 0^m ++ S y :: t) 0
    out['R3Cm'] = (cfgL(bblk({'c': 1}, 2) + mkrun(Z, {'c': 1, 'm': 1}, 3) + digit({'y': 1}, 1) + T),
                   cfgL(bblk({}, 1) + mkrun(D2, {'c': 1}, 2) + mkrun(Z, {'m': 1}) + digit({'y': 1}, 1) + T))
    # R4: b = c+1:  F(0^j) (c+1) -> F(2^(c+2)) 0
    out['R4m'] = (cfgL(bblk({'c': 1}, 2) + [0, BLANK]),
                  cfgL(bblk({}, 1) + mkrun(D2, {'c': 1}, 2) + [BLANK]))
    return out
