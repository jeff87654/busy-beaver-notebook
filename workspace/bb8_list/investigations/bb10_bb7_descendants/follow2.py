"""Stage follower for champion-core machines (BB(7)/BB(8)-champion descendants), version 2 (repeated blocks).

Follows the REAL run of a machine from the first list exhaustion K(0^n; 0; B) (B = the champion's final
accumulator, astronomically large, residues known: numres.tau()) through alternating stages:
  literal stage : literal simulation (hyb10.exe) from a configuration with symbolic parameters, run for several
                  representative parameter values (all in the real residue class modulo the step), until a halt or a
                  verified champion phase (a K-moment after >= 4 consecutive R1/R2/R3 transitions); the outcome is
                  fitted as an affine function of the parameters.  Item lists are compressed into repeated blocks
                  ((x y z)^k), so lists that grow with a parameter keep their shape.
  rule check    : R1, R2 and R3 are checked literally in front of the champion phase's tail (rule_check).
  jump          : the champion process R1-R3 is run abstractly (closed forms H_d, residues mod QBIG for huge
                  values) to the next event: the borrow reaches a blocking token (D0, D2, D3, the left end of the
                  list) or the a-token bottoms out at D0/D2/D3.  The event configuration is the next stage's input.
A jump that clears a list whose length is itself huge is a "full cycle" (f_omega-type step).
Usage: python follow2.py MACHINE [--n 11] [--template T] [--stages 8] [--budget 200000000] [--log FILE] [--verbose]
Prints "RESULT ..." at the end.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from numres import Num, QBIG, tau, H, r1_rounds

HERE = Path(__file__).resolve().parent
HYB = str(HERE / os.environ.get('HYBEXE', 'hyb10.exe'))
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
TMP = Path(os.environ.get('CLAUDE_JOB_DIR', tempfile.gettempdir())) / 'tmp'
TMP.mkdir(parents=True, exist_ok=True)
CANON = 'B'
STAGE_LOG = []
LEVEL = {}


class Fail(Exception):
    pass


# ------------------------------------------------------------------------------------------- affine -------------
class Aff:
    """const + sum coef_p * p over named parameters, rational coefficients"""

    def __init__(self, const=0, co=None):
        self.c = Fraction(const)
        self.co = {k: Fraction(v) for k, v in (co or {}).items() if v != 0}

    def __add__(self, o):
        o = o if isinstance(o, Aff) else Aff(o)
        co = dict(self.co)
        for k, v in o.co.items():
            co[k] = co.get(k, 0) + v
        return Aff(self.c + o.c, co)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Aff) else Aff(o)
        return self + Aff(-o.c, {k: -v for k, v in o.co.items()})

    def __mul__(self, k):
        return Aff(self.c * k, {p: v * k for p, v in self.co.items()})

    __rmul__ = __mul__

    def is_const(self):
        return not self.co

    def at(self, vals):
        x = self.c + sum(v * vals[k] for k, v in self.co.items())
        if x.denominator != 1:
            raise Fail(f'non-integer value {x} of {self} at {vals}')
        return int(x)

    def num(self, params):
        den = self.c.denominator
        for v in self.co.values():
            den = den * v.denominator // math.gcd(den, v.denominator)
        acc = Num(int(self.c * den))
        for k, v in self.co.items():
            acc = acc + params[k] * int(v * den)
        return acc.divexact(den) if den != 1 else acc

    def __repr__(self):
        parts = [(f'{v}*{k}' if v != 1 else k) for k, v in sorted(self.co.items())]
        if self.c != 0 or not parts:
            parts.append(str(self.c))
        return '+'.join(parts).replace('+-', '-')

    def __eq__(self, o):
        o = o if isinstance(o, Aff) else Aff(o)
        return self.c == o.c and self.co == o.co

    def __hash__(self):
        return hash((self.c, tuple(sorted(self.co.items()))))


def A(x):
    return x if isinstance(x, Aff) else Aff(x)


# ------------------------------------------------------------------------------------------- items --------------
# entry: ('D', m, c) token D(m) x c;  ('J', ((pat, k), ...), c) junk x c;  ('B', (entries...), c) block x c;
#        ('Q', state, 1) head marker (halt / timeout views only)
JRUN = re.compile(r'\((10|01)\)\^(\d+)|([01]):(\d+)')


def parse_items(s):
    out = []
    for tok in s.split():
        cnt = 1
        m = re.fullmatch(r'(.*)\*(\d+)', tok)
        if m:
            tok, cnt = m.group(1), int(m.group(2))
        if tok.startswith('<'):
            runs = []
            for part in tok[1:-1].split('.'):
                g = JRUN.fullmatch(part)
                if not g:
                    raise Fail(f'bad junk part {part!r} in {tok!r}')
                runs.append((g.group(1), int(g.group(2))) if g.group(1) else (g.group(3), int(g.group(4))))
            out.append(('J', tuple(runs), cnt))
        elif tok.startswith('['):
            out.append(('Q', tok[1:-1], cnt))
        else:
            out.append(('D', int(tok), cnt))
    return out


def j2r(entries):
    """junk items -> run entries ('R', (pat, k), 1), so that repeated junk patterns compress into blocks"""
    out = []
    for kind, p, c in entries:
        if kind == 'J':
            for _ in range(c):
                out += [('R', run, 1) for run in p]
        else:
            out.append((kind, p, c))
    return out


def word_of(entries):
    parts = []
    for kind, p, c in entries:
        if kind == 'D':
            parts.append(('10' * p + '1') * c)
        elif kind == 'J':
            parts.append(''.join(pat * k for pat, k in p) * c)
        elif kind == 'R':
            parts.append(p[0] * p[1] * c)
        elif kind == 'B':
            parts.append(word_of(p) * c)
        else:
            raise Fail('head marker in a word')
    return ''.join(parts)


def merge(entries):
    out = []
    for e in entries:
        if out and out[-1][0] == e[0] and e[0] in ('D', 'R') and out[-1][1] == e[1]:
            out[-1] = (e[0], e[1], out[-1][2] + e[2])
        else:
            out.append(e)
    return out


def singles(entries):
    """expand counts (concrete) into single items"""
    out = []
    for kind, p, c in entries:
        if kind == 'B':
            for _ in range(c):
                out += singles(p)
        else:
            out += [(kind, p, 1)] * c
    return out


def compress(entries, maxp=4):
    """concrete entries -> RLE entries, then repeated blocks of 2..maxp RLE entries (>= 3 repetitions)"""
    s = merge(singles(entries))
    out = []
    i, n = 0, len(s)
    while i < n:
        best = None
        for p in range(2, maxp + 1):
            reps = 1
            while i + (reps + 1) * p <= n and s[i + reps * p:i + (reps + 1) * p] == s[i:i + p]:
                reps += 1
            if reps >= 3 and (best is None or reps * p > best[0] * best[1]):
                best = (reps, p)
        if best:
            reps, p = best
            out.append(('B', tuple(s[i:i + p]), reps))
            i += reps * p
        else:
            out.append(s[i])
            i += 1
    return out


def shape_of(entries):
    sh = []
    for k, p, _ in entries:
        if k == 'J':
            sh.append(('J', tuple(pat for pat, _ in p)))
        elif k == 'R':
            sh.append(('R', p[0]))
        elif k == 'B':
            sh.append(('B', shape_of(p)))
        else:
            sh.append((k, None))
    return tuple(sh)


def fields_of(entries):
    f = []
    for k, p, c in entries:
        if k == 'D':
            f += [p, c]
        elif k == 'J':
            f += [kk for _, kk in p] + [c]
        elif k == 'R':
            f += [p[1], c]
        elif k == 'B':
            f += fields_of(p) + [c]
        else:
            f += [c]
    return f


def rebuild(shape, fields, i=0):
    out = []
    for k, sub in shape:
        if k == 'D':
            out.append(('D', fields[i], fields[i + 1])); i += 2
        elif k == 'J':
            n = len(sub)
            out.append(('J', tuple(zip(sub, fields[i:i + n])), fields[i + n])); i += n + 1
        elif k == 'R':
            out.append(('R', (sub, fields[i]), fields[i + 1])); i += 2
        elif k == 'B':
            inner, i = rebuild(sub, fields, i)
            out.append(('B', tuple(inner), fields[i])); i += 1
        else:
            out.append((k, None, fields[i])); i += 1
    return out, i


def inst(sym, vals):
    """symbolic -> concrete entries"""
    out = []
    for kind, p, c in sym:
        cc = A(c).at(vals)
        if cc < 0:
            raise Fail(f'negative count {c} at {vals}')
        if cc == 0:
            continue
        if kind == 'D':
            pp = A(p).at(vals)
            if pp < 0:
                raise Fail(f'negative token {p} at {vals}')
            out.append(('D', pp, cc))
        elif kind == 'J':
            out.append(('J', tuple((pat, A(k).at(vals)) for pat, k in p), cc))
        elif kind == 'R':
            kk = A(p[1]).at(vals)
            if kk < 0:
                raise Fail(f'negative run {p} at {vals}')
            if kk:
                out.append(('R', (p[0], kk), cc))
        elif kind == 'B':
            out.append(('B', tuple(inst(p, vals)), cc))
        else:
            out.append((kind, p, cc))
    return merge(out)


def symc(entries):
    """concrete -> constant symbolic"""
    out = []
    for k, p, c in entries:
        if k == 'D':
            out.append(('D', Aff(p), Aff(c)))
        elif k == 'J':
            out.append(('J', tuple((pat, Aff(n)) for pat, n in p), Aff(c)))
        elif k == 'R':
            out.append(('R', (p[0], Aff(p[1])), Aff(c)))
        elif k == 'B':
            out.append(('B', tuple(symc(p)), Aff(c)))
        else:
            out.append((k, p, Aff(c)))
    return out


def all_affs(sym):
    out = []
    for kind, p, c in sym:
        out.append(A(c))
        if kind == 'D':
            out.append(A(p))
        elif kind == 'J':
            out += [A(k) for _, k in p]
        elif kind == 'R':
            out.append(A(p[1]))
        elif kind == 'B':
            out += all_affs(p)
    return out


def params_in(sym):
    ps = set()
    for kind, p, c in sym:
        ps |= set(A(c).co)
        if kind == 'D':
            ps |= set(A(p).co)
        elif kind == 'J':
            for _, k in p:
                ps |= set(A(k).co)
        elif kind == 'R':
            ps |= set(A(p[1]).co)
        elif kind == 'B':
            ps |= params_in(p)
    return ps


def fmt_sym(sym):
    out = []
    for kind, p, c in sym:
        if kind == 'D':
            s = f'D({p})'
        elif kind == 'J':
            s = '<' + '.'.join(f'{pat}^{k}' for pat, k in p) + '>'
        elif kind == 'R':
            s = f'{p[0]}^{p[1]}' if len(p[0]) == 1 else f'({p[0]})^{p[1]}'
        elif kind == 'B':
            s = '(' + fmt_sym(p) + ')'
        else:
            s = f'[{p}]'
        cs = str(c)
        out.append(s if cs == '1' else f'{s}^{{{cs}}}')
    return ' '.join(out)


# ------------------------------------------------------------------------------------------- hyb10 --------------
def run_hyb(machine, word, maxsteps, extra=(), start=None, canon=None):
    start, canon = start or CANON, canon or CANON
    fd, path = tempfile.mkstemp(suffix='.txt', dir=TMP)
    with os.fdopen(fd, 'w') as f:
        f.write(word)
    try:
        r = subprocess.run([HYB, machine, path, str(len(word)), start, str(maxsteps), '-q', canon, *extra],
                           capture_output=True, text=True, creationflags=LOW)
    finally:
        os.unlink(path)
    lines = r.stdout.strip().splitlines()
    if not lines:
        raise Fail(f'hyb10 gave no output: {r.stderr}')
    last = lines[-1]
    head_, _, body = last.partition(' | ')
    f = head_.split()
    out = {'kind': f[0], 'step': int(f[1]), 'raw': last}
    items = parse_items(body)
    if f[0] == 'J':
        tl = int(f[2].split('=')[1])
        out['e'] = int(f[3].split('=')[1])
        s = singles(items)
        left, tail = s[:len(s) - tl], s[len(s) - tl:]
        if len(left) < 2 or left[-1][0] != 'D' or left[-2][0] != 'D':
            raise Fail('K-moment without a/r tokens')
        out['left'] = compress(j2r(left[:-2])) + [left[-2], left[-1]]
        out['tail'] = compress(j2r(tail))
        out['tail_c'] = tail
    elif f[0] == 'H':
        out['state'], out['read'], out['ones'] = f[2], int(f[3]), int(f[4])
    out['items'] = items
    return out


_RC = {}


def rule_check(machine, tail_entries, e, canon=None):
    canon = canon or CANON
    """literal check that R1, R2 and R3 hold in front of this tail: K-moment [11 7 1 4 | a=4 | r=e | tail],
    prelocked, 30 transitions; passes if R1, R2, R3 all occur and nothing breaks"""
    key = (machine, word_of(tail_entries), e, canon)
    if key in _RC:
        return _RC[key]
    base = [('D', 0, 2), ('D', 7, 1), ('D', 1, 1), ('D', 4, 1), ('D', 4, 1), ('D', e, 1)]
    w = word_of(base) + word_of(tail_entries)
    ntail = len(singles(tail_entries))
    fd, path = tempfile.mkstemp(suffix='.txt', dir=TMP)
    with os.fdopen(fd, 'w') as f:
        f.write(w)
    try:
        r = subprocess.run([HYB, machine, path, str(len(w)), canon, '300000000', '-p', str(ntail), '-e', str(e), '-x',
                            '-v', '30', '-q', canon], capture_output=True, text=True, creationflags=LOW)
    finally:
        os.unlink(path)
    kinds, ok = [], True
    for l in r.stdout.splitlines():
        if l.startswith('V '):
            kinds.append(l.split()[2])
            if len(kinds) >= 30:
                break
        elif l.startswith('U '):
            ok = False
            break
    _RC[key] = (ok and {'R1', 'R2', 'R3'} <= set(kinds), ''.join(k[1] for k in kinds[:30]))
    return _RC[key]


# ------------------------------------------------------------------------------------------- jump ---------------
def num_of(x, params):
    return A(x).num(params)


def jump(left, tail, params, e=2):
    """abstract champion process from a symbolic K-moment left = [..list.., a, r], tail; returns
    (event config, new params, info)"""
    a_e, r_e = left[-2], left[-1]
    ent = list(left[:-2])
    for te in tail:
        if params_in([te]):
            pass                      # parameter-dependent tail is fine (carried along unchanged)
    a = num_of(a_e[1], params)
    r = num_of(r_e[1], params)
    k = len(ent)
    while k > 0 and (ent[k - 1][0] == 'D' or (ent[k - 1][0] == 'B' and all(x[0] == 'D' for x in ent[k - 1][1]))):
        k -= 1
    lft, lst = ent[:k], ent[k:]
    info = {'huge_depth': False, 'levels': []}
    newp = dict(params)

    def mk_r(x):
        if x.exact and x.x <= 20000:
            return Aff(x.x)
        name = f'R{len([p for p in newp if p.startswith("R")]) + 1}'
        newp[name] = x
        return Aff(0, {name: 1})

    def ev(kind, rest, block, zeros, a_new, r_new):
        items = list(rest)
        if block is not None:
            items.append(('D', Aff(block), Aff(1)))
        if not (A(zeros) == Aff(0)):
            items.append(('D', Aff(1), A(zeros)))
        items.append(('D', Aff(a_new), Aff(1)))
        # omega-level of the new accumulator: the inputs' level, +1 if the cleared length is itself huge
        # (the cleared length is the zero count of the event configuration)
        lv_in = max([LEVEL.get(p, 0) for p in params_in(list(left) )] + [0])
        zA = A(zeros)
        zhuge = any(not params[p].exact or params[p].x > 20000 for p in zA.co)
        lv = max(lv_in, 1 + max([LEVEL.get(p, 0) for p in zA.co] + [0])) if zhuge else lv_in
        rr = mk_r(r_new)
        for p in rr.co:
            LEVEL[p] = lv
        info['level'] = lv
        items.append(('D', rr, Aff(1)))
        return items + list(tail), newp, dict(info, event=kind)

    # (1) a-token
    if not a.ge(4):
        if a.x != 1:
            return ev('a-block', lft + lst, None, 0, a.x, r)
    else:
        bot = {1: 1, 2: 2, 0: 3}[a.m(3)]
        u = (a - bot).divexact(3)
        r = r1_rounds(u, r, e)
        if bot != 1:
            return ev('a-block', lft + lst, None, 0, bot, r)
    # (2) the list, from the right; zeros = zero tokens right of the current position (symbolic and Num)
    zeros, zn = Aff(0), Num(0)
    lst = list(lst)
    t = tau(e)

    def clear_token(mv, depth, r):
        """borrow a standard token (value mv = 1 mod 3) down to D1 at the given depth; returns r"""
        m = num_of(mv, params)
        u = (m - 1).divexact(3)
        return H(depth.x if depth.exact else 'huge', u, r, e)

    def nonstd(rest, mv, zeros, zn):
        """r not = e mod 3 at a borrow: the refilled neighbour bottoms out"""
        m = num_of(mv, params)
        d = zn + 1
        v = r * 2 + (7 - 2 * e)
        bot = {0: 3, 2: 2}[v.m(3)]
        u = (v - bot).divexact(3)
        dep = d - 1
        rr = r1_rounds(u, Num(e), e) if dep.eq(0) else H(dep.x if dep.exact else 'huge', u, Num(e), e)
        rest = rest + [('D', A(mv) - 3, Aff(1))]
        if dep.eq(0):
            return ev('a-block', rest, None, zeros, bot, rr)
        return ev('block', rest, bot, A(zeros) - 1, 1, rr)

    while True:
        if not lst:
            return ev('left', lft, None, zeros, 1, r)
        kind, pv, cv = lst[-1]
        cn = num_of(cv, params)
        if kind == 'D':
            m = num_of(pv, params)
            if m.eq(1):
                lst.pop(); zeros = zeros + A(cv); zn = zn + cn
                continue
            rest = lst[:-1] + ([('D', pv, A(cv) - 1)] if not (A(cv) - 1 == Aff(0)) else [])
            if not m.ge(4):
                return ev('block', lft + rest, m.x, zeros, 1, r)
            if r.m(3) != e % 3:
                return nonstd(lft + rest, pv, zeros, zn)
            bot = {1: 1, 2: 2, 0: 3}[m.m(3)]
            d = zn + 1
            if not d.exact:
                info['huge_depth'] = True
            if bot != 1:
                u = (m - bot).divexact(3)
                r = H(d.x if d.exact else 'huge', u, r, e)
                return ev('block', lft + rest, bot, zeros, 1, r)
            if cn.exact and cn.x <= 64:
                for i in range(cn.x):
                    r = clear_token(pv, d + i, r)
            else:
                for i in range(8):
                    r = clear_token(pv, d + i, r)
                if not (r == t):
                    raise Fail(f'accumulator did not reach the fixed point: {r}')
                info['huge_depth'] = True
            lst.pop(); zeros = zeros + A(cv); zn = zn + cn
            continue
        # a block of tokens (inner tuple), repeated cv times
        inner = list(pv)
        ivals = [(num_of(x[1], params), num_of(x[2], params), x) for x in inner]
        if any(not c.exact for _, c, _ in ivals):
            raise Fail('block with symbolic inner counts')
        flat = []
        for m, c, x in ivals:
            flat += [(m, x[1])] * c.x
        nonstd_idx = [i for i, (m, _) in enumerate(flat) if m.m(3) != 1 or m.eq(1) is False and not m.ge(1)]
        bad = [i for i, (m, _) in enumerate(flat) if m.m(3) != 1]
        if not bad:
            # every inner token is a standard digit (or a zero): clear all copies
            if r.m(3) != e % 3:
                raise Fail('non-standard accumulator in front of a block')
            reps = cn.x if cn.exact and cn.x <= 64 // max(1, len(flat)) else 8
            for _ in range(reps):
                for m, mv in reversed(flat):
                    if m.eq(1):
                        zn = zn + 1
                        continue
                    r = clear_token(mv, zn + 1, r)
                    zn = zn + 1
            if not (cn.exact and cn.x <= 64 // max(1, len(flat))):
                if not (r == t):
                    raise Fail(f'accumulator did not reach the fixed point (block): {r}')
                info['huge_depth'] = True
                zn = zn + (cn - reps) * len(flat)
            lst.pop()
            zeros = zeros + A(cv) * len(flat)
            continue
        # the last copy contains a non-standard token at flat index j (rightmost)
        j = bad[-1]
        for m, mv in reversed(flat[j + 1:]):
            if m.eq(1):
                zn = zn + 1; zeros = zeros + 1
                continue
            if r.m(3) != e % 3:
                raise Fail('non-standard accumulator inside a block')
            r = clear_token(mv, zn + 1, r)
            zn = zn + 1; zeros = zeros + 1
        rest = lst[:-1]
        if not (A(cv) - 1 == Aff(0)):
            rest = rest + [('B', pv, A(cv) - 1)]
        rest = rest + [('D', mv, Aff(1)) for m, mv in flat[:j]]
        m, mv = flat[j]
        if not m.ge(4):
            return ev('block', lft + rest, m.x, zeros, 1, r)
        if r.m(3) != e % 3:
            return nonstd(lft + rest, mv, zeros, zn)
        bot = {2: 2, 0: 3}[m.m(3)]
        u = (m - bot).divexact(3)
        d = zn + 1
        r = H(d.x if d.exact else 'huge', u, r, e)
        return ev('block', lft + rest, bot, zeros, 1, r)


# ------------------------------------------------------------------------------------------- fitting ------------
RANK_LB = {1: 6, 2: 200, 3: 200, 4: 200}
STEPS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 28, 30, 35, 36, 42, 45, 48, 56, 60,
         70, 72, 84, 90, 105, 120, 126, 140, 168, 180, 210, 252, 280, 315, 360, 420]
VAL = 12
KS = 22
RUNIT = int(os.environ.get('FOLLOW_RUNIT', '3'))


def rep_base(val, m, lb):
    r = val.m(m)
    return lb + ((r - lb) % m)


def fit_values(xs, ys):
    a = Fraction(ys[1] - ys[0], xs[1] - xs[0])
    b = ys[0] - a * xs[0]
    return (a, b) if all(a * x + b == y for x, y in zip(xs, ys)) else None


class Stage:
    def __init__(self, machine, sym, params, ranks, budget, log, verbose=False, start=None):
        self.machine, self.sym, self.params, self.ranks = machine, sym, params, ranks
        self.budget, self.log, self.verbose = budget, log, verbose
        self.cache = {}
        self.start = start or CANON       # state of the head at the right end of the input word
        self.q = self.start               # canonical state used to detect K-moments

    def run_at(self, vals, budget=None):
        budget = budget or self.budget
        key = (self.q,) + tuple(sorted(vals.items()))
        c = self.cache.get(key)
        if c is None or (c['kind'] == 'T' and c['step'] < budget):
            w = word_of(inst(self.sym, vals))
            out = run_hyb(self.machine, w, budget, start=self.start, canon=self.q)
            out['q'] = self.q
            if self.verbose:
                self.log(f'    run {vals}: {out["raw"][:200]}')
            self.cache[key] = out
        return self.cache[key]

    @staticmethod
    def sig(o):
        if o['kind'] == 'J':
            return ('J', o['e'], shape_of(o['left']), shape_of(o['tail']))
        return (o['kind'],)

    def run(self):
        """period search by consecutive sampling: for each symbolic parameter p, K values base + j*unit (unit 1, or
        3 for accumulators); the outcome signatures give the period P; the real class mod P is fitted (>= 4 points)
        and validated on further points of that class."""
        ps = sorted(params_in(self.sym))
        exact = {p: self.params[p].x for p in ps if self.params[p].exact and self.params[p].x <= 20000}
        sym_ps = [p for p in ps if p not in exact]
        if not sym_ps:
            o = self.run_at(exact)
            res = {'kind': o['kind'], 'out': o, 'vals': exact, 'period': 0}
            if o['kind'] == 'J':
                res['left'], res['tail'], res['e'] = symc(o['left']), symc(o['tail']), o['e']
            elif o['kind'] == 'H':
                res['ones'] = Aff(o['ones']); res['halt_state'] = (o['state'], o['read'])
            return res
        # FOLLOW_RUNIT (env): sampling step for huge accumulators R (default 3).  A multiple of 3 such as 120 keeps every
        # sample in the real residue class mod 120 (needed when the outcome is not periodic over all residues mod 3)
        unit = {p: (RUNIT if p.startswith('R') else 1) for p in sym_ps}
        # rational coefficients in the input (e.g. (12b-30)/7 groups) restrict a parameter to a residue class
        for p in sym_ps:
            for x in all_affs(self.sym):
                if p in x.co:
                    d = x.co[p].denominator
                    for q in x.co:
                        d = d * x.co[q].denominator // math.gcd(d, x.co[q].denominator)
                    d = d * x.c.denominator // math.gcd(d, x.c.denominator)
                    unit[p] = unit[p] * d // math.gcd(unit[p], d)
        base = dict(exact)
        for p in sym_ps:
            base[p] = rep_base(self.params[p], unit[p], RANK_LB[self.ranks.get(p, 1)])
        o0 = self.run_at(base)
        if o0['kind'] == 'T':
            # no K-moment in the input's state: try the other canonical states (K-moments of another phase)
            n = len(self.machine.split('_'))
            for q in [chr(65 + i) for i in range(n)]:
                if q == self.q:
                    continue
                self.q = q
                o1 = self.run_at(base)
                if o1['kind'] in ('J', 'H'):
                    o0 = o1
                    self.log(f'  (K-moments found in state {q})')
                    break
            else:
                self.q = self.start
        if o0['kind'] == 'T':
            return {'kind': 'T', 'out': o0, 'vals': base, 'period': None}
        sub_budget = min(self.budget, 30 * o0['step'] + 20_000_000)
        periods = {}
        for p in sym_ps:
            sigs, flds = [], []
            for j in range(KS):
                v = dict(base); v[p] = base[p] + j * unit[p]
                o = self.run_at(v, sub_budget if j else None)
                sigs.append(self.sig(o))
                flds.append((fields_of(o['left']) + fields_of(o['tail'])) if o['kind'] == 'J' else
                            [o['ones']] if o['kind'] == 'H' else [])
            P = None
            for cand in range(1, (KS - 1) // 3 + 1):
                # candidate classes j = 0 mod cand: same signature and every field affine in j
                js = list(range(0, KS, cand))
                if len(js) < 4 or sigs[0][0] not in ('J', 'H') or any(sigs[j] != sigs[0] for j in js):
                    continue
                if all(fit_values(js, [flds[j][i] for j in js]) is not None for i in range(len(flds[0]))):
                    P = cand
                    break
            if P is None:
                # shape period P0 from the signatures, then larger periods P0*m tried with direct real-class samples
                P0 = next((c for c in range(1, KS // 2 + 1) if all(sigs[j] == sigs[j + c] for j in range(KS - c))), None)
                if P0 is None or sigs[0][0] not in ('J', 'H'):
                    raise Fail(f'no period for {p}: ' + ''.join(s[0] for s in sigs))
                for mult in (2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 21):
                    cand = P0 * mult
                    if cand <= (KS - 1) // 3:
                        continue
                    xs = [base[p] + j * cand * unit[p] for j in range(4)]
                    outs_ = []
                    for x in xs:
                        v = dict(base); v[p] = x
                        outs_.append(self.run_at(v, None))
                    if any(self.sig(o) != sigs[0] for o in outs_):
                        continue
                    ff = [(fields_of(o['left']) + fields_of(o['tail'])) if o['kind'] == 'J' else [o['ones']] for o in outs_]
                    if all(fit_values(list(range(4)), [f_[i] for f_ in ff]) is not None for i in range(len(ff[0]))):
                        P = cand
                        break
                if P is None:
                    raise Fail(f'no period for {p} (shape period {P0}): ' + ''.join(s[0] for s in sigs))
            periods[p] = P
        # the real residue class: base must be in the real class mod P*unit; shift base accordingly
        rbase = dict(exact)
        for p in sym_ps:
            m = periods[p] * unit[p]
            rbase[p] = rep_base(self.params[p], m, RANK_LB[self.ranks.get(p, 1)])
        pts = [rbase]
        for p in sym_ps:
            for k in (1, 2, 3):
                v = dict(rbase); v[p] = rbase[p] + k * periods[p] * unit[p]; pts.append(v)
        if len(sym_ps) > 1:
            v = dict(rbase)
            for p in sym_ps:
                v[p] = rbase[p] + periods[p] * unit[p]
            pts.append(v)
        outs = [self.run_at(v) for v in pts]
        sig0 = self.sig(outs[0])
        if any(self.sig(o) != sig0 for o in outs) or sig0[0] not in ('J', 'H'):
            raise Fail(f'periods {periods}: real-class samples disagree: ' + ''.join(self.sig(o)[0] for o in outs))
        kind = sig0[0]
        F = [fields_of(o['left']) + fields_of(o['tail']) for o in outs] if kind == 'J' else [[o['ones']] for o in outs]
        fitted = []
        for i in range(len(F[0])):
            aff = self.fit_multi(sym_ps, pts, [f[i] for f in F])
            if aff is None:
                break
            fitted.append(aff)
        res = {'kind': kind, 'period': periods, 'vals': pts[0], 'out': outs[0]}
        if len(fitted) < len(F[0]):
            if kind == 'H':
                res['halt_state'] = (outs[0]['state'], outs[0]['read'])
                res['ones'] = 'non-affine: ' + ', '.join(f"{o['ones']}@{v}" for o, v in zip(outs, pts))
                return res
            raise Fail(f'periods {periods}: non-affine fields')
        # validation: a point in the real class modulo lcm(P*unit, VAL)
        vpt = dict(exact)
        for p in sym_ps:
            m = periods[p] * unit[p]
            L = m * VAL // math.gcd(m, VAL)
            x = rep_base(self.params[p], L, RANK_LB[self.ranks.get(p, 1)])
            while any(x == q[p] for q in pts):
                x += L
            vpt[p] = x
        vo = self.run_at(vpt)
        vf = (fields_of(vo['left']) + fields_of(vo['tail'])) if vo['kind'] == 'J' else [vo.get('ones')]
        if self.sig(vo) != sig0 or any(f.at(vpt) != y for f, y in zip(fitted, vf)):
            raise Fail(f'periods {periods}: validation at {vpt} failed ({self.sig(vo)[0]})')
        res['validated'] = vpt
        if kind == 'J':
            nl = len(fields_of(outs[0]['left']))
            res['left'] = rebuild(shape_of(outs[0]['left']), fitted[:nl])[0]
            res['tail'] = rebuild(shape_of(outs[0]['tail']), fitted[nl:])[0]
            res['e'] = outs[0]['e']
        else:
            res['ones'] = fitted[0]
            res['halt_state'] = (outs[0]['state'], outs[0]['read'])
        return res

    def quick(self, rres):
        """accept a reference machine's fitted result for this stage if this machine agrees at the reference's base
        point and validation point (signature and every fitted field / the ones count)"""
        if rres['kind'] not in ('J', 'H') or not isinstance(rres.get('ones', Aff(0)), Aff) and rres['kind'] == 'H':
            return None
        pts = [rres['vals']]
        per = rres.get('period')
        if isinstance(per, dict) and per:
            p = sorted(per)[0]
            v = dict(rres['vals']); v[p] = v[p] + per[p] * (3 if p.startswith('R') else 1)
            pts.append(v)
        outs = []
        for v in pts:
            o = self.run_at(v)
            if o['kind'] != rres['kind']:
                return None
            if o['kind'] == 'J':
                if o['e'] != rres['e'] or shape_of(o['left']) != shape_of(rres['left']) or shape_of(o['tail']) != shape_of(rres['tail']):
                    return None
                exp = fields_of(rres['left']) + fields_of(rres['tail'])
                got = fields_of(o['left']) + fields_of(o['tail'])
                if any(A(f).at(v) != y for f, y in zip(exp, got)):
                    return None
            elif A(rres['ones']).at(v) != o['ones']:
                return None
            outs.append(o)
        res = dict(rres)
        res['out'] = outs[0]
        return res

    def fit_multi(self, sym_ps, pts, ys):
        base, co, idx = pts[0], {}, 1
        for p in sym_ps:
            f = fit_values([base[p]] + [pts[idx + k][p] for k in range(3)], [ys[0]] + [ys[idx + k] for k in range(3)])
            if f is None:
                return None
            co[p] = f[0]
            idx += 3
        aff = Aff(0, co)
        aff.c = Fraction(ys[0]) - sum(v * base[k] for k, v in co.items())
        if any(aff.c + sum(cv * v[k] for k, cv in co.items()) != y for v, y in zip(pts, ys)):
            return None
        return aff


# ------------------------------------------------------------------------------------------- driver -------------
TRX = re.compile(r'([LR]),([A-P]),P=([01-]*),u=([01]+),s=([01]+),d=(\d+)d\+(\d+),b=(\d+)b\+(\d+),S=([01-]*)$')


def kword_sym(n, template=None):
    """K(0^n; 0; b) with b symbolic.  Default: the BB(7) champion template 11 D1^n D1 (10)^(3b+2) 111001.
    With a dlscan2 template R,Q,P=..,u=..,s=..,d=xd+y,b=zb+w,S=..: P (u^y s)^(n+1) u^(zb+w) S as raw runs."""
    if template is None:
        return [('D', Aff(0), Aff(2)), ('D', Aff(1), Aff(n + 1)), ('D', Aff(2, {'b': 3}), Aff(1)),
                ('D', Aff(0), Aff(1)), ('J', (('1', Aff(1)), ('0', Aff(2)), ('1', Aff(1))), Aff(1))]
    g = TRX.match(template)
    if not g or g.group(1) != 'R':
        raise Fail(f'unsupported template {template}')
    side, q, P, u, s, al, be, alB, beB, S = g.groups()
    P = '' if P == '-' else P
    S = '' if S == '-' else S
    runs = [(ch, Aff(1)) for ch in P]
    for _ in range(n + 1):
        runs.append((u, Aff(int(be))))
        runs += [(ch, Aff(1)) for ch in s]
    runs.append((u, Aff(int(beB), {'b': int(alB)})))
    runs += [(ch, Aff(1)) for ch in S]
    return [('J', tuple(runs), Aff(1))]


def follow(machine, n=11, stages=8, budget=200_000_000, log=print, verbose=False, template=None, ref=None, blank=False):
    B = (tau() - 2).divexact(3)
    params, ranks = {'b': B}, {'b': 1}
    sym = [] if blank else kword_sym(n, template)
    history, cycles = [], 0
    shapes = []
    stage_start = 'A' if blank else CANON
    for s in range(stages):
        shapes.append(shape_of(sym))
        consts = tuple(str(x) for x in fields_of(sym) if A(x).is_const())
        shapes[-1] = (shapes[-1], consts)
        if len(shapes) >= 3 and shapes[-1] == shapes[-2] == shapes[-3]:
            prev = fields_of(prev_sym)
            cur = fields_of(sym)
            deltas = [f'{A(c)} <- {A(p)}' for p, c in zip(prev, cur) if not (A(p) == A(c))]
            log(f'  LOOP: the stage input shape repeated 3 times; changed fields: {deltas}')
            history.append(('LOOP', len(deltas)))
            return {'result': 'LOOP', 'stages': s, 'full_cycles': cycles, 'history': history}
        prev_sym = sym
        st = Stage(machine, sym, params, ranks, budget, log, verbose, start=stage_start)
        log(f'stage {s}: input {fmt_sym(sym)}')
        res = None
        if ref is not None and s < len(ref) and ref[s][0] == fmt_sym(sym):
            res = st.quick(ref[s][1])
            if res is not None:
                log('  (reference stage result confirmed at 2 points)')
        if res is None:
            res = st.run()
        STAGE_LOG.append((fmt_sym(sym), {k: v for k, v in res.items() if k != 'out'}))
        if res['kind'] == 'H':
            log(f'  HALT (step {res["period"]}): ones = {res["ones"]}, state {res["halt_state"]}')
            history.append(('H', str(res['ones'])))
            return {'result': 'HALT', 'stages': s + 1, 'full_cycles': cycles, 'ones': res['ones'], 'history': history}
        if res['kind'] != 'J':
            log(f'  outcome {res["kind"]} (step {res.get("period")}) at {res["vals"]}: {res["out"]["raw"][:300]}')
            history.append((res['kind'],))
            return {'result': 'UNCLEAR-' + res['kind'], 'stages': s + 1, 'full_cycles': cycles, 'history': history}
        e = res['e']
        log(f'  champion phase (step {res["period"]}, e={e}): {fmt_sym(res["left"])} | tail {fmt_sym(res["tail"])}')
        tail_c = res['out']['tail_c']
        rc_ok, rc_seq = rule_check(machine, tail_c, e, st.q)
        log(f'  rule check R1-R3 in front of this tail: {"PASS" if rc_ok else "FAIL"} ({rc_seq})')
        if not rc_ok:
            history.append(('RULES-FAIL',))
            return {'result': 'UNCLEAR-RULES', 'stages': s + 1, 'full_cycles': cycles, 'history': history}
        ev_sym, params2, info = jump(res['left'], res['tail'], params, e)
        for p in params2:
            if p not in ranks:
                ranks[p] = min(4, max(ranks.values()) + 1)
        newp = {k: str(v) for k, v in params2.items() if k not in params}
        params = params2
        big = info['huge_depth']
        cycles += 1 if big else 0
        log(f'  jump -> event {info["event"]}, huge-length list cleared: {big}; omega-level {info.get("level", 0)}; new params {newp}')
        log(f'  event config: {fmt_sym(ev_sym)}')
        history.append(('J', info['event'], big))
        sym = ev_sym
        stage_start = st.q
    return {'result': 'MAXSTAGES', 'stages': stages, 'full_cycles': cycles, 'history': history}


def main():
    global CANON
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('--n', type=int, default=11)
    ap.add_argument('--template')
    ap.add_argument('--blank', action='store_true', help='start from the blank tape (state A) instead of K(0^n;0;B)')
    ap.add_argument('--stages', type=int, default=8)
    ap.add_argument('--budget', type=int, default=200_000_000)
    ap.add_argument('--log')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--ref', help='reference machine whose logs/<ref>.stages.pkl results are reused when confirmed')
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None

    def log(s):
        print(s, flush=True)
        if lf:
            lf.write(s + '\n'); lf.flush()

    if a.template:
        CANON = a.template.split(',')[1]
    log(f'machine {a.machine}' + (f' template {a.template} n={a.n}' if a.template else ''))
    try:
        import pickle
        ref = None
        if a.ref:
            rp = HERE / 'logs' / f'{a.ref}.stages.pkl'
            if rp.exists():
                ref = pickle.loads(rp.read_bytes())
        try:
            r = follow(a.machine, a.n, a.stages, a.budget, log, a.verbose, a.template, ref, a.blank)
        finally:
            (HERE / 'logs' / f'{a.machine}.stages.pkl').write_bytes(pickle.dumps(STAGE_LOG))
        log(f'RESULT {r["result"]} stages={r["stages"]} full_cycles={r["full_cycles"]} level={max(LEVEL.values(), default=0)} history={r["history"]}'
            + (f' ones={r["ones"]}' if 'ones' in r else ''))
    except Fail as ex:
        log(f'RESULT FAIL {ex}')


if __name__ == '__main__':
    main()
