"""Shared setup for the 12-state candidate T12a = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---."""
import sys
import ctypes
try:   # run every script of this folder at Idle priority
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util, validate
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---'
pl.set_tm(TM)
assert engine.pl is pl and coqgen.pl is pl
U = (0, 1)        # one unit (10) of a token, as a left stream


def run(blk, **cnt):
    return ('run', tuple(blk), tuple(sorted(cnt.items())))


def tok(k, **var):
    """one token D(k + var-form) = (10)^m 1, as a left stream 1 (01)^m (nearest first)"""
    out = [1] + [0, 1] * k
    if var:
        out.append(run(U, **var))
    return out


def header(title):
    return (HERE / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '12') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
