"""Actual machine (not mirror) helpers: K(ds;a;b) = head E on blank at the left end, then 11 (01)^b 0 (01)^a 0 (01)^dn ... 0 (01)^d1."""
import sys
from tmlit import Sim, ST
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
def word(ds, a, b):
    w = '11' + '01' * b + '0' + '01' * a
    for d in reversed(ds):
        w += '0' + '01' * d
    return w
def start(ds, a, b, tm=ACT):
    w = word(ds, a, b)
    return Sim.from_word(tm, '0' * 6 + w + '0' * 6, 5, 'E', size=1 << 16)
def tapestr(s):
    lo, hi = s.lo, s.hi
    t = ''.join(map(str, s.tape[lo:hi + 1]))
    p = s.pos - lo
    return t[:p] + '[' + ST[s.state] + ']' + t[p:]
