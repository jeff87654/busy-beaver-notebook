"""Run-length, gap-aware, 2-adic-exact follower for
1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH (gh0LH verifier).
Configuration (G-frame K-moment): runs [v, c]: v = token (int >= 0 or Huge) or gap (int -k = 0^k), c = count (int >= 1
or Huge); the last two runs are singletons [a,1], [r,1]; word = D(v)^c ... then 10101010, head on the blank right, state G.
Abstract champion rules on the tokens right of the last gap (literal checks: rulecheck.py / rulecheck3.py):
  R1 [a+3|r]->[a|2r+6];  R2 [X+3|1|r]->[X|2r+7|0];  R3 [Y+3,1^k|1|r]->[Y,2r+7,1^(k-1)|1|0]
Events run literally (kst3.exe) with representatives CRT(s2 mod 8, odd mod 315) and one +SHIFT run per huge symbol;
outputs (token values and run counts) are read off as rational-affine functions of the huge symbols.
Borrow from a huge token / across a huge run with r = 0 mod 3 -> shortcut (non-digit -> residue mod 3, right part -> D1,
accumulator -> U).
  python ghf5.py B0 [--log FILE] [-v] [--maxj N]"""
import sys, subprocess, argparse
from fractions import Fraction
from math import gcd
from hv2 import Huge, U, mk, mod, lin, r1, isH, Unknown, MO, m2
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
BUD = 3000; SHIFT = 360; MLIT = 2520; BASEK = 0
DENOMS = (1, 2, 3, 4, 6, 8, 12, 16, 24)


class Fail(Exception):
    pass


def isgap(x): return not isH(x) and x < 0
def D(m): return '0' * (-m) if isgap(m) else '10' * m + '1'


TAIL = '10101010'
_sv = None


def kst(w, maxs=40_000_000_000):
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen(['./ksim.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               bufsize=1, creationflags=IDLE)
    _sv.stdin.write(f'{w} {len(w)} G {maxs}\n'); _sv.stdin.flush()
    return _sv.stdout.readline().split()


def hadd(x, y):
    """x + y for counts (int or Huge)"""
    if isH(x) and isH(y): return Huge(x.s2 + y.s2, x.odd + y.odd, gcd(x.mo, y.mo))
    if isH(x): return lin(1, x, y)
    if isH(y): return lin(1, y, x)
    return x + y


def dec(c): return lin(1, c, -1) if isH(c) else c - 1
def pos(c): return isH(c) or c > 0


def norm(R):
    out = []
    for v, c in R:
        if not pos(c): continue
        if out and ((isH(v) and out[-1][0] == v) or (not isH(v) and not isH(out[-1][0]) and out[-1][0] == v)):
            out[-1][1] = hadd(out[-1][1], c)
        else:
            out.append([v, c])
    return out


def total(cs):
    t = 0
    for c in cs: t = hadd(t, c)
    return t


def r1any(a, r):
    ra = mod(a, 3)
    return r1(lin(1, a, 1 - ra), r), ra


def clear(R):
    g = len(R) - 1
    while g >= 0 and not isgap(R[g][0]): g -= 1
    if g >= len(R) - 2: raise Fail('gap inside [a|r]')
    E, steps, kind = clear0([list(x) for x in R[g + 1:]])
    if g >= 0 and kind.startswith('LEFT'): kind = 'GAP' + kind[4:]
    return [list(x) for x in R[:g + 1]] + E, steps, kind


def clear0(R):
    for x in R[-2:]:
        if x[1] != 1: raise Fail(f'[a|r] runs must be single: {R[-2:]}')
    toks, a, r = R[:-2], R[-2][0], R[-1][0]
    steps = 0
    while True:
        if not isH(a) and a in (0, 2): return norm(toks) + [[a, 1], [r, 1]], steps, f'ABLK{a}'
        if a != 1:
            r, a = r1any(a, r); steps += 1; continue
        i = len(toks) - 1
        while i >= 0 and (not isH(toks[i][0]) and toks[i][0] == 1): i -= 1
        if i < 0: return norm(toks) + [[1, 1], [r, 1]], steps, 'LEFT'
        t, c = toks[i]
        if not isH(t) and t in (0, 2): return norm(toks) + [[1, 1], [r, 1]], steps, f'BLK{t}'
        bigright = any(isH(cc) for _, cc in toks[i + 1:])
        if (isH(t) or isH(c) or bigright or steps > BUD) and mod(r, 3) == 0:
            j = i
            while j >= 0 and mod(toks[j][0], 3) == 1: j -= 1
            right = total([cc for _, cc in toks[j + 1:]])
            if j < 0: return norm([[1, right]]) + [[1, 1], [U, 1]], steps + 1, 'LEFT*'
            v, cj = toks[j]
            head = toks[:j] + [[v, dec(cj)]]
            return norm(head + [[mod(v, 3), 1], [1, right]]) + [[1, 1], [U, 1]], steps + 1, f'BLK{mod(v, 3)}*'
        # exact borrow from the last element of run i
        if isH(c) or c > 1:
            toks[i:i + 1] = [[t, dec(c)], [lin(1, t, -3), 1]]
            i += 1
        else:
            toks[i][0] = lin(1, t, -3)
        steps += 1
        if i + 1 < len(toks):
            v1, c1 = toks[i + 1]
            if v1 != 1: raise Fail('expected a run of D1 right of the borrow')
            toks[i + 1:i + 2] = [[lin(2, r, 7), 1], [1, dec(c1)]]
        else:
            a = lin(2, r, 7)
        r = 0
        toks = norm(toks)


def rep0(x):
    r8 = m2(x.s2, 3); ro = x.odd % 315
    return (r8 + 8 * (((ro - r8) * pow(8, -1, 315)) % 315)) + MLIT * BASEK


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


def literal(R):
    syms = []
    for v, c in R:
        for x in (v, c):
            if isH(x) and x not in syms: syms.append(x)

    reps = [rep0(x) + MLIT * (1 + k) for k, x in enumerate(syms)]

    def rep(x, shift=None):
        if not isH(x): return x
        k = syms.index(x)
        return reps[k] + (SHIFT if shift == k else 0)
    outs = []
    for sh in [None] + list(range(len(syms))):
        o = kst(''.join(D(rep(v, sh)) * rep(c, sh) for v, c in R) + TAIL)
        if not o: raise Fail('kst3 gave no output')
        outs.append(o)
        if o[0] != 'K': break
    o = outs[0]
    if o[0] == 'H':
        if any(x[0] != 'H' or x[2:4] != o[2:4] for x in outs[1:]): raise Fail(f'halt not uniform {outs}')
        return ('H', o, syms)
    if o[0] != 'K': raise Fail(f'literal: {o[:3]} from {rle(R)}')
    base = runs_of(list(map(int, o[3:])))
    co = [[dict(), dict()] for _ in base]
    for k, oo in enumerate(outs[1:]):
        if oo[0] != 'K': raise Fail(f'shift run {k}: {oo[:3]} from {rle(R)}')
        sv = runs_of(list(map(int, oo[3:])))
        if len(sv) != len(base) or any((u[0] < 0) != (w[0] < 0) for u, w in zip(base, sv)):
            raise Fail(f'run structure depends on huge #{k} ({syms[k]}): {len(base)} vs {len(sv)} runs; from {rle(R)}')
        for p, (u, w) in enumerate(zip(base, sv)):
            for f in (0, 1):
                if u[f] != w[f]:
                    if f == 0 and u[0] < 0: raise Fail('gap length depends on huge')
                    cf = Fraction(w[f] - u[f], SHIFT)
                    if cf.denominator not in DENOMS: raise Fail(f'non-affine dependence run {p}.{f}: {u} {w} from {rle(R)}')
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
    out = [[build(u[0], co[p][0]), build(u[1], co[p][1])] for p, u in enumerate(base)]
    if out[-1][1] != 1 or out[-2][1] != 1: raise Fail('a/r run not single')
    return ('K', int(o[1]), norm(out[:-2]) + out[-2:])


def rle(R):
    return ' '.join((f'g{-v}' if isgap(v) else f'{v}') + ('' if (not isH(c) and c == 1) else f'^{c}') for v, c in R)


def follow(b0, log=None, verbose=False, maxj=10**8):
    R = [[1, 35], [1, 1], [3 * b0, 1]]              # K(0^35; 0; b0) = [D1^35 | 1 | 3b]
    nj = nl = 0
    while nj < maxj:
        if len(R) >= 2:
            E, steps, kind = clear(R)
            if steps > 0:
                nj += 1
                if log: log.write(f'J{nj} {kind} steps={steps} | ' + rle(E) + '\n')
                R = E; continue
        res = literal(R); nl += 1
        if res[0] == 'H':
            if log: log.write(f'HALT {" ".join(res[1])} syms={res[2]} from {rle(R)}\n')
            return 'HALT', nj, nl, ' '.join(res[1])
        R = res[2]
        if log and verbose: log.write(f'  L {res[1]} -> {rle(R)}\n')
    return 'MAX', nj, nl, None


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('b0', type=int); ap.add_argument('--log'); ap.add_argument('-v', action='store_true')
    ap.add_argument('--maxj', type=int, default=10**8)
    a = ap.parse_args()
    lg = open(a.log, 'w', buffering=1) if a.log else None
    try:
        r = follow(a.b0, lg, a.v, a.maxj)
    except (Fail, Unknown, AssertionError) as e:
        import traceback; traceback.print_exc()
        r = ('FAIL', repr(e)[:3000])
    print(a.b0, *r, flush=True)
    if lg: lg.write(f'RESULT {r}\n'); lg.close()
