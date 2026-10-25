"""Shared setup: the autoproof engine (bb8_list/autoproof) for C04."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
AUTO = HERE
sys.path.insert(0, str(AUTO))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util, validate
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_1RK1RC'
pl.set_tm(TM)
assert engine.pl is pl and coqgen.pl is pl
TB = (0, 0, 1, 1, 1, 1, 1, 1)   # one tail block (11111100) as a left stream


def run(blk, **cnt):
    return ('run', tuple(blk), tuple(sorted(cnt.items())))


def header(title):
    return (AUTO / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '9') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))


def gen_rule(name, start, target, progress, positive=(), tree=None):
    if tree is None:
        tree = engine.explore(start, target, positive=frozenset(positive))
    gen = coqgen.RuleGen(name, engine)
    text = coqgen.rule_lemma(name, start, target, tree, gen, progress=progress, positive=positive)
    return gen.lemmas, text
