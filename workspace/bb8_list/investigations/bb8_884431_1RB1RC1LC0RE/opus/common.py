"""Shared setup: the autoproof engine (bb8_list/autoproof, first on the path) and the macro states of 884431."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
AUTO = HERE.parents[2] / 'autoproof'
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(AUTO))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util, validate
TM = '1RB1RC_1LC0RE_1LF1LD_1LA1LE_1RH1RF_0LF1LG_0LD1LA_---0RA'
pl.set_tm(TM)
assert engine.pl is pl and coqgen.pl is pl


def header(title):
    return (AUTO / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '8') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))


def gen_rule(name, start, target, progress, tree=None):
    """Explore and generate (lemma texts, rule text)."""
    if tree is None:
        tree = engine.explore(start, target)
    gen = coqgen.RuleGen(name, engine)
    text = coqgen.rule_lemma(name, start, target, tree, gen, progress=progress)
    return gen.lemmas, text
