"""Stage follower for champion-core machines (BB(7)-champion descendants).

Follows the REAL run of a machine from the first list exhaustion K(0^n; 0; B) (B = the BB(7) champion's final
accumulator, astronomically large, residues known: numres.tau()) through alternating stages:
  literal stage : literal simulation (hyb10.exe) from a configuration with symbolic parameters, run for several
                  representative parameter values, until a halt or a verified champion phase (K-moment where R1-R3
                  provably drive the run for >= 4 transitions); the outcomes are fitted as affine functions of
                  the parameters (period search over the residue classes the real parameters lie in).
  jump          : the champion process R1-R3 is run abstractly (closed forms H_d, residues mod QBIG for huge
                  values) to the next event: the borrow reaches a blocking token (D0, D2, D3, junk/left end) or the
                  a-token bottoms out at D0/D2/D3.  The event configuration is the next stage's input.
Usage: python follow.py MACHINE [--n 11] [--stages 8] [--budget 400000000] [--log FILE] [--verbose]
Outcome classes printed at the end (one line "RESULT ..."): see classify().
"""
from __future__ import annotations

import argparse
import itertools
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


class Fail(Exception):
    pass


# --------------------------------------------------------------------------------------------- items ------------
# entry: ('D', m, c)  token D(m) repeated c times;  ('J', ((pat, k), ...), c)  junk segment repeated c times;
#        ('Q', state, 1) head marker (halt / timeout views only)
JRUN = re.compile(r'\((10|01)\)\^(\d+)|([01]):(\d+)')


def parse_items(s):
    out = []
    for tok in s.split():
        cnt = 1
        m = re.fullmatch(r'(.*)\*(\d+)', tok)
        if m and not tok.endswith('>') or (m and tok.endswith('>') is False):
            pass
        if m:
            tok, cnt = m.group(1), int(m.group(2))
        if tok.startswith('<'):
            runs = []
            for part in tok[1:-1].split('.'):
                g = JRUN.fullmatch(part)
                if not g:
                    raise Fail(f'bad junk part {part!r} in {tok!r}')
                if g.group(1):
                    runs.append((g.group(1), int(g.group(2))))
                else:
                    runs.append((g.group(3), int(g.group(4))))
            out.append(('J', tuple(runs), cnt))
        elif tok.startswith('['):
            out.append(('Q', tok[1:-1], cnt))
        else:
            out.append(('D', int(tok), cnt))
    return out


def word_of(entries):
    parts = []
    for kind, p, c in entries:
        if kind == 'D':
            parts.append(('10' * p + '1') * c)
        elif kind == 'J':
            parts.append(''.join(pat * k for pat, k in p) * c)
        else:
            raise Fail('head marker in a word')
    return ''.join(parts)


def fmt_entries(entries):
    out = []
    for kind, p, c in entries:
        if kind == 'D':
            s = str(p)
        elif kind == 'J':
            s = '<' + '.'.join(f'({pat})^{k}' if len(pat) == 2 else f'{pat}:{k}' for pat, k in p) + '>'
        else:
            s = f'[{p}]'
        out.append(s if c == 1 else f'{s}*{c}')
    return ' '.join(out)


def flatten_right(entries, n):
    """the last n single items (count-expanded) of an entry list, plus the remaining entry list"""
    ent = list(entries)
    tail = []
    while len(tail) < n:
        if not ent:
            raise Fail('tail longer than the list')
        kind, p, c = ent.pop()
        one = Aff(1) if isinstance(c, Aff) else 1
        if isinstance(c, Aff) and c.is_const():
            c = int(c.c)
            one = 1
        if (isinstance(c, Aff)) or c > 1:
            ent.append((kind, p, c - 1))
        tail.insert(0, (kind, p, Aff(1)))
    return ent, tail


# --------------------------------------------------------------------------------------------- hyb10 ------------
CANON = 'B'


def run_hyb(machine, word, maxsteps, head=None, state=None, extra=()):
    state = state or CANON
    extra = tuple(extra) + ('-q', CANON)
    fd, path = tempfile.mkstemp(suffix='.txt', dir=TMP)
    with os.fdopen(fd, 'w') as f:
        f.write(word)
    try:
        h = len(word) if head is None else head
        r = subprocess.run([HYB, machine, path, str(h), state, str(maxsteps), *extra], capture_output=True, text=True,
                           creationflags=LOW)
    finally:
        os.unlink(path)
    lines = r.stdout.strip().splitlines()
    if not lines:
        raise Fail(f'hyb10 gave no output: {r.stderr}')
    last = lines[-1]
    head_, _, body = last.partition(' | ')
    f = head_.split()
    out = {'kind': f[0], 'step': int(f[1]), 'items': parse_items(body), 'raw': last}
    if f[0] == 'J':
        out['tail'] = int(f[2].split('=')[1])
        out['e'] = int(f[3].split('=')[1]) if len(f) > 3 and f[3].startswith('e=') else 2
    elif f[0] == 'H':
        out['state'], out['read'], out['ones'] = f[2], int(f[3]), int(f[4])
    return out


# --------------------------------------------------------------------------------------------- affine -----------
class Aff:
    """beta + sum alpha_p * p over named parameters, rational coefficients"""

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

    def is_const(self):
        return not self.co

    def at(self, vals):
        x = self.c + sum(v * vals[k] for k, v in self.co.items())
        if x.denominator != 1:
            raise Fail(f'non-integer value {x} of {self} at {vals}')
        return int(x)

    def num(self, params):
        """evaluate at the real parameters (Num)"""
        den = self.c.denominator
        for v in self.co.values():
            den = den * v.denominator // __import__('math').gcd(den, v.denominator)
        acc = Num(int(self.c * den))
        for k, v in self.co.items():
            acc = acc + params[k] * int(v * den)
        return acc.divexact(den) if den != 1 else acc

    def __repr__(self):
        parts = []
        for k, v in sorted(self.co.items()):
            parts.append(f'{v}*{k}' if v != 1 else k)
        if self.c != 0 or not parts:
            parts.append(str(self.c))
        return '+'.join(parts).replace('+-', '-')

    def __eq__(self, o):
        o = o if isinstance(o, Aff) else Aff(o)
        return self.c == o.c and self.co == o.co


def sym_inst(sym, vals):
    """symbolic entries -> concrete entries"""
    out = []
    for kind, p, c in sym:
        cc = c.at(vals) if isinstance(c, Aff) else c
        if cc < 0:
            raise Fail(f'negative count {c} at {vals}')
        if cc == 0:
            continue
        if kind == 'D':
            pp = p.at(vals) if isinstance(p, Aff) else p
            if pp < 0:
                raise Fail(f'negative token {p} at {vals}')
            out.append(('D', pp, cc))
        elif kind == 'J':
            runs = tuple((pat, k.at(vals) if isinstance(k, Aff) else k) for pat, k in p)
            out.append(('J', runs, cc))
        else:
            out.append((kind, p, cc))
    return merge(out)


def merge(entries):
    out = []
    for e in entries:
        if out and out[-1][0] == e[0] == 'D' and out[-1][1] == e[1]:
            out[-1] = ('D', e[1], out[-1][2] + e[2])
        else:
            out.append(e)
    return out


def shape_of(entries):
    return tuple((k, tuple(pat for pat, _ in p) if k == 'J' else None) for k, p, _ in entries)


def fields_of(entries):
    f = []
    for k, p, c in entries:
        if k == 'D':
            f += [p, c]
        elif k == 'J':
            f += [kk for _, kk in p] + [c]
        else:
            f += [c]
    return f


def rebuild_sym(shape, fields):
    out, i = [], 0
    for k, pats in shape:
        if k == 'D':
            out.append(('D', fields[i], fields[i + 1])); i += 2
        elif k == 'J':
            n = len(pats)
            out.append(('J', tuple(zip(pats, fields[i:i + n])), fields[i + n])); i += n + 1
        else:
            out.append((k, None, fields[i])); i += 1
    return out


# --------------------------------------------------------------------------------------------- jump -------------
def bottom(m):
    return {0: 3, 1: 1, 2: 2}[m % 3] if True else None


def jump(sym_items, tail_len, params, log, e=2):
    """abstract champion process from a symbolic K-moment; returns (event_items_sym, new_params, info)"""
    ent, tail = flatten_right(sym_items, tail_len + 2)
    a_e, r_e = tail[0], tail[1]
    tail = tail[2:]
    if a_e[0] != 'D' or r_e[0] != 'D':
        raise Fail('K-moment without a/r tokens')
    for te in tail:
        if any(isinstance(x, Aff) and not x.is_const() for x in ([te[1]] if te[0] == 'D' else [k for _, k in te[1]])):
            raise Fail('parameter-dependent tail')
    a = a_e[1].num(params) if isinstance(a_e[1], Aff) else Num(a_e[1])
    r = r_e[1].num(params) if isinstance(r_e[1], Aff) else Num(r_e[1])
    # list part: maximal run of D entries at the right end of ent
    k = len(ent)
    while k > 0 and ent[k - 1][0] == 'D':
        k -= 1
    left, lst = ent[:k], ent[k:]
    info = {'depth': Aff(0), 'huge_depth': False, 'levels': []}
    newp = dict(params)

    def mk_r(x, tag):
        """the final accumulator as an Aff (new parameter if huge or big)"""
        if x.exact and x.x <= 20000:
            return Aff(x.x)
        name = f'R{len([p for p in newp if p.startswith("R")]) + 1}'
        newp[name] = x
        return Aff(0, {name: 1})

    def ev(kind, left_entries, block, zeros, a_new, r_new):
        items = list(left_entries)
        if block is not None:
            items.append(('D', Aff(block), Aff(1)))
        if not (isinstance(zeros, Aff) and zeros == Aff(0)):
            items.append(('D', Aff(1), zeros))
        items.append(('D', Aff(a_new), Aff(1)))
        items.append(('D', mk_r(r_new, kind), Aff(1)))
        items += [(te[0], te[1], te[2]) for te in tail]
        return items, newp, dict(info, event=kind)

    # (1) a-token
    am3 = a.m(3)
    if not a.ge(4):
        if a.x != 1:
            return ev('a-block', left + lst, None, Aff(0), a.x, r)
    else:
        bot = {1: 1, 2: 2, 0: 3}[am3]
        u = (a - bot).divexact(3)
        r = r1_rounds(u, r, e)
        info['levels'].append(('a', u))
        if bot != 1:
            return ev('a-block', left + lst, None, Aff(0), bot, r)
    # (2) list from the right
    zeros = Aff(0)            # number of zero tokens right of the current position (symbolic)
    zeros_num = Num(0)
    lst = list(lst)
    while True:
        if not lst:
            return ev('left', left, None, zeros, 1, r)
        kind, mv, cv = lst[-1]
        m = mv.num(params) if isinstance(mv, Aff) else Num(mv)
        c = cv
        if m.eq(1):
            lst.pop()
            zeros = zeros + c
            zeros_num = zeros_num + (c.num(params) if isinstance(c, Aff) else Num(c))
            continue
        if not m.ge(4):
            # blocking token (0, 2, 3)
            rest = lst[:-1] + ([('D', mv, c - 1)] if not (c - 1 == Aff(0)) else [])
            return ev('block', left + rest, m.x, zeros, 1, r)
        d = zeros_num + 1                       # tokens to the right of the borrowed copy, a included
        dd = d.x if d.exact else 'huge'
        if d.exact is False:
            info['huge_depth'] = True
        if r.m(3) != e % 3:
            # non-standard accumulator: the first refill is non-standard and bottoms out
            m2 = m - 3
            v = r * 2 + (7 - 2 * e)
            bot = {0: 3, 2: 2}[v.m(3)]
            u = (v - bot).divexact(3)
            dep = d - 1
            rr = r1_rounds(u, Num(e), e) if dep.eq(0) else H(dep.x if dep.exact else 'huge', u, Num(e), e)
            info['levels'].append(('nonstd', d))
            rest = lst[:-1] + ([('D', mv, c - 1)] if not (c - 1 == Aff(0)) else [])
            rest.append(('D', Aff(m2.x) if m2.exact else (mv - 3), Aff(1)))
            if dep.eq(0):
                return ev('a-block', left + rest, None, zeros, bot, rr)
            # the refilled token is the zero just right of the borrowed one
            return ev('block', left + rest, bot, zeros - 1, 1, rr)
        bot = {1: 1, 2: 2, 0: 3}[m.m(3)]
        # copies of this entry: process copy by copy (exact small counts) or as a block
        cn = c.num(params) if isinstance(c, Aff) else Num(c)
        u = (m - bot).divexact(3)
        if bot != 1:
            r = H(dd if dd != 'huge' else 'huge', u, r, e)
            info['levels'].append(('block-entry', d))
            rest = lst[:-1] + ([('D', mv, c - 1)] if not (c - 1 == Aff(0)) else [])
            return ev('block', left + rest, bot, zeros, 1, r)
        # standard digits: clear all copies
        t = tau(e)
        if cn.exact and cn.x <= 64:
            for i in range(cn.x):
                di = d + i
                r = H(di.x if di.exact else 'huge', u, r, e)
        else:
            # many copies: after a few the accumulator is the universal fixed point
            for i in range(8):
                di = d + i
                r = H(di.x if di.exact else 'huge', u, r, e)
            if not (r == t):
                raise Fail(f'accumulator did not reach the fixed point: {r}')
        info['levels'].append(('entry', d, cn))
        if not cn.exact or not d.exact or (d + cn).ge(10 ** 6):
            info['huge_depth'] = info['huge_depth'] or (not cn.exact)
        lst.pop()
        zeros = zeros + c
        zeros_num = zeros_num + cn


# --------------------------------------------------------------------------------------------- fitting ----------
RANK_LB = {1: 6, 2: 600, 3: 3000, 4: 9000}
VAL_MOD = 2520
VAL_LB = {1: 6, 2: 600, 3: 3000, 4: 9000}
STEPS = [60, 120, 180, 420, 840, 2520]


def rep_base(val, m, lb):
    """smallest x >= lb with x = val (mod m)"""
    r = val.m(m)
    return lb + ((r - lb) % m)


def fit_values(xs, ys):
    """affine fit y = a x + b over rationals, exact on all points; None if impossible"""
    (x0, y0), (x1, y1) = (xs[0], ys[0]), (xs[1], ys[1])
    a = Fraction(y1 - y0, x1 - x0)
    b = y0 - a * x0
    for x, y in zip(xs, ys):
        if a * x + b != y:
            return None
    return a, b


class Stage:
    def __init__(self, machine, sym, params, ranks, budget, log, verbose=False):
        self.machine, self.sym, self.params, self.ranks = machine, sym, params, ranks
        self.budget, self.log, self.verbose = budget, log, verbose
        self.cache = {}

    def free_params(self):
        ps = set()
        for kind, p, c in self.sym:
            for x in ([p, c] if kind == 'D' else [k for _, k in p] + [c] if kind == 'J' else [c]):
                if isinstance(x, Aff):
                    ps |= set(x.co)
        return sorted(ps)

    def run_at(self, vals):
        key = tuple(sorted(vals.items()))
        if key in self.cache:
            return self.cache[key]
        ent = sym_inst(self.sym, vals)
        w = word_of(ent)
        out = run_hyb(self.machine, w, self.budget)
        if self.verbose:
            self.log(f'    run {vals}: {out["kind"]} @{out["step"]}  {out["raw"][:160]}')
        self.cache[key] = out
        return out

    def outcome_sig(self, o):
        if o['kind'] == 'J':
            return ('J', o['tail'], o.get('e', 2), shape_of(o['items']))
        if o['kind'] == 'H':
            return ('H',)
        return (o['kind'],)

    def run(self):
        ps = self.free_params()
        exact = {p: self.params[p].x for p in ps if self.params[p].exact and self.params[p].x <= 20000}
        sym_ps = [p for p in ps if p not in exact]
        if not sym_ps:
            o = self.run_at(exact)
            res = {'kind': o['kind'], 'fit': None, 'out': o, 'vals': exact, 'period': 0}
            if o['kind'] == 'J':
                res['sym'] = [(k, (Aff(p) if k == 'D' else tuple((pat, Aff(n)) for pat, n in p)), Aff(c))
                              for k, p, c in o['items']]
                res['tail'] = o['tail']
                res['e'] = o['e']
            elif o['kind'] == 'H':
                res['ones'] = Aff(o['ones']); res['steps'] = o['step']; res['halt_state'] = o['state'], o['read']
            return res
        tries = []
        for m in STEPS:
            step = {p: (3 * m if p.startswith('R') else m) for p in sym_ps}
            base = dict(exact)
            for p in sym_ps:
                base[p] = rep_base(self.params[p], step[p], RANK_LB[self.ranks.get(p, 1)])
            pts = [base]
            for p in sym_ps:
                for k in (1, 2, 3):
                    v = dict(base); v[p] = base[p] + k * step[p]; pts.append(v)
            if len(sym_ps) > 1:
                v = dict(base)
                for p in sym_ps:
                    v[p] = base[p] + step[p]
                pts.append(v)
            outs = []
            ok = True
            for v in pts:
                outs.append(self.run_at(v))
                if outs[0]['kind'] == 'T':
                    break
                if self.outcome_sig(outs[-1]) != self.outcome_sig(outs[0]):
                    ok = False
                    break
            tries.append((m, ''.join(self.outcome_sig(o)[0] for o in outs)))
            if not ok:
                continue
            kind = outs[0]['kind']
            if kind != 'J' and kind != 'H':
                return {'kind': kind, 'fit': None, 'out': outs[0], 'vals': pts[0], 'period': m}
            if kind == 'J':
                F = [fields_of(o['items']) for o in outs]
            else:
                F = [[o['ones']] for o in outs]
            fitted = []
            good = True
            for i in range(len(F[0])):
                aff = self.fit_multi(sym_ps, pts, [f[i] for f in F])
                if aff is None:
                    good = False
                    break
                fitted.append(aff)
            if not good:
                tries[-1] = (m, tries[-1][1] + ' nonaffine')
                continue
            res = {'kind': kind, 'period': m, 'vals': pts[0], 'out': outs[0]}
            if kind == 'J':
                res['sym'] = rebuild_sym(shape_of(outs[0]['items']), fitted)
                res['tail'] = outs[0]['tail']
                res['e'] = outs[0]['e']
            else:
                res['ones'] = fitted[0]
                st = self.fit_multi(sym_ps, pts, [o['step'] for o in outs])
                res['steps'] = st if st is not None else 'non-affine (' + ', '.join(str(o['step']) for o in outs) + ')'
                res['halt_state'] = outs[0]['state'], outs[0]['read']
            return res
        raise Fail(f'no consistent step: {tries}')

    def fit_multi(self, sym_ps, pts, ys):
        base = pts[0]
        co = {}
        idx = 1
        for p in sym_ps:
            xs = [base[p]] + [pts[idx + k][p] for k in range(3)]
            yy = [ys[0]] + [ys[idx + k] for k in range(3)]
            f = fit_values(xs, yy)
            if f is None:
                return None
            co[p] = f[0]
            idx += 3
        aff = Aff(0, co)
        aff.c = Fraction(ys[0]) - sum(v * base[k] for k, v in co.items())
        for v, y in zip(pts, ys):
            if aff.c + sum(cv * v[k] for k, cv in co.items()) != y:
                return None
        return aff


_RC = {}


def rule_check(machine, tail_entries, e, canon='B'):
    """literal check that R1, R2 and R3 hold in front of this tail: start K-moment [11, 7, 1, 4 | a=4 | r=e | tail]
    (prelocked), 30 transitions; True if R1, R2, R3 all occur and nothing breaks"""
    key = (machine, fmt_entries(tail_entries), e)
    if key in _RC:
        return _RC[key]
    base = [('D', 0, 2), ('D', 7, 1), ('D', 1, 1), ('D', 4, 1), ('D', 4, 1), ('D', e, 1)]
    w = word_of(base) + word_of(tail_entries)
    ntail = sum(c for _, _, c in tail_entries)
    fd, path = tempfile.mkstemp(suffix='.txt', dir=TMP)
    with os.fdopen(fd, 'w') as f:
        f.write(w)
    try:
        r = subprocess.run([HYB, machine, path, str(len(w)), canon, '20000000', '-p', str(ntail), '-e', str(e), '-x',
                            '-q', canon], capture_output=True, text=True, creationflags=LOW)
    finally:
        os.unlink(path)
    kinds = []
    ok = True
    for l in r.stdout.splitlines():
        if l.startswith('V '):
            kinds.append(l.split()[2])
            if len(kinds) >= 30:
                break
        elif l.startswith('U '):
            ok = False
            break
    res = ok and {'R1', 'R2', 'R3'} <= set(kinds)
    _RC[key] = (res, ''.join(k[1] for k in kinds[:30]))
    return _RC[key]


# --------------------------------------------------------------------------------------------- driver -----------
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


def follow(machine, n=11, stages=8, budget=400_000_000, log=print, verbose=False, template=None):
    t = tau()
    B = (t - 2).divexact(3)
    params = {'b': B}
    ranks = {'b': 1}
    sym = kword_sym(n, template)
    history = []
    cycles = 0
    for s in range(stages):
        st = Stage(machine, sym, params, ranks, budget, log, verbose)
        log(f'stage {s}: input {fmt_sym(sym)}')
        res = st.run()
        if res['kind'] == 'H':
            ones = res['ones']
            log(f'  HALT (period {res["period"]}): ones = {ones}, steps = {res["steps"]}, state {res["halt_state"]}')
            history.append(('H', ones))
            return {'result': 'HALT', 'stages': s + 1, 'full_cycles': cycles, 'ones': ones, 'history': history,
                    'params': params}
        if res['kind'] == 'T':
            log(f'  TIMEOUT (period {res.get("period")}) at {res["vals"]}: {res["out"]["raw"][:300]}')
            history.append(('T',))
            return {'result': 'UNCLEAR-T', 'stages': s + 1, 'full_cycles': cycles, 'history': history,
                    'params': params, 'last': res['out']['raw']}
        if res['kind'] != 'J':
            log(f'  outcome {res["kind"]}: {res["out"]["raw"][:300]}')
            return {'result': 'UNCLEAR-' + res['kind'], 'stages': s + 1, 'full_cycles': cycles, 'history': history,
                    'params': params}
        log(f'  champion phase (period {res["period"]}): {fmt_sym(res["sym"])}  tail={res["tail"]} e={res.get("e", 2)}')
        _, tail_c = flatten_right(res['out']['items'], res['tail'])
        rc_ok, rc_seq = rule_check(machine, merge([(k, p, 1) for k, p, _ in tail_c]), res.get('e', 2), CANON)
        log(f'  rule check R1-R3 in front of this tail: {"PASS" if rc_ok else "FAIL"} ({rc_seq})')
        if not rc_ok:
            history.append(('RULES-FAIL',))
            return {'result': 'UNCLEAR-RULES', 'stages': s + 1, 'full_cycles': cycles, 'history': history,
                    'params': params}
        ev_sym, params2, info = jump(res['sym'], res['tail'], params, log, res.get('e', 2))
        for p in params2:
            if p not in ranks:
                ranks[p] = min(4, max(ranks.values()) + 1)
        params = params2
        big = info.get('huge_depth')
        if big:
            cycles += 1
        log(f'  jump -> event {info["event"]}, huge-length list cleared: {big}; new params '
            f'{ {k: str(v) for k, v in params.items() if k not in st.params} }')
        log(f'  event config: {fmt_sym(ev_sym)}')
        history.append(('J', info['event'], big))
        sym = ev_sym
    return {'result': 'MAXSTAGES', 'stages': stages, 'full_cycles': cycles, 'history': history, 'params': params}


def fmt_sym(sym):
    out = []
    for kind, p, c in sym:
        if kind == 'D':
            s = f'D({p})'
        elif kind == 'J':
            s = '<' + '.'.join(f'{pat}^{k}' for pat, k in p) + '>'
        else:
            s = f'[{p}]'
        cs = str(c)
        out.append(s if cs == '1' else f'{s}^{{{cs}}}')
    return ' '.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('--n', type=int, default=11)
    ap.add_argument('--template')
    ap.add_argument('--stages', type=int, default=8)
    ap.add_argument('--budget', type=int, default=400_000_000)
    ap.add_argument('--log')
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None

    def log(s):
        print(s, flush=True)
        if lf:
            lf.write(s + '\n'); lf.flush()

    log(f'machine {a.machine}')
    try:
        global CANON
        if a.template:
            CANON = a.template.split(',')[1]
        r = follow(a.machine, a.n, a.stages, a.budget, log, a.verbose, a.template)
        log(f'RESULT {r["result"]} stages={r["stages"]} full_cycles={r["full_cycles"]} '
            f'history={r["history"]}' + (f' ones={r["ones"]}' if 'ones' in r else ''))
    except Fail as e:
        log(f'RESULT FAIL {e}')


if __name__ == '__main__':
    main()
