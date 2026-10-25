"""Shared setup: the autoproof engine (bb8_list/autoproof) for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
AUTO = HERE.parents[1] / 'autoproof'
sys.path.insert(0, str(AUTO))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util, validate
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA'
pl.set_tm(TM)
assert engine.pl is pl and coqgen.pl is pl


def run(blk, **cnt):
    return ('run', tuple(blk), tuple(sorted(cnt.items())))


def header(title):
    return (AUTO / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '9') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))

# ---- family shapes (left streams nearest-first); head in G on the blank right of the word
Z = (1, 0, 1)            # zero digit token D1
P = (1, 0)               # one unit of a token


def tok(n, var=None, blk=P):
    """the token D(n + var) as a stream: [1;0]^^n *> [blk]^^var *> 1"""
    out = list(P) * n
    if var:
        out.append(run(blk, **{var: 1}))
    return out + [1]


def KR(atok, acc, rest, tail=None):
    """Kr: [1;0]^^2 *> 1 >> acc >> atok >> rest"""
    return ('G', (tail if tail is not None else [1, 0, 1, 0, 1]) + acc + atok + rest, [BLANK], '>')
