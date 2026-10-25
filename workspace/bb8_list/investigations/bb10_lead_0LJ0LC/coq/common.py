"""Shared setup: the autoproof engine (local copy, 10 states) for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util, validate
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC'
pl.set_tm(TM)
assert engine.pl is pl and coqgen.pl is pl
U = (0, 1)        # one unit (10) of a group, as a left stream
Z = (1, 0, 1)     # a zero digit group 1 (10)^1, as a left stream


def run(blk, **cnt):
    return ('run', tuple(blk), tuple(sorted(cnt.items())))


def grp(c, **var):
    """one group 1 >> [0;1]^^(n + var-form) (left stream)"""
    out = [1] + [0, 1] * c
    if var:
        out.append(run(U, **var))
    return out


def G(left):
    """head in G on the blank right of the word"""
    return ('G', list(left), [BLANK], '>')


def header(title):
    return (HERE / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '10') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
