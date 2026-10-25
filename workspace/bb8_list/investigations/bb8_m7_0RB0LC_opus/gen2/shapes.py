"""Token-family configurations for the explorer (left streams nearest-first) with the second-epoch tails.
T0  = champion tail 111 00 1 ;  T1j = 1^8 (00 1^6)^j 00 1 00 1  (j = run variable)."""
from common import *
Z = (1, 0, 1)          # a zero digit token D1 as a left stream block
U = (0, 1)             # one unit of a token / accumulator
SIX = (1, 1, 1, 1, 1, 1, 0, 0)
TAILS = {
    'T0': [1, 0, 0, 1, 1, 1],
    'T1': [1, 0, 0, 1, 0, 0, run(SIX, j=1)] + [1] * 8,
}
TAIL = 'T1'
def tailpart():
    return list(TAILS[TAIL])
def tok(n, var=None, blk=U):
    out = [1] + [0, 1] * n
    if var:
        out.append(run(blk, **{var: 1}))
    return out
def K(acc, atok, rest):
    return ('B', tailpart() + acc + atok + rest + [1, V('l')], [BLANK], '>')
def accr(n=0, var=None, blk=U):
    out = [0, 1] * n
    if var:
        out.append(run(blk, **{var: 1}))
    return out
