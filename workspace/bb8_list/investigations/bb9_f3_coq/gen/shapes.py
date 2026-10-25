"""Configurations of the token family Kt for the explorer (left streams nearest-first)."""
from common import *
Z = (1, 0, 1)          # a zero digit token D1 as a left stream block
U = (0, 1)             # one unit of a token / accumulator


def tailpart():
    return [1, 0, 0, 1, run(TB, t=1), 1, 1]


def tok(n, var=None, blk=U):
    """1 >> [0;1]^^(n + var)"""
    out = [1] + [0, 1] * n
    if var:
        out.append(run(blk, **{var: 1}))
    return out


def K(acc, atok, rest):
    """head in B on the blank right of the word"""
    return ('B', tailpart() + acc + atok + rest + [1, V('l')], [BLANK], '>')


def accr(n=0, var=None, blk=U):
    out = [0, 1] * n
    if var:
        out.append(run(blk, **{var: 1}))
    return out
