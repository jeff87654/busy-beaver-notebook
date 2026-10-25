"""fam.py: register a base (machine + dlscan2 template + real first-list length n) as a mini-follower family of
halt_redirect/mf/mf35g.py (read-only use of that module), with the follower start = the base's configuration at its
first undefined read after K(0^n; 0; b) (any halting slot, not only E0).

  import fam; F = fam.register('lbl', base, template, n)   ->  mf35g.follow('lbl', machine10, ...)
  fam.start(lbl, b) -> (word, head, state, slot)     (fails loudly if the base does not halt from K(0^n;0;b))
  fam.inline_start(lbl, b, slot) -> the configuration at the first read of the given (used) slot after K(0^n;0;b)
"""
from __future__ import annotations
import sys
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_engines1')
import mf35g
from eng import parse_tmpl, kword, run_to_halt, Fail, Sim, tape_word

REG = {}


def register(lbl, base, tmpl, n):
    T = parse_tmpl(tmpl)
    if T['O'] != 'R' or T['al'] != 3 or T['be'] != 1 or T['alB'] != 3:
        raise Fail(f'template {tmpl} is not a right-side 3d+1 / 3b+E champion template')
    suf = T['S'] if T['u'].endswith('1') else T['S'][1:]
    if not T['u'].endswith('1') and not T['S'].startswith('1'):
        raise Fail('cannot derive SUF')
    E = T['beB']
    mf35g.FAMILIES[lbl] = dict(base=base, Q=T['Q'], SUF=suf, E=E, word=lambda b: kword(T, [0] * n, 0, b))
    REG[lbl] = dict(base=base, T=T, n=n)
    return mf35g.FAMILIES[lbl]


def kstart(lbl, b):
    R = REG[lbl]
    w = '0000' + kword(R['T'], [0] * R['n'], 0, b) + '0'
    return w, len(w) - 1, R['T']['Q']


def start(lbl, b, maxs=50_000_000):
    """first undefined read of the base after K(0^n;0;b); also installs it as the follower start for b"""
    R = REG[lbl]
    w, h, q = kstart(lbl, b)
    r = run_to_halt(R['base'], w, h, q, maxs)
    if r[0] != 'H':
        raise Fail(f'{lbl}: base does not halt from K(0^{R["n"]};0;{b}) within {maxs}')
    _, steps, word, hd, st, sym = r
    mf35g._XC[(lbl, b)] = (word, hd, st)
    return word, hd, st, f'{st}{sym}'


def inline_start(lbl, b, slot, maxs=50_000_000, skip=0):
    """configuration at the (skip+1)-th read of a used slot (e.g. 'H1') after K(0^n;0;b); installs it"""
    R = REG[lbl]
    w, h, q = kstart(lbl, b)
    s = Sim.from_word(R['base'], w, h, q, size=1 << 18)
    qs, cs = 'ABCDEFGHIJ'.index(slot[0]), int(slot[1])
    seen = 0
    while s.steps < maxs:
        if s.state == qs and s.tape[s.pos] == cs:
            if seen == skip:
                word, lo = tape_word(s)
                mf35g._XC[(lbl, b)] = (word, s.pos - lo, slot[0])
                return word, s.pos - lo, slot[0], s.steps
            seen += 1
        if not s.step():
            raise Fail(f'{lbl}: base halted before reading {slot}')
    raise Fail(f'{lbl}: {slot} not read within {maxs}')
