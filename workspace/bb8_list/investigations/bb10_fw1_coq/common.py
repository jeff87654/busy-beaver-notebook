"""Shared setup for the f_{omega+1} BB(10) candidate 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA."""
import sys
import ctypes
try:   # run every script of this folder at Idle priority (0x40 = IDLE_PRIORITY_CLASS)
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util, validate
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
pl.set_tm(TM)
assert engine.pl is pl and coqgen.pl is pl
U = (0, 1)        # one unit (10) of a token, as a left stream


def run(blk, **cnt):
    return ('run', tuple(blk), tuple(sorted(cnt.items())))


def tok(k, **var):
    """one token D(c + var-form) = (10)^m 1, as a left stream 1 (01)^m"""
    out = [1] + [0, 1] * k
    if var:
        out.append(run(U, **var))
    return out


def tok2(k, **var):
    """token D(k + 2*var-form) with the doubled part as a run of (0101) blocks"""
    out = [1] + [0, 1] * k
    if var:
        out.append(run((0, 1, 0, 1), **var))
    return out


def G(left):
    """head in G on the blank right of the word"""
    return ('G', list(left), [BLANK], '>')


def header(title):
    return (HERE / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '10') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
