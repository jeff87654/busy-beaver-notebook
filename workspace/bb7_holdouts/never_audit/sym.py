"""sym.py (never_audit): drive symsim.exe (sound symbolic macro simulator, reused from bb8_resid, patched with --stopq)
from v-list K-configs and parse its tapes back into v-lists with linear-form entries.

v-coding: tape cells oriented so that the K-event head side is the RIGHT end; the v-list is the list of 1-run lengths
separated by single 0s (00 = a zero entry).  A K-config = (state q, v-list, t) where t = number of 0 cells between the
last 1-run and the head (the head reads a blank cell just past the visited span).
Machines whose K-event is on the LEFT are mirrored (swap L/R) so everything is right-handed.
"""
import subprocess, os, re
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
SYMSIM = os.path.join(HERE, 'src', 'symsim.exe')
LIT = os.path.join(HERE, 'src', 'lit.exe')

def mirror(m):
    out = []
    for g in m.split('_'):
        h = ''
        for i in range(0, 6, 3):
            t = g[i:i+3]
            if t[2] != '-': t = t[0] + ('L' if t[1] == 'R' else 'R') + t[2]
            h += t
        out.append(h)
    return '_'.join(out)

class Lin:
    """linear form over symbols with Fraction coefficients; key '' = constant"""
    def __init__(self, d=None):
        self.d = {k: Fr(v) for k, v in (d or {}).items() if v != 0}
    @staticmethod
    def c(v): return Lin({'': v})
    def __add__(s, o):
        o = o if isinstance(o, Lin) else Lin.c(o); d = dict(s.d)
        for k, v in o.d.items(): d[k] = d.get(k, 0) + v
        return Lin(d)
    __radd__ = __add__
    def __neg__(s): return Lin({k: -v for k, v in s.d.items()})
    def __sub__(s, o): return s + (-(o if isinstance(o, Lin) else Lin.c(o)))
    def __rsub__(s, o): return (-s) + o
    def __mul__(s, o):
        if isinstance(o, Lin):
            if s.isconst(): return o * s.const()
            assert o.isconst(); o = o.const()
        return Lin({k: v * o for k, v in s.d.items()})
    __rmul__ = __mul__
    def __truediv__(s, o):
        if isinstance(o, Lin): assert o.isconst(); o = o.const()
        return Lin({k: v / Fr(o) for k, v in s.d.items()})
    def isconst(s): return all(k == '' for k in s.d)
    def const(s): return s.d.get('', Fr(0))
    def __eq__(s, o):
        o = o if isinstance(o, Lin) else Lin.c(o); return (s - o).d == {}
    def __hash__(s): return hash(tuple(sorted(s.d.items())))
    def __repr__(s):
        if s.isconst():
            c = s.const(); return str(c.numerator) if c.denominator == 1 else str(c)
        parts = []
        for k in sorted(s.d, key=lambda k: (k == '', k)):
            v = s.d[k]
            vs = (str(v.numerator) if v.denominator == 1 else '(%s)' % v)
            parts.append(vs if k == '' else (k if v == 1 else ('-' + k if v == -1 else vs + '*' + k)))
        return '+'.join(parts).replace('+-', '-')
    def ev(s, env):
        r = Fr(0)
        for k, v in s.d.items(): r += v * (1 if k == '' else env[k])
        return r

def parse_expr(e):
    e = e.strip()
    if e.startswith('{'): e = e[1:-1]
    e2 = re.sub(r'(?<![X\w])(\d+)', lambda mo: 'Lin.c(%s)' % mo.group(1), e)
    e2 = re.sub(r'X(\d+)', lambda mo: 'V("X%s")' % mo.group(1), e2)
    return eval(e2, {'Lin': Lin, 'V': lambda k: Lin({k: 1})})

def parse_tape(s):
    """symsim show() text -> (items, state) where items = list of (word, count Lin) left to right, head token 'Q>'.
    Only the right-facing representation 'Q>' is expected at our stops."""
    toks = s.split(); items = []; q = None; hidx = None
    for t in toks:
        if len(t) == 2 and t[1] == '>' and t[0].isalpha(): q = t[0]; hidx = len(items); continue
        if len(t) == 2 and t[0] == '<' and t[1].isalpha(): q = t[1]; hidx = len(items); continue
        if '^' in t:
            w, c = t.split('^', 1); items.append((w, parse_expr(c)))
        else: items.append((t, Lin.c(1)))
    return items, q, hidx

def items_to_v(items):
    """word-run items (left part of the tape, left to right) -> v-list entries (Lin) with blocks.
    returns (entries, trailing_zeros); entries: Lin or ('blk', [Lin...], countLin)."""
    ent = []; cur = Lin.c(0); started = False; zeros = 0
    def feed_bits(bits):
        nonlocal cur, started, zeros
        for b in bits:
            if b == '1':
                if started and zeros >= 1:
                    ent.append(cur); ent.extend([Lin.c(0)] * (zeros - 1)); cur = Lin.c(0)
                started = True; zeros = 0; cur = cur + 1
            else:
                if started: zeros += 1
    for w, n in items:
        if n.isconst():
            k = int(n.const())
            if k > 2000 and '0' in w and '1' in w:
                n = Lin.c(k)  # treat as block below
            else:
                feed_bits(w * k); continue
        if set(w) == {'1'}:
            if started and zeros >= 1:
                ent.append(cur); ent.extend([Lin.c(0)] * (zeros - 1)); cur = Lin.c(0)
            started = True; zeros = 0; cur = cur + n * len(w); continue
        if set(w) == {'0'}:
            if not started: continue
            # symbolic zero run: zeros count symbolic -> zero entries; represent as block of zeros
            if started:
                ent.append(cur); cur = Lin.c(0)
                ent.append(('blk', [Lin.c(0)], n * len(w) - 1 - (zeros)))  # n*len zeros -> n*len-1 zero entries
                zeros = 1; started = True
                # mark: the pending run after these zeros starts fresh; we set zeros=1 so next 1 emits cur(=0)?
                cur = None
            continue
        # mixed word repeated n times: first copy concretely, middle copies as block, record
        feed_bits(w); feed_bits(w)          # copies 1 and 2 literally (n >= 2 assumed for symbolic n)
        before = len(ent)
        st = (cur, zeros, started)
        feed_bits(w)                        # copy 3: steady-state emissions
        mid = ent[before:]
        del ent[before:]
        cur, zeros, started = st
        ent.append(('blk', mid, n - 2))
        # after the block the carry state equals the state after one copy (determined by w)
        cur, zeros, started = _carry_after(w, cur, zeros, started)
    if started and cur is not None: ent.append(cur)
    return clean(ent), zeros

def _carry_after(w, cur, zeros, started):
    # state after feeding w once from a state reached after >=1 copy of w (same as current carry by construction)
    return cur, zeros, started

def clean(ent):
    out = []
    for e in ent:
        if e is None: continue
        if isinstance(e, tuple) and e[0] == 'blk':
            if e[2] == 0: continue
            if e[2].isconst() and e[2].const() <= 50:
                out.extend(list(e[1]) * int(e[2].const())); continue
        out.append(e)
    return out

def vshow(v, maxn=60):
    s = []; i = 0
    while i < len(v):
        e = v[i]
        if isinstance(e, tuple): s.append('[%s]^{%s}' % (','.join(map(str, e[1])), e[2])); i += 1; continue
        j = i
        while j < len(v) and not isinstance(v[j], tuple) and v[j] == e: j += 1
        s.append(str(e) + ('*%d' % (j - i) if j - i > 1 else '')); i = j
    if len(s) > maxn: s = s[:maxn // 3] + ['...'] + s[-2 * maxn // 3:]
    return ' '.join(s)

def v_to_tokens(v, t, q, syms=None):
    """v-list entries (int, or str like 'H5' for a symbol class, or ('rep',d,n)) -> symsim tokens; head after t zeros"""
    toks = []
    for i, e in enumerate(v):
        if i > 0: toks.append('0')
        if isinstance(e, str): toks.append('1^' + e)
        elif isinstance(e, tuple):  # ('rep', d, n): n copies of digit d (d>=1)
            _, d, n = e
            toks.pop() if toks and toks[-1] == '0' and i > 0 else None
            toks.append(('0' + '1' * d) + '^' + str(n)) if i > 0 else toks.append(('1' * d + '0') + '^' + str(n))
        elif e > 0: toks.append('1^%d' % e)
        else: pass
    s = ' '.join(toks)
    if t > 0: s += ' 0^%d' % t
    return s + ' ' + q + '>'

def run_sym(m, q, tape, mg=720, budget=200000, stopn=1, stopall=True, prove=True, hlb=None, tlimit=60, extra=()):
    args = [SYMSIM, 'run', '--noch', '--nokt', '--mg', str(mg), '--budget', str(budget), '--tapeall', '200000',
            '--stopq', q, '--stopn', str(stopn), '--tlimit', str(tlimit)]
    if stopall: args.append('--stopall')
    if not prove: args.append('--noprove')
    if hlb: args += ['--hlb', str(hlb)]
    args += list(extra)
    inp = '%s %s %s\n' % (m, q, tape)
    p = subprocess.run(args, input=inp, capture_output=True, text=True, timeout=tlimit * 3 + 30)
    stops = []; verdict = None; final = None; syms = ''
    for l in p.stdout.splitlines():
        if l.startswith('STOP '):
            a, b = l.split(' TAPE ', 1); tp, sd = b.rsplit(' |', 1) if ' |' in b else (b, '')
            stops.append((a, tp.strip(), sd))
        elif l.startswith('R '): verdict = l.split()[3]; rline = l
        elif l.startswith('TAPE '): final = l[5:]
        elif l.startswith('TAPESYMS'): syms = l
    return verdict, stops, final, p.stdout

def stop_v(tp):
    items, q, h = parse_tape(tp)
    left = items[:h]; right = items[h:]
    v, z = items_to_v(left)
    rb = all(set(w) <= {'0'} for w, n in right)
    return q, v, z, rb

def ksteps(m, q, v, z, isK, n=1, maxstops=400, mg=720, hlb=1000, budget=400000, tlimit=60, prove=True):
    """run symsim from K-config (v,z) until n further K-moments (isK(v,z) true) or halt; returns (verdict, [v...], raw)"""
    tp = v_to_tokens(v, z, q)
    verdict, st, fin, out = run_sym(m, q, tp, stopn=maxstops, mg=mg, hlb=hlb, budget=budget, tlimit=tlimit, prove=prove)
    ks = []
    for a, t, sd in st:
        try: qq, vv, zz, rb = stop_v(t)
        except Exception as ex: ks.append(('PARSEFAIL', t[:200])); continue
        if isK(vv, zz):
            ks.append((vv, zz, sd))
            if len(ks) >= n: return 'K', ks, out
    return verdict, ks, out
