"""Accelerated follower (gh0LH verifier) for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH.

Configuration (G-frame K-moment: word + 10101010, head on the blank right, state G) as a list of items:
  ['R', v, c]   run of c copies of token D(v) (v int >= 0 or Huge) or a gap 0^k (v = -k, c = 1)
  ['G', pat, c] c copies of the block pat (tuple of (v, small int) runs); c int or Huge
The last two items are ['R', a, 1], ['R', r, 1].
Abstract champion rules on the tokens right of the last gap (literal checks rulecheck.py, rulecheck3.py):
  R1 [a+3|r]->[a|2r+6];  R2 [X+3|1|r]->[X|2r+7|0];  R3 [Y+3,1^k|1|r]->[Y,2r+7,1^(k-1)|1|0].
A borrow from a huge token or across a huge run (r = 0 mod 3) is shortcut: the first non-digit token (from the right)
-> its residue mod 3, everything right of it -> D1, accumulator -> U.
Events run literally (ksim2.exe = block-2 chain simulator, identical to kst3.exe on all tests) on a right window of the
configuration (locality checked: the head never enters the window's first item), with representatives
CRT(s2 mod 8, odd mod 315) + 2520(1+k) and one +360 run per huge symbol; outputs are read off as rational-affine
functions of the huge symbols.  Affine periods (identical shapes, counts changing by constants over 2 periods) are
skipped N periods at a time (N may be huge).  Everything unexpected fails loudly.
  python ghf7.py B0 [--log FILE] [-v] [--maxj N]"""
import sys, subprocess, argparse
from fractions import Fraction
from math import gcd
from hv2 import Huge, U, mk, mod, lin, r1, isH, Unknown, MO, m2
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
BUD = 300; SHIFT = 360; MLIT = 2520
DENOMS = (1, 2, 3, 4, 6, 8, 12, 16, 24)
PMAX = 24
LASTEXPR = ''
DUMP = None
START0 = False


class Fail(Exception):
    pass


# ---------------------------------------------------------------- values and counts
def isgap(x): return not isH(x) and x < 0
def D(m): return '0' * (-m) if isgap(m) else '10' * m + '1'
def heq(x, y):
    if isH(x) or isH(y): return isH(x) and isH(y) and x == y
    return x == y
def hadd(x, y):
    if isH(x) and isH(y): return Huge(x.s2 + y.s2, x.odd + y.odd, gcd(x.mo, y.mo))
    if isH(x): return lin(1, x, y)
    if isH(y): return lin(1, y, x)
    return x + y
def hmul(c, x): return lin(c, x, 0) if isH(x) else c * x
def hdiff(x, y):
    """x - y as an exact int if determined, else None"""
    if not isH(x) and not isH(y): return x - y
    if isH(x) and isH(y):
        d = x.s2 - y.s2
        if d.denominator != 1: return None
        d = int(d); mo = gcd(x.mo, y.mo)
        if (x.odd - y.odd - d) % mo: return None
        return d
    return None
def pos(c): return isH(c) or c > 0
def dec(c, k=1): return lin(1, c, -k) if isH(c) else c - k
def vkey(v): return ('H', v.s2, v.odd, v.mo) if isH(v) else v


# ---------------------------------------------------------------- normalisation, peeling, grouping
def norm(items):
    out = []
    for it in items:
        if not pos(it[2]): continue
        if it[0] == 'R' and out and out[-1][0] == 'R' and not isgap(it[1]) and heq(out[-1][1], it[1]):
            out[-1] = ['R', out[-1][1], hadd(out[-1][2], it[2])]
        elif it[0] == 'G' and out and out[-1][0] == 'G' and out[-1][1] == it[1]:
            out[-1] = ['G', it[1], hadd(out[-1][2], it[2])]
        else:
            out.append(list(it))
    return out


def peel(items, i):
    """replace group item i by (group with one copy less) + explicit copy"""
    _, pat, c = items[i]
    rest = [['G', pat, dec(c)]] if (isH(c) or c > 1) else []
    return items[:i] + rest + [['R', v, n] for v, n in pat] + items[i + 1:]


def flat_tail(items, k):
    """make the last k items (before [a|r]) plain runs"""
    while True:
        body = items[:-2]
        j = None
        for i in range(max(0, len(body) - k), len(body)):
            if body[i][0] == 'G': j = i
        if j is None: return items
        items = peel(items, j)


def absorb(items):
    """merge explicit copies of a group's pattern adjacent to it; form groups from >= 3 tandem copies"""
    items = norm(items[:-2]) + [list(x) for x in items[-2:]]
    changed = True
    while changed:
        changed = False
        for i, it in enumerate(items[:-2]):
            if it[0] != 'G': continue
            pat = it[1]; L = len(pat)
            nxt = items[i + 1:i + 1 + L]
            if len(nxt) == L and i + L < len(items) - 2 and all(x[0] == 'R' and heq(x[1], v) and not isH(x[2]) and x[2] == n for x, (v, n) in zip(nxt, pat)):
                items = items[:i] + [['G', pat, hadd(it[2], 1)]] + items[i + 1 + L:]; changed = True; break
            prv = items[i - L:i] if i >= L else []
            if len(prv) == L and all(x[0] == 'R' and heq(x[1], v) and not isH(x[2]) and x[2] == n for x, (v, n) in zip(prv, pat)):
                items = items[:i - L] + [['G', pat, hadd(it[2], 1)]] + items[i + 1:]; changed = True; break
    # new groups: >= 3 consecutive copies of a pattern of 2..8 plain small-count runs, away from the active right end
    body_end = len(items) - 14
    i = 0
    while i < body_end:
        best = None
        for L in range(2, 9):
            seg = items[i:i + L]
            if len(seg) < L or any(x[0] != 'R' or isH(x[2]) for x in seg): continue
            key = [(vkey(x[1]), x[2]) for x in seg]
            n = 1
            while i + (n + 1) * L <= body_end and [(vkey(x[1]), x[2]) if x[0] == 'R' and not isH(x[2]) else None for x in items[i + n * L:i + (n + 1) * L]] == key:
                n += 1
            if n >= 3 and (best is None or n * L > best[0] * best[1]): best = (n, L)
        if best:
            n, L = best
            pat = tuple((x[1], x[2]) for x in items[i:i + L])
            items = items[:i] + [['G', pat, n]] + items[i + n * L:]
            body_end -= n * L - 1
        i += 1
    return norm(items[:-2]) + items[-2:]


# ---------------------------------------------------------------- abstract champion process
def r1any(a, r):
    ra = mod(a, 3)
    return r1(lin(1, a, 1 - ra), r), ra


def clear(items):
    """returns (items', steps, kind); peels groups as needed"""
    while True:
        res = clear_try(items)
        if res[0] == 'PEEL':
            pp = peel(items, res[1]); items = norm(pp[:-2]) + pp[-2:]; continue
        return res


def clear_try(items):
    body = items[:-2]
    # active part = runs right of the last gap / group
    g = len(body) - 1
    while g >= 0 and body[g][0] == 'R' and not isgap(body[g][1]): g -= 1
    a, r = items[-2][1], items[-1][1]
    toks = [[x[1], x[2]] for x in body[g + 1:]]
    steps = 0
    while True:
        if not isH(a) and a in (0, 2):
            return norm(body[:g + 1] + [['R', v, c] for v, c in toks]) + [['R', a, 1], ['R', r, 1]], steps, f'ABLK{a}'
        if a != 1:
            r, a = r1any(a, r); steps += 1; continue
        i = len(toks) - 1
        while i >= 0 and not isH(toks[i][0]) and toks[i][0] == 1: i -= 1
        if i < 0:
            if g >= 0 and body[g][0] == 'G' and steps == 0: return ('PEEL', g)
            if g >= 0 and body[g][0] == 'G':
                return ('PEEL', g)
            kind = 'GAP' if g >= 0 else 'LEFT'
            return norm(body[:g + 1] + [['R', v, c] for v, c in toks]) + [['R', 1, 1], ['R', r, 1]], steps, kind
        t, c = toks[i]
        if not isH(t) and t in (0, 2):
            return norm(body[:g + 1] + [['R', v, c] for v, c in toks]) + [['R', 1, 1], ['R', r, 1]], steps, f'BLK{t}'
        bigright = any(isH(cc) for _, cc in toks[i + 1:])
        if (isH(t) or isH(c) or bigright or steps > BUD) and mod(r, 3) == 0:
            return shortcut(body, g, toks, i, steps)
        if isH(c) or c > 1:
            toks[i:i + 1] = [[t, dec(c)], [lin(1, t, -3), 1]]; i += 1
        else:
            toks[i][0] = lin(1, t, -3)
        steps += 1
        if i + 1 < len(toks):
            v1, c1 = toks[i + 1]
            if not (not isH(v1) and v1 == 1): raise Fail('expected D1 run right of the borrow')
            toks[i + 1:i + 2] = [[lin(2, r, 7), 1], [1, dec(c1)]]
        else:
            a = lin(2, r, 7)
        r = 0
        toks = [[v, cc] for v, cc in toks if pos(cc)]


def shortcut(body, g, toks, i, steps):
    """long countdown: find the first non-digit token from position i leftwards (through groups of digits)"""
    ones = 0
    for _, cc in toks[i + 1:]: ones = hadd(ones, cc)
    j = i
    while j >= 0 and mod(toks[j][0], 3) == 1:
        ones = hadd(ones, toks[j][1]); j -= 1
    if j >= 0:
        v, cj = toks[j]
        left = body[:g + 1] + [['R', vv, cc] for vv, cc in toks[:j]] + [['R', v, dec(cj)], ['R', mod(v, 3), 1]]
        return norm(left + [['R', 1, ones]]) + [['R', 1, 1], ['R', U, 1]], steps + 1, f'BLK{mod(v, 3)}*'
    # reached the boundary g of the active part
    while g >= 0:
        it = body[g]
        if it[0] == 'R' and isgap(it[1]):
            return norm(body[:g + 1] + [['R', 1, ones]]) + [['R', 1, 1], ['R', U, 1]], steps + 1, 'GAP*'
        if it[0] == 'G':
            pat, c = it[1], it[2]
            if all(not isgap(v) and mod(v, 3) == 1 for v, _ in pat):
                ones = hadd(ones, hmul(sum(n for _, n in pat), c)); g -= 1; continue
            return ('PEEL', g)
        v, cj = it[1], it[2]
        if mod(v, 3) == 1:
            ones = hadd(ones, cj); g -= 1; continue
        left = body[:g] + [['R', v, dec(cj)], ['R', mod(v, 3), 1]]
        return norm(left + [['R', 1, ones]]) + [['R', 1, 1], ['R', U, 1]], steps + 1, f'BLK{mod(v, 3)}*'
    return norm([['R', 1, ones]]) + [['R', 1, 1], ['R', U, 1]], steps + 1, 'LEFT*'


# ---------------------------------------------------------------- literal stages
_sv = None
def ksim(w, maxs=10 ** 15):
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen(['./ksim2.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               bufsize=1, creationflags=IDLE)
    _sv.stdin.write(f'{w} {len(w)} G {maxs}\n'); _sv.stdin.flush()
    return _sv.stdout.readline().split()


def rep0(x):
    r8 = m2(x.s2, 3); ro = x.odd % 315
    return r8 + 8 * (((ro - r8) * pow(8, -1, 315)) % 315)


def runs_of(vals):
    out = []
    for v in vals:
        if out and out[-1][0] == v: out[-1][1] += 1
        else: out.append([v, 1])
    if out[-1][1] > 1:
        v, c = out.pop(); out += [[v, c - 1], [v, 1]]
    if out[-2][1] > 1:
        v, c = out.pop(-2); out.insert(len(out) - 1, [v, c - 1]); out.insert(len(out) - 1, [v, 1])
    return out


def literal(items, W0=16):
    W = W0
    while True:
        items = flat_tail(items, W)
        full = W >= len(items)
        win = items if full else items[-W:]
        if any(it[0] == 'G' for it in win):
            if not full: raise Fail('group inside window after flattening')
        try:
            res = literal_window(win, full, small=True)
        except Fail as e:
            res = literal_window(win, full, small=False)
        if res[0] == 'WIDEN':
            if full: raise Fail('locality failure on the full configuration')
            W += 12; continue
        if res[0] == 'H': return res
        return ('K', res[1], norm(items[:len(items) - len(win)] + res[2][:-2]) + res[2][-2:])


def literal_window(win, full, small=False):
    global LASTEXPR
    syms = []
    def sym(x):
        if isH(x) and x not in syms: syms.append(x)
    for it in reversed(win):              # the accumulator (rightmost) gets the smallest representative
        if it[0] == 'R': sym(it[1]); sym(it[2])
        else:
            for v, _ in it[1]: sym(v)
            sym(it[2])
    # small: the accumulator symbol (k = 0, rightmost) uses its bare residue representative (>= 8 enforced);
    # on any structural failure the stage is redone with all representatives >= 2520
    reps = [rep0(x) + MLIT * (k if small else 1 + k) for k, x in enumerate(syms)]
    if small and reps and reps[0] < 8: reps[0] += MLIT
    def rep(x, shift=None):
        if not isH(x): return x
        k = syms.index(x)
        return reps[k] + (SHIFT if shift == k else 0)
    def word(shift):
        out = []
        for it in win:
            if it[0] == 'R': out.append(D(rep(it[1], shift)) * rep(it[2], shift))
            else: out.append(''.join(D(rep(v, shift)) * n for v, n in it[1]) * rep(it[2], shift))
        return ''.join(out) + '10101010'
    first_len = None if full else len(D(rep(win[0][1])) * rep(win[0][2])) if win[0][0] == 'R' else None
    outs = []
    for sh in [None] + list(range(len(syms))):
        o = ksim(word(sh))
        if not o: raise Fail('ksim2 gave no output')
        if o[0] == 'K':
            at = o.index('@'); minpos = int(o[at + 1]); o = o[:at]
            if not full and minpos < first_len: return ('WIDEN',)
        outs.append(o)
        if o[0] != 'K': break
    o = outs[0]
    if o[0] == 'H':
        if any(x[0] != 'H' or x[2:4] != o[2:4] for x in outs[1:]): raise Fail(f'halt not uniform {outs}')
        if not full: return ('WIDEN',)        # report halts only from the full configuration
        return ('H', o, syms)
    if o[0] != 'K': raise Fail(f'literal: {o[:3]}')
    base = runs_of(list(map(int, o[3:])))
    co = [[dict(), dict()] for _ in base]
    for k, oo in enumerate(outs[1:]):
        if oo[0] != 'K': raise Fail(f'shift run {k}: {oo[:3]}')
        sv = runs_of(list(map(int, oo[3:])))
        if len(sv) != len(base) or any((u[0] < 0) != (w[0] < 0) for u, w in zip(base, sv)):
            raise Fail(f'run structure depends on huge #{k} ({syms[k]}): {len(base)} vs {len(sv)} runs')
        for p, (u, w) in enumerate(zip(base, sv)):
            for f in (0, 1):
                if u[f] != w[f]:
                    if f == 0 and u[0] < 0: raise Fail('gap length depends on huge')
                    cf = Fraction(w[f] - u[f], SHIFT)
                    if cf.denominator not in DENOMS: raise Fail(f'non-affine dependence run {p}.{f}: {u} {w}')
                    co[p][f][k] = cf
    def build(u, coef):
        if not coef: return u
        const = Fraction(u) - sum(c * reps[k] for k, c in coef.items())
        s2 = sum(c * syms[k].s2 for k, c in coef.items()) + const
        mo = MO
        for k in coef: mo = gcd(mo, syms[k].mo)
        q = 1
        for c in list(coef.values()) + [const]: q = q * c.denominator // gcd(q, c.denominator)
        q2 = 1
        while q % 2 == 0: q //= 2; q2 *= 2
        num = sum(int(c * q * q2) * syms[k].odd for k, c in coef.items()) + int(const * q * q2)
        num = (num * pow(q2, -1, mo)) % mo
        if mo % q or num % q: raise Fail(f'odd division by {q} not resolvable (mo={mo})')
        return Huge(s2, num // q, mo // q)
    def expr(u, coef):
        if not coef: return str(u)
        const = Fraction(u) - sum(c * reps[k] for k, c in coef.items())
        return '+'.join(f'{c}*S{k}' for k, c in coef.items()) + (('+' if const > 0 else '') + str(const) if const else '')
    LASTEXPR = ' '.join(expr(u[0], co[p][0]) + ('' if (not co[p][1] and u[1] == 1) else '^' + expr(u[1], co[p][1]))
                        for p, u in enumerate(base)) + '  | S: ' + ' '.join(f'S{k}={x}' for k, x in enumerate(syms))
    out = [['R', build(u[0], co[p][0]), build(u[1], co[p][1])] for p, u in enumerate(base)]
    if out[-1][2] != 1 or out[-2][2] != 1: raise Fail('a/r run not single')
    if DUMP is not None:
        import json
        def hj(x): return {'s2': str(x.s2), 'odd': x.odd, 'mo': x.mo} if isH(x) else x
        def form(u, coef):
            const = Fraction(u) - sum(c * reps[k] for k, c in coef.items())
            return {'const': str(const), 'coef': {str(k): str(c) for k, c in coef.items()}}
        DUMP.write(json.dumps({'win': [[it[0], hj(it[1]) if it[0] == 'R' else [[hj(v), n] for v, n in it[1]], hj(it[2])] for it in win],
                               'syms': [hj(x) for x in syms], 'reps': reps, 'steps': int(o[1]), 'full': bool(full),
                               'out': [[form(u[0], co[p][0]), form(u[1], co[p][1])] for p, u in enumerate(base)]}) + chr(10))
    return ('K', int(o[1]), out)


# ---------------------------------------------------------------- periods
def shape(items):
    return tuple((it[0], vkey(it[1]) if it[0] == 'R' else tuple((vkey(v), n) for v, n in it[1]),
                  None if (it[0] == 'R' and not isH(it[2]) and it[2] == 1 and False) else 0) for it in items)


def counts(items): return [it[2] for it in items]


def try_period(hist, kinds):
    """hist: list of item-lists after each jump; returns (P, deltas) for an affine period over 2 periods"""
    n = len(hist)
    for P in range(1, PMAX + 1):
        if n < 2 * P + 1: break
        A, B, C = hist[n - 1 - 2 * P], hist[n - 1 - P], hist[n - 1]
        if not (shape(A) == shape(B) == shape(C)): continue
        if kinds[n - 2 * P:n - P] != kinds[n - P:n]: continue
        ok = True; deltas = []
        for ca, cb, cc in zip(counts(A), counts(B), counts(C)):
            d1, d2 = hdiff(cb, ca), hdiff(cc, cb)
            if d1 is None or d2 is None or d1 != d2: ok = False; break
            deltas.append(d1)
        # values must be equal too (shape compares vkeys) -> fine
        if ok and any(deltas): return P, deltas
    return None


def accelerate(items, P, deltas):
    """skip N periods; returns (items', N) or None"""
    cands = []
    for it, d in zip(items, deltas):
        if d >= 0: continue
        c = it[2]; margin = 2 * (-d) + 8
        if isH(c):
            rem = margin + (mod(c, -d) - margin) % (-d)
            cands.append(('H', c, rem, -d))
        else:
            if c - margin <= 0: return None
            cands.append(('I', (c - margin) // (-d), None, -d))
    if not cands: return None
    ints = [x[1] for x in cands if x[0] == 'I']
    if ints:
        N = min(ints)
        if N <= 0: return None
    else:
        # all limiting counts huge: they must have exact differences
        base = cands[0]
        best = None
        for x in cands:
            Nx = Huge((x[1].s2 - x[2]) / x[3], 0, 1)
            # exact N as Huge
            num = x[1].odd - x[2]; mo = x[1].mo; g = gcd(x[3], mo)
            if num % g: raise Fail('period division not exact')
            Nx = Huge((x[1].s2 - x[2]) / x[3], (num // g) * pow(x[3] // g, -1, mo // g), mo // g)
            if best is None: best = Nx
            else:
                dd = hdiff(Nx, best)
                if dd is None: raise Fail('cannot compare two huge period counts')
                if dd < 0: best = Nx
        N = best
    new = []
    for it, d in zip(items, deltas):
        c = it[2]
        if d: c = hadd(c, hmul(d, N)) if isH(N) else hadd(c, d * N)
        new.append([it[0], it[1], c])
    return new, N


# ---------------------------------------------------------------- driver
def rle(items):
    out = []
    for it in items:
        c = it[2]
        cs = '' if (not isH(c) and c == 1) else f'^{c}'
        if it[0] == 'R':
            v = it[1]; out.append((f'g{-v}' if isgap(v) else f'{v}') + cs)
        else:
            out.append('(' + ' '.join((f'g{-v}' if isgap(v) else f'{v}') + ('' if n == 1 else f'^{n}') for v, n in it[1]) + ')' + cs)
    return ' '.join(out)


def follow(b0, log=None, verbose=False, maxj=10 ** 8):
    items = [['R', 1, 35], ['R', 1, 1], ['R', 3 * b0, 1]]        # K(0^35; 0; b0) = [D1^35 | 1 | 3b]
    if START0:   # stage 0 result, checked literally (reach2.exe, jobs_s0.txt) and reached by the follower for b=1,6,11,16
        assert b0 % 5 == 1
        items = [['R', 9, (12 * b0 + 8) // 5], ['R', 11, 1], ['R', 1, (24 * b0 + 196) // 5], ['R', 1, 1], ['R', 1, 1]]
    nj = 0; nl = 0; total = 0; hist = []; kinds = []; nacc = 0
    while nj < maxj:
        if len(items) >= 2:
            E, steps, kind = clear(items)
            if steps > 0:
                nj += 1; total = hadd(total, 1)
                E = absorb(E)
                hist.append(E); kinds.append(kind)
                if len(hist) > 3 * PMAX + 3: hist.pop(0); kinds.pop(0)
                if log: log.write(f'J{nj} T={total} {kind} steps={steps} | ' + rle(E) + '\n')
                items = E
                per = try_period(hist, kinds)
                if per:
                    P, deltas = per
                    acc = accelerate(items, P, deltas)
                    if acc:
                        items, N = acc; nacc += 1
                        total = hadd(total, hmul(P, N)) if isH(N) else hadd(total, P * N)
                        hist = [items]; kinds = [kind]
                        if log: log.write(f'ACC P={P} N={N} deltas={deltas} T={total} | ' + rle(items) + '\n')
                continue
        res = literal(items); nl += 1
        if res[0] == 'H':
            if log: log.write(f'HALT {" ".join(res[1])} T={total} from {rle(items)}\n')
            return 'HALT', nj, nl, total, ' '.join(res[1])
        items = absorb(res[2])
        if log and verbose: log.write(f'  L {res[1]} -> {rle(items)}\n    X {LASTEXPR}\n')
    return 'MAX', nj, nl, total, None


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('b0', type=int); ap.add_argument('--log'); ap.add_argument('-v', action='store_true')
    ap.add_argument('--maxj', type=int, default=10 ** 8); ap.add_argument('--dump'); ap.add_argument('--start0', action='store_true')
    a = ap.parse_args()
    if a.dump: DUMP = open(a.dump, 'w', buffering=1)
    if a.start0: START0 = True
    lg = open(a.log, 'w', buffering=1) if a.log else None
    try:
        r = follow(a.b0, lg, a.v, a.maxj)
    except (Fail, Unknown, AssertionError) as e:
        import traceback; traceback.print_exc()
        r = ('FAIL', repr(e)[:3000])
    print(a.b0, *r, flush=True)
    if lg: lg.write(f'RESULT {r}\n'); lg.close()
