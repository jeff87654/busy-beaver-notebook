"""eng.py: shared helpers for the bb9_engines1 census.

Templates are dlscan2 templates 'O,Q,P=..,u=..,s=..,d=ad+b,b=ab+b,S=..' (O = R or L; L means: mirror the machine and
use the template on the right).  K(ds; a; b) word (right side, head on the blank right of the word, state Q):
    P + [u^(al*d+be) s for d in ds] + u^(al*a+be) s + u^(alB*b+beB) + S
validate_template() checks this against the literal blank-tape run at the step trace2 reports (fails loudly).
"""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_champ35_1RB0RA_1LC0RH')
from tmlit import Sim

TRACE2 = r'C:/Users/jeffr/Downloads/bb8/bb8_list/neighbors/trace2.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


class Fail(Exception):
    pass


def mirror(m):
    return '_'.join(''.join((x[0] + {'L': 'R', 'R': 'L'}[x[1]] + x[2]) if x[2] not in '-Z' else x
                            for x in (r[:3], r[3:])) for r in m.split('_'))


def parse_tmpl(t):
    o, q, rest = t.split(',', 2)
    kv = dict(x.split('=', 1) for x in rest.split(','))
    al, be = map(int, re.match(r'(\d+)d([+-]\d+)', kv['d']).groups())
    alB, beB = map(int, re.match(r'(\d+)b([+-]\d+)', kv['b']).groups())
    dash = lambda s: '' if s == '-' else s
    return dict(O=o, Q=q, P=dash(kv['P']), u=kv['u'], s=dash(kv['s']), al=al, be=be, alB=alB, beB=beB, S=dash(kv['S']))


def kword(T, ds, a, b):
    w = T['P']
    for d in list(ds) + [a]:
        n = T['al'] * d + T['be']
        if n < 0:
            raise Fail(f'negative block {n}')
        w += T['u'] * n + T['s']
    n = T['alB'] * b + T['beB']
    if n < 0:
        raise Fail(f'negative b block {n}')
    return w + T['u'] * n + T['S']


def work_machine(m, T):
    """machine as simulated on the right side (mirrored for O = L)"""
    return mirror(m) if T['O'] == 'L' else m


def tape_word(s):
    lo, hi = s.bounds()
    return ''.join(map(str, s.tape[lo:hi + 1])), lo


def trim(w):
    return w.strip('0')


def validate_template(m, tstr, maxsteps=200_000_000):
    """run trace2 for the first K configuration, then re-simulate literally to that step and compare words"""
    T = parse_tmpl(tstr)
    al, be = T['al'], T['be']
    out = subprocess.run([TRACE2, m, T['O'], T['Q'], T['P'] or '-', T['u'], T['s'] or '-', str(al), str(be),
                          str(T['alB']), str(T['beB']), T['S'] or '-', str(maxsteps), '1'],
                         capture_output=True, text=True, creationflags=LOW).stdout.strip()
    mm = re.match(r'step (\d+): K\(([\d,]*); (\d+); (\d+)\)', out)
    if not mm:
        raise Fail(f'trace2 gave no K: {out!r}')
    step = int(mm.group(1))
    ds = [int(x) for x in mm.group(2).split(',')] if mm.group(2) else []
    a, b = int(mm.group(3)), int(mm.group(4))
    wm = work_machine(m, T)
    s = Sim(wm, size=1 << 18)
    while s.steps < step:
        if not s.step():
            raise Fail('halted before the K step')
    w, lo = tape_word(s)
    exp = kword(T, ds, a, b)
    # exact check: the nonblank part equals the word, head on the cell right of the word
    w1 = w.rstrip('0')
    lo1 = lo + (len(w1) - len(w1.lstrip('0')))
    w1 = w1.lstrip('0')
    if trim(exp) != w1:
        raise Fail(f'template word mismatch at step {step}: tape {w1[:80]}... vs {trim(exp)[:80]}...')
    lead = len(exp) - len(exp.lstrip('0'))
    if s.pos != lo1 - lead + len(exp) or s.state != 'ABCDEFGHIJ'.index(T['Q']):
        raise Fail(f'head/state mismatch at step {step}: pos {s.pos - lo1} state {s.state}')
    return dict(step=step, ds=ds, a=a, b=b, T=T)


def tokens(w):
    """tokenize a word into D(m) = (10)^m 1 tokens and zero gaps: list of ('D', m) / ('G', k)"""
    out = []
    i, n = 0, len(w)
    while i < n:
        if w[i] == '0':
            j = i
            while j < n and w[j] == '0':
                j += 1
            out.append(('G', j - i)); i = j; continue
        m = 0; i += 1
        while i + 1 < n and w[i] == '0' and w[i + 1] == '1':
            m += 1; i += 2
        out.append(('D', m))
    return out


def tokstr(toks, head_tok=None):
    """run-length string of a token list"""
    parts = []
    i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]:
            j += 1
        k, v = toks[i]
        x = (str(v) if k == 'D' else f'_{v}')
        parts.append(x + (f'^{j - i}' if j - i > 1 else ''))
        i = j
    return ' '.join(parts)


def run_to_halt(m, word, head, state, maxs):
    """simulate from (word, head, state); returns ('H', steps, word, headidx, statechar, sym) or ('T', steps)"""
    s = Sim.from_word(m, word, head, state, size=max(1 << 16, 4 * len(word)))
    while s.steps < maxs:
        if not s.step():
            w, lo = tape_word(s)
            return ('H', s.steps, w, s.pos - lo, 'ABCDEFGHIJ'[s.last[0]], s.last[1])
    return ('T', s.steps)


def run_to_event(m, word, head, state, maxs, T, minlen=0):
    """simulate until an undefined read ('H', ...) or the first K-moment of template T after step 0
    ('K', steps, word, headidx): state Q reading 0 right of every 1, tape ending in S"""
    s = Sim.from_word(m, word, head, state, size=max(1 << 16, 4 * len(word)))
    q = 'ABCDEFGHIJ'.index(T['Q']); S = T['S'].rstrip('0'); tz = len(T['S']) - len(S)
    tape = s.tape
    while s.steps < maxs:
        if not s.step():
            w, lo = tape_word(s)
            return ('H', s.steps, w, s.pos - lo, 'ABCDEFGHIJ'[s.last[0]], s.last[1])
        if s.state == q and tape[s.pos] == 0 and s.pos >= s.hi - 1:
            p = s.pos - 1 - tz
            if all(tape[p + 1 + i] == 0 for i in range(tz)) and \
                    ''.join(map(str, tape[p - len(S) + 1:p + 1])) == S and not any(tape[s.pos:s.hi + 1]) and                     s.pos - s.lo > minlen:
                w, lo = tape_word(s)
                return ('K', s.steps, w, s.pos - lo)
    return ('T', s.steps)
