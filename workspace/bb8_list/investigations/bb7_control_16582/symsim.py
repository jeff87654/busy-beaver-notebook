"""Small symbolic Turing-machine prover (Ligocki-style, written for this investigation).

Tape = left token list | head cell (state, bit) | right token list.
Tokens: ('L', bits) literal string, or ('R', block, e) = block repeated e times,
where e is a LinExpr (integer-linear in named parameters, each parameter >= a
declared lower bound).

Soundness principles
 * Literal cells are simulated one TM step at a time.
 * A run block^e is crossed in one move only if the TM, entering ONE copy of
   `block` in state q from one side, leaves it on the opposite side in the same
   state q without ever leaving through the entry side (checked by isolated
   simulation of that single block).  Then by induction on e the whole run is
   crossed and becomes newblock^e.  Valid for every e >= 0.
 * Otherwise one copy is peeled off (needs e >= 1, which must be provable from
   the parameter lower bounds; if not provable the proof attempt aborts).
 * Lemmas (previously proven rules) are applied by exact pattern matching on
   the tokens adjacent to the head.  Iterated lemmas are proven as a one-step
   Diff rule with the counter >= 1, and applied as a whole by induction.
 * Normalisation only uses string identities (merge adjacent literals, absorb
   literal copies of a block into an adjacent run, rotate a run using a
   neighbouring literal: a(ba)^e = (ab)^e a).
"""
from __future__ import annotations
import itertools

TM_STR = "1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG"
STATES = "ABCDEFG"


def parse_tm(s):
    t = []
    for ch in s.split('_'):
        row = []
        for i in (0, 3):
            e = ch[i:i + 3]
            if e == '---' or e[2] == 'Z':
                row.append(None)
            else:
                row.append((int(e[0]), 1 if e[1] == 'R' else -1, STATES.index(e[2])))
        t.append(row)
    return t


TM = parse_tm(TM_STR)


class Halt(Exception):
    pass


class ProofFail(Exception):
    pass


# ---------------------------------------------------------------- LinExpr
class E:
    __slots__ = ('c', 'v')

    def __init__(self, c=0, v=None):
        self.c = c
        self.v = {k: x for k, x in (v or {}).items() if x != 0}

    @staticmethod
    def var(name):
        return E(0, {name: 1})

    def __add__(self, o):
        o = o if isinstance(o, E) else E(o)
        v = dict(self.v)
        for k, x in o.v.items():
            v[k] = v.get(k, 0) + x
        return E(self.c + o.c, v)

    __radd__ = __add__

    def __neg__(self):
        return E(-self.c, {k: -x for k, x in self.v.items()})

    def __sub__(self, o):
        o = o if isinstance(o, E) else E(o)
        return self + (-o)

    def __mul__(self, k):
        if isinstance(k, E):
            if not k.v:
                k = k.c
            elif not self.v:
                return k * self.c
            else:
                raise ProofFail('nonlinear product')
        return E(self.c * k, {a: x * k for a, x in self.v.items()})

    __rmul__ = __mul__

    def __eq__(self, o):
        o = o if isinstance(o, E) else E(o)
        return self.c == o.c and self.v == o.v

    def __hash__(self):
        return hash((self.c, tuple(sorted(self.v.items()))))

    def is_const(self):
        return not self.v

    def subst(self, env):
        r = E(self.c)
        for k, x in self.v.items():
            r = r + (env[k] if k in env else E.var(k)) * x
        return r

    def minval(self, lb):
        """Provable lower bound (None if unbounded below)."""
        m = self.c
        for k, x in self.v.items():
            if x < 0:
                return None
            m += x * lb.get(k, 0)
        return m

    def __repr__(self):
        parts = []
        for k in sorted(self.v):
            x = self.v[k]
            parts.append(k if x == 1 else f"{x}{k}")
        if self.c or not parts:
            parts.append(str(self.c))
        return '+'.join(parts).replace('+-', '-')


def as_e(x):
    return x if isinstance(x, E) else E(x)


# ---------------------------------------------------------------- blocks
_cross_cache = {}


def cross(block, state, direction):
    """Enter one copy of block in `state` moving `direction` (+1: enter at
    left end).  Return (newblock, steps) if it exits the opposite side in the
    same state, else None.  Raises Halt if the TM halts inside."""
    key = (block, state, direction)
    if key in _cross_cache:
        return _cross_cache[key]
    cells = [int(b) for b in block]
    pos = 0 if direction > 0 else len(cells) - 1
    st = state
    steps = 0
    res = None
    while steps < 10000:
        tr = TM[st][cells[pos]]
        if tr is None:
            res = None  # would halt inside; treat as no crossing (peel instead)
            break
        w, d, ns = tr
        cells[pos] = w
        pos += d
        st = ns
        steps += 1
        if pos < 0 or pos >= len(cells):
            exit_dir = 1 if pos >= len(cells) else -1
            if exit_dir == direction and st == state:
                res = (''.join(map(str, cells)), steps)
            break
    _cross_cache[key] = res
    return res


def rotations(u):
    return [u[i:] + u[:i] for i in range(len(u))]


def canon_block(u):
    return max(rotations(u))


COMPRESS_BLOCKS = ('100', '110')
COMPRESS_MIN = 3


def compress_literal(bits):
    """Split a literal into literal / run tokens (pure string identity)."""
    toks = []
    lit = ''
    i = 0
    while i < len(bits):
        best = None
        for u in COMPRESS_BLOCKS:
            k = 0
            while bits.startswith(u, i + len(u) * k):
                k += 1
            if k >= COMPRESS_MIN and (best is None or k * len(u) > best[1] * len(best[0])):
                best = (u, k)
        if best:
            if lit:
                toks.append(('L', lit))
                lit = ''
            toks.append(('R', best[0], E(best[1])))
            i += best[1] * len(best[0])
        else:
            lit += bits[i]
            i += 1
    if lit:
        toks.append(('L', lit))
    return toks


# ---------------------------------------------------------------- config
class Config:
    def __init__(self, left, state, cell, right, lb=None, walled=(False, False)):
        if isinstance(walled, bool):
            walled = (walled, walled)
        self.walled = tuple(walled)  # (left, right): True = tape beyond tokens NOT known blank
        self.left = list(left)
        self.right = list(right)
        self.state = state
        self.cell = cell
        self.lb = dict(lb or {})
        self.steps = 0  # concrete steps (only meaningful if all exps concrete)
        self.sym_steps = False

    def copy(self):
        c = Config(self.left, self.state, self.cell, self.right, self.lb, self.walled)
        c.steps = self.steps
        c.sym_steps = self.sym_steps
        return c

    # ---- normalisation of one side (tokens in left-to-right order)
    @staticmethod
    def norm_side(toks, lb, side, walled=False):
        # expand runs with constant exponent <= 0 / drop empties; merge literals
        out = []
        for t in toks:
            if t[0] == 'L':
                if not t[1]:
                    continue
                if out and out[-1][0] == 'L':
                    out[-1] = ('L', out[-1][1] + t[1])
                else:
                    out.append(t)
            else:
                e = as_e(t[2])
                if e.is_const() and e.c == 0:
                    continue
                if e.is_const() and e.c < 0:
                    raise ProofFail('negative run length')
                if out and out[-1][0] == 'R' and out[-1][1] == t[1]:
                    out[-1] = ('R', t[1], out[-1][2] + e)
                else:
                    out.append(('R', t[1], e))
        # compress long literal repeats of the machine's blocks into runs
        comp = []
        for t in out:
            if t[0] == 'L' and len(t[1]) >= 3 * COMPRESS_MIN:
                comp.extend(compress_literal(t[1]))
            else:
                comp.append(t)
        out = comp
        changed = True
        while changed:
            changed = False
            for i, t in enumerate(out):
                if t[0] != 'R':
                    continue
                u = t[1]
                # absorb copies from literal on the left / right
                if i > 0 and out[i - 1][0] == 'L' and out[i - 1][1].endswith(u):
                    out[i - 1] = ('L', out[i - 1][1][:-len(u)])
                    out[i] = ('R', u, t[2] + 1)
                    changed = True
                    break
                if i + 1 < len(out) and out[i + 1][0] == 'L' and out[i + 1][1].startswith(u):
                    out[i + 1] = ('L', out[i + 1][1][len(u):])
                    out[i] = ('R', u, t[2] + 1)
                    changed = True
                    break
                # rotate toward canonical block
                cu = canon_block(u)
                if u != cu:
                    # u = b a, cu = a b.  Need literal ending with a on the left
                    for k in range(1, len(u)):
                        b, a = u[:k], u[k:]
                        if a + b != cu:
                            continue
                        if i > 0 and out[i - 1][0] == 'L' and out[i - 1][1].endswith(a):
                            out[i - 1] = ('L', out[i - 1][1][:-len(a)])
                            out[i] = ('R', cu, t[2])
                            out.insert(i + 1, ('L', a))
                            changed = True
                        elif i + 1 < len(out) and out[i + 1][0] == 'L' and out[i + 1][1].startswith(b):
                            out[i + 1] = ('L', out[i + 1][1][len(b):])
                            out[i] = ('R', cu, t[2])
                            out.insert(i, ('L', b))
                            changed = True
                        break
                    if changed:
                        break
            if changed:
                # re-merge
                out = Config.norm_side(out, lb, side, walled)
                return out
        # strip blank padding at the outer end (only when the tape beyond is blank)
        if walled:
            return [t for t in out if not (t[0] == 'L' and not t[1])]
        if side == 'L':
            while out and out[0][0] == 'L' and set(out[0][1]) <= {'0'}:
                out.pop(0)
            if out and out[0][0] == 'L':
                out[0] = ('L', out[0][1].lstrip('0'))
        else:
            while out and out[-1][0] == 'L' and set(out[-1][1]) <= {'0'}:
                out.pop()
            if out and out[-1][0] == 'L':
                out[-1] = ('L', out[-1][1].rstrip('0'))
        return [t for t in out if not (t[0] == 'L' and not t[1])]

    def normalize(self):
        self.left = Config.norm_side(self.left, self.lb, 'L', self.walled[0])
        self.right = Config.norm_side(self.right, self.lb, 'R', self.walled[1])

    def ge(self, e, k):
        m = as_e(e).minval(self.lb)
        return m is not None and m >= k

    # ---- pop the cell adjacent to the head on one side
    def _pop_cell(self, side, state, direction):
        """Head moves onto the next cell of `side` ('R' list when moving right).
        May cross whole runs.  Returns bit under the head."""
        toks = self.right if side == 'R' else self.left
        while True:
            if not toks:
                if self.walled[0 if side == 'L' else 1]:
                    raise ProofFail('head left the pattern (wall on side %s)' % side)
                return 0
            t = toks[0] if side == 'R' else toks[-1]
            if t[0] == 'L':
                s = t[1]
                if side == 'R':
                    bit = int(s[0])
                    rest = s[1:]
                    if rest:
                        toks[0] = ('L', rest)
                    else:
                        toks.pop(0)
                else:
                    bit = int(s[-1])
                    rest = s[:-1]
                    if rest:
                        toks[-1] = ('L', rest)
                    else:
                        toks.pop()
                return bit
            # a run
            u, e = t[1], as_e(t[2])
            cr = cross(u, state, direction)
            if cr is not None:
                nu, st = cr
                if side == 'R':
                    toks.pop(0)
                    self.left.append(('R', nu, e))
                else:
                    toks.pop()
                    self.right.insert(0, ('R', nu, e))
                if e.is_const():
                    self.steps += st * e.c
                else:
                    self.sym_steps = True
                continue
            # peel one copy
            if not self.ge(e, 1):
                raise ProofFail(f'cannot peel run {u}^{e}: not provably >= 1')
            if side == 'R':
                toks[0] = ('R', u, e - 1)
                toks.insert(0, ('L', u))
            else:
                toks[-1] = ('R', u, e - 1)
                toks.append(('L', u))

    def try_head_cross(self):
        """Head (state q, bit b) about to move toward a run u^e that is separated
        from the head by a literal s such that the cells between the run and the
        head, together with the head cell, form a prefix (left side) / suffix
        (right side) of u.  Re-read the tape as a run of a rotated block that
        ends (starts) at the head cell and cross it if a single block is crossed
        in state q.  Pure induction on e; returns True if crossed."""
        tr = TM[self.state][self.cell]
        if tr is None:
            return False
        d = tr[1]
        q = self.state
        b = str(self.cell)
        if d < 0:
            toks = self.left
            if not toks:
                return False
            if toks[-1][0] == 'L':
                if len(toks) < 2 or toks[-2][0] != 'R':
                    return False
                lit, run = toks[-1][1], toks[-2]
            else:
                lit, run = '', toks[-1]
            u, e = run[1], as_e(run[2])
            w = lit + b
            m = len(w)
            if m > len(u) or u[:m] != w:
                return False
            u2 = u[m:] + u[:m]
            cr = cross(u2, q, -1)
            if cr is None:
                return False
            nu, st = cr
            # tape: ... u^e w  ==  ... u[:m] (u2)^e ; head on last cell of the run
            if lit:
                toks.pop()
            toks.pop()
            self.right.insert(0, ('R', nu, e))
            self.left.append(('L', u[:m]))
            if e.is_const():
                self.steps += st * e.c
            else:
                self.sym_steps = True
            # head now moves onto the cell left of the run, in state q
            self.state = q
            self.cell = self._pop_cell('L', q, -1)
            return True
        else:
            toks = self.right
            if not toks:
                return False
            if toks[0][0] == 'L':
                if len(toks) < 2 or toks[1][0] != 'R':
                    return False
                lit, run = toks[0][1], toks[1]
            else:
                lit, run = '', toks[0]
            u, e = run[1], as_e(run[2])
            w = b + lit
            m = len(w)
            if m > len(u) or u[len(u) - m:] != w:
                return False
            u2 = u[len(u) - m:] + u[:len(u) - m]
            cr = cross(u2, q, +1)
            if cr is None:
                return False
            nu, st = cr
            if lit:
                toks.pop(0)
            toks.pop(0)
            self.left.append(('R', nu, e))
            self.right.insert(0, ('L', u[len(u) - m:]))
            if e.is_const():
                self.steps += st * e.c
            else:
                self.sym_steps = True
            self.state = q
            self.cell = self._pop_cell('R', q, +1)
            return True

    def step(self):
        if self.try_head_cross():
            return
        tr = TM[self.state][self.cell]
        if tr is None:
            raise Halt(self)
        w, d, ns = tr
        self.steps += 1
        if d > 0:
            self.left.append(('L', str(w)))
            self.state = ns
            self.cell = self._pop_cell('R', ns, +1)
        else:
            self.right.insert(0, ('L', str(w)))
            self.state = ns
            self.cell = self._pop_cell('L', ns, -1)

    def __str__(self):
        def f(t):
            if t[0] == 'L':
                return t[1]
            return f"({t[1]})^{{{t[2]}}}" if not t[2].is_const() else f"({t[1]})^{t[2]}"
        return ' '.join(map(f, self.left)) + f" [{STATES[self.state]}{self.cell}] " + ' '.join(map(f, self.right))

    def key(self):
        self.normalize()
        return (tuple(self.left), self.state, self.cell, tuple(self.right))


# ---------------------------------------------------------------- patterns
def parse_side(s, env_vars):
    """Parse a token string like "00 (100)^{a} 1010 (110)^{b+1}" into tokens.
    Exponent syntax: {expr} with expr like a, a+1, 2a+3 (vars are single words)."""
    toks = []
    for part in s.split():
        if part.startswith('('):
            blk, ex = part[1:].split(')^')
            ex = ex.strip('{}')
            toks.append(('R', blk, parse_expr(ex)))
        else:
            toks.append(('L', part))
    return toks


def parse_expr(s):
    s = s.replace('-', '+-')
    e = E(0)
    for term in s.split('+'):
        term = term.strip()
        if not term:
            continue
        neg = term.startswith('-')
        term = term.lstrip('-')
        i = 0
        while i < len(term) and term[i].isdigit():
            i += 1
        coef = int(term[:i]) if i else 1
        name = term[i:]
        if name:
            x = E.var(name) * coef
        else:
            x = E(coef)
        e = e - x if neg else e + x
    return e


def make_config(s, lb=None, walled=(False, False)):
    """Config from 'LEFT [Xb] RIGHT'."""
    l, rest = s.split('[', 1)
    hs, r = rest.split(']', 1)
    c = Config(parse_side(l, None), STATES.index(hs[0]), int(hs[1]), parse_side(r, None), lb, walled)
    c.normalize()
    return c


def instantiate(s, env, walled=(True, True)):
    c = make_config(s, walled=walled)
    c.left = [(t[0], t[1], t[2].subst(env)) if t[0] == 'R' else t for t in c.left]
    c.right = [(t[0], t[1], t[2].subst(env)) if t[0] == 'R' else t for t in c.right]
    c.normalize()
    return c


def same(c1, c2):
    return c1.key() == c2.key()


# ---------------------------------------------------------------- lemmas
class Lemma:
    """Pattern LHS -> RHS.  Pattern strings use variables; `lb` gives the
    variables' lower bounds under which the lemma was proven."""

    def __init__(self, name, lhs, rhs, lb, iterate_var=None, walled=(True, True)):
        self.name = name
        self.walled = walled
        self.lhs = make_config(lhs, walled=walled)
        self.rhs_str = rhs
        self.lb = lb
        self.iterate_var = iterate_var
        self.lhs_str = lhs

    def match(self, c):
        """Try to match self.lhs against the head neighbourhood of c.
        Returns (env, nleft_consumed_tokens, nright_consumed) or None."""
        if c.state != self.lhs.state or c.cell != self.lhs.cell:
            return None
        env = {}
        L = [list(t) for t in c.left]
        R = [list(t) for t in c.right]

        def bind(pe, ce):
            # pe = var + const (or const); ce = config expression
            pe = as_e(pe)
            if pe.is_const():
                return pe == ce
            if len(pe.v) != 1 or list(pe.v.values())[0] != 1:
                return False
            var = list(pe.v)[0]
            val = ce - pe.c
            if var in env:
                return env[var] == val
            m = val.minval(c.lb)
            if m is None or m < self.lb.get(var, 0):
                return False
            env[var] = val
            return True

        # left side, from the head outward
        li = len(L) - 1
        for pt in reversed(self.lhs.left):
            if pt[0] == 'L':
                need = pt[1]
                while need:
                    if li < 0:
                        if set(need) <= {'0'} and not c.walled[0]:
                            need = ''
                            break
                        return None
                    ct = L[li]
                    if ct[0] != 'L':
                        return None
                    s = ct[1]
                    k = min(len(s), len(need))
                    if s[len(s) - k:] != need[len(need) - k:]:
                        return None
                    need = need[:len(need) - k]
                    s = s[:len(s) - k]
                    if s:
                        L[li] = ['L', s]
                    else:
                        li -= 1
            else:
                if li < 0:
                    if not bind(pt[2], E(0)):
                        return None
                    continue
                ct = L[li]
                if ct[0] != 'R' or ct[1] != pt[1]:
                    # allow zero-length run
                    if bind(pt[2], E(0)):
                        continue
                    return None
                if not bind(pt[2], as_e(ct[2])):
                    return None
                li -= 1
        ri = 0
        for pt in self.lhs.right:
            if pt[0] == 'L':
                need = pt[1]
                while need:
                    if ri >= len(R):
                        if set(need) <= {'0'} and not c.walled[1]:
                            need = ''
                            break
                        return None
                    ct = R[ri]
                    if ct[0] != 'L':
                        return None
                    s = ct[1]
                    k = min(len(s), len(need))
                    if s[:k] != need[:k]:
                        return None
                    need = need[k:]
                    s = s[k:]
                    if s:
                        R[ri] = ['L', s]
                    else:
                        ri += 1
            else:
                if ri >= len(R):
                    if not bind(pt[2], E(0)):
                        return None
                    continue
                ct = R[ri]
                if ct[0] != 'R' or ct[1] != pt[1]:
                    if bind(pt[2], E(0)):
                        continue
                    return None
                if not bind(pt[2], as_e(ct[2])):
                    return None
                ri += 1
        restL = [tuple(t) for t in L[:li + 1]]
        restR = [tuple(t) for t in R[ri:]]
        # a lemma proven with blank tape beyond a side needs blank tape there
        if not self.walled[0]:
            if c.walled[0] or any(not (t[0] == 'L' and set(t[1]) <= {'0'}) for t in restL):
                return None
        if not self.walled[1]:
            if c.walled[1] or any(not (t[0] == 'L' and set(t[1]) <= {'0'}) for t in restR):
                return None
        return env, restL, restR

    def apply(self, c):
        m = self.match(c)
        if m is None:
            return False
        env, restL, restR = m
        rhs = instantiate(self.rhs_str, env, walled=self.walled)
        c.left = restL + rhs.left
        c.right = rhs.right + restR
        c.state = rhs.state
        c.cell = rhs.cell
        c.sym_steps = True
        c.normalize()
        self.count = getattr(self, 'count', 0) + 1
        c.lemma_log = getattr(c, 'lemma_log', []) + [self.name]
        return True


def run(c, lemmas=(), max_steps=100000, stop=None, trace=False):
    """Run until stop(c) is true (checked after every step / lemma).  Returns
    the number of loop iterations."""
    for it in range(max_steps):
        applied = False
        for lm in lemmas:
            if lm.apply(c):
                applied = True
                if trace:
                    print('  lemma', lm.name, ':', c)
                break
        if not applied:
            c.step()
            c.normalize()
            if trace:
                print(' ', c)
        if stop is not None and stop(c):
            return it + 1
    raise ProofFail('max_steps exceeded')


def prove(name, lhs, rhs, lb, lemmas=(), iterate_var=None, max_steps=100000, trace=False, walled=(True, True)):
    """Prove LHS ->* RHS symbolically (for the variables >= lb).  If
    iterate_var is given, the proven statement is the one-step Diff rule with
    that variable decremented, i.e. LHS(v) -> RHS where RHS is written with v-1;
    the returned lemma then applies the iterated closed form, which must be
    supplied by the caller as a separate Lemma.  Returns a Lemma."""
    c = make_config(lhs, lb, walled)
    target = make_config(rhs, lb, walled)
    tk = target.key()
    def stop(x):
        return x.key() == tk
    try:
        n = run(c, lemmas, max_steps, stop, trace)
    except ProofFail as ex:
        raise ProofFail(f'{name}: {ex}; last config {c}')
    return Lemma(name, lhs, rhs, lb, iterate_var, walled), n
