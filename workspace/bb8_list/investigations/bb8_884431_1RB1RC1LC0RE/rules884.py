"""Machine-level rules of 1RB1RC_1LC0RE_... for the family
   Kc ds a b = 0^inf A> 0 11 (01)^(2b+1) 11 (01)^a  rgt ds,   rgt (d::t) = 11 (01)^d rgt t,  rgt [] = 111 0^inf
planner tokens (nearest the head first); (01)^(2b) is written as the block 0101 with count b."""
import sys
sys.path.insert(0, '.')
import planner8 as pl
from planner8 import BLANK, mkrun, V

TM = '1RB1RC_1LC0RE_1LF1LD_1LA1LE_1RH1RF_0LF1LG_0LD1LA_---0RA'
U = (0, 1)
U2 = (0, 1, 0, 1)
E = (1, 1)
Q = 'A'


def kc(b2, a, rest):
    """b2 = (dict, const): number of (0101) blocks in the b-run (b-run = (0101)^b2 01); a = list of tokens of the a-run;
    rest = tokens after the a-run (starting with the next sep)."""
    toks = [0, 1, 1] + mkrun(U2, b2[0], b2[1]) + [0, 1] + [1, 1] + a + rest
    return toks


def cfg(toks):
    return (Q, [BLANK], pl.norm_side(toks), '>')


def arun(d, c):
    return mkrun(U, d, c)


def a2run(d, c):         # (01)^(2*cnt + c): d counts blocks of 0101
    return mkrun(U2, d, 0) + mkrun(U, {}, c)


def rules():
    T = [1, 1, V('t')]
    out = []
    # R1 : K ds (S a) b -> K ds a (S b)
    out.append(('R1m', cfg(kc(({'b': 1}, 0), arun({'a': 1}, 1), T)),
                cfg(kc(({'b': 1}, 1), arun({'a': 1}, 0), T))))
    # R2 : K (S y :: t') 0 b -> K (y :: t') (2b+3) 0     rgt (S y :: t') = 11 (01)^(S y) rgt t'
    out.append(('R2m', cfg(kc(({'b': 1}, 0), [], [1, 1] + mkrun(U, {'y': 1}, 1) + T)),
                cfg(kc(({}, 0), a2run({'b': 1}, 3), [1, 1] + mkrun(U, {'y': 1}, 0) + T))))
    # R3 : K (0^(S k) ++ S y :: t') 0 b -> K (1^k ++ (2b+3) :: y :: t') 1 0
    zeros = mkrun(E, {'k': 1}, 1)
    start3 = kc(({'b': 1}, 0), [], zeros + [1, 1] + mkrun(U, {'y': 1}, 1) + T)
    big = [1, 1] + a2run({'b': 1}, 3)
    ones = mkrun((1, 1) + U, {'k': 1}, 0)
    tgt3 = kc(({}, 0), arun({}, 1), ones + big + [1, 1] + mkrun(U, {'y': 1}, 0) + T)
    out.append(('R3m', cfg(start3), cfg(tgt3)))
    # R4 : K (0^n) 0 b -> K (1^n ++ 0^(2b+2)) 1 0
    start4 = kc(({'b': 1}, 0), [], mkrun(E, {'n': 1}, 0) + [1, 1, 1, BLANK])
    tgt4 = kc(({}, 0), arun({}, 1), mkrun((1, 1) + U, {'n': 1}, 0) + mkrun((1, 1, 1, 1), {'b': 1}, 1) + [1, 1, 1, BLANK])
    out.append(('R4m', cfg(start4), cfg(tgt4)))
    return out


if __name__ == '__main__':
    pl.set_tm(TM)
    for name, s, t in rules():
        print(name, pl.show(s)); print('   ->', pl.show(t))
