"""Gap-aware, 2-adic-exact follower for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH (gh0LH verifier).
Configuration (G-frame K-moment): items = tokens (int >= 0 or Huge) and gaps (int -k = 0^k, k >= 2), last two items [a, r];
word = items as D(m) = (10)^m 1 / 0^k, then 10101010, head on the blank right, state G.
Abstract champion rules on the tokens right of the last gap (checked literally, all contexts: rulecheck*.py):
  R1 [a+3|r]->[a|2r+6] (any a);  R2 [X+3|1|r]->[X|2r+7|0];  R3 [Y+3,1^k|1|r]->[Y,2r+7,1^(k-1)|1|0]
Events (a in {0,2}; borrow reaching 0/2, the gap or the left end) run literally (kst3.exe) with representatives
rep = CRT(s2 mod 8, odd mod 315) [+2520*BASEK] and one +SHIFT run per huge symbol to read off affine (rational) outputs.
Borrow from a huge token with r = 0 mod 3 -> token -> residue mod 3, right part -> D1, accumulator -> U.
  python ghf4.py B0 [--log FILE] [-v] [--maxj N]"""
import sys, subprocess, argparse
from fractions import Fraction
from math import gcd
from hv2 import Huge, U, mk, mod, lin, r1, isH, Unknown, MO, m2
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
BUD = 3000; SHIFT = 360; MLIT = 2520; BASEK = 0
class Fail(Exception): pass
def isgap(x): return not isH(x) and x < 0
def D(m): return '0' * (-m) if isgap(m) else '10' * m + '1'
TAIL = '10101010'
_sv = None
def kst(w, maxs=40_000_000_000):
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen(['./kst3.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               bufsize=1, creationflags=IDLE)
    _sv.stdin.write(f'{w} {len(w)} G {maxs}\n'); _sv.stdin.flush()
    return _sv.stdout.readline().split()
def r1any(a, r):
    ra = mod(a, 3)
    return r1(lin(1, a, 1 - ra), r), ra
def clear(T):
    g = len(T) - 1
    while g >= 0 and not isgap(T[g]): g -= 1
    if g >= len(T) - 2: raise Fail('gap inside [a|r]')
    E, steps, kind, fp = clear0(T[g + 1:])
    if g >= 0 and kind.startswith('LEFT'): kind = 'GAP' + kind[4:]
    return T[:g + 1] + E, steps, kind
def clear0(T):
    toks, a, r = list(T[:-2]), T[-2], T[-1]
    steps = 0
    while True:
        if not isH(a) and a in (0, 2): return toks + [a, r], steps, f'ABLK{a}', len(toks)
        if a != 1:
            r, a = r1any(a, r); steps += 1; continue
        i = len(toks) - 1
        while i >= 0 and toks[i] == 1: i -= 1
        if i < 0: return toks + [1, r], steps, 'LEFT', -1
        t = toks[i]
        if not isH(t) and t in (0, 2): return toks + [1, r], steps, f'BLK{t}', i
        if (isH(t) or steps > BUD) and mod(r, 3) == 0:
            j = i
            while j >= 0 and mod(toks[j], 3) == 1: j -= 1
            n = len(toks)
            if j < 0: return [1] * n + [1, U], steps + 1, 'LEFT*', -1
            return toks[:j] + [mod(toks[j], 3)] + [1] * (n - j - 1) + [1, U], steps + 1, f'BLK{mod(toks[j], 3)}*', j
        toks[i] = lin(1, t, -3); steps += 1
        if i + 1 < len(toks): toks[i + 1] = lin(2, r, 7)
        else: a = lin(2, r, 7)
        r = 0
def rep0(x):
    r8 = m2(x.s2, 3); ro = x.odd % 315
    return (r8 + 8 * (((ro - r8) * pow(8, -1, 315)) % 315)) + MLIT * BASEK
def literal(T):
    syms = []
    for x in T:
        if isH(x) and x not in syms: syms.append(x)
    def rep(x, shift=None):
        if not isH(x): return x
        k = syms.index(x)
        return rep0(x) + (SHIFT if shift == k else 0)
    outs = []
    for sh in [None] + list(range(len(syms))):
        o = kst(''.join(D(rep(x, sh)) for x in T) + TAIL)
        if not o: raise Fail('kst3 gave no output')
        outs.append(o)
        if o[0] != 'K': break
    o = outs[0]
    if o[0] == 'H':
        if any(x[0] != 'H' or x[2:4] != o[2:4] for x in outs[1:]): raise Fail(f'halt not uniform {outs}')
        return ('H', o, syms)
    if o[0] != 'K': raise Fail(f'literal: {o[:3]} from {rle(T)}')
    base = list(map(int, o[3:]))
    coefs = [dict() for _ in base]
    for k, oo in enumerate(outs[1:]):
        if oo[0] != 'K': raise Fail(f'shift run {k}: {oo[:3]} from {rle(T)}')
        sv = list(map(int, oo[3:]))
        if len(sv) != len(base): raise Fail(f'token count depends on huge #{k} ({syms[k]}): {len(base)} vs {len(sv)}; from {rle(T)}')
        for p, (u, v) in enumerate(zip(base, sv)):
            if u != v:
                if u < 0 or v < 0: raise Fail(f'gap depends on huge: {u} {v}')
                c = Fraction(v - u, SHIFT)
                if c.denominator not in (1, 2, 3, 4, 6, 8, 12, 16, 24): raise Fail(f'non-affine dependence pos {p}: {u} {v} from {rle(T)}')
                coefs[p][k] = c
    out = []
    for p, u in enumerate(base):
        if not coefs[p]: out.append(u); continue
        const = Fraction(u) - sum(c * rep0(syms[k]) for k, c in coefs[p].items())
        s2 = sum(c * syms[k].s2 for k, c in coefs[p].items()) + const
        mo = MO
        for k in coefs[p]: mo = gcd(mo, syms[k].mo)
        q = 1
        for c in list(coefs[p].values()) + [const]: q = q * c.denominator // gcd(q, c.denominator)
        q2 = 1
        while q % 2 == 0: q //= 2; q2 *= 2
        num = sum(int(c * q * q2) * syms[k].odd for k, c in coefs[p].items()) + int(const * q * q2)
        num = (num * pow(q2, -1, mo)) % mo
        if mo % q or num % q: raise Fail(f'odd division by {q} not resolvable (mo={mo}) from {rle(T)}')
        out.append(Huge(s2, (num // q), mo // q))
    return ('K', int(o[1]), out)
def rle(T):
    out = []
    for x in T:
        if out and out[-1][0] == x: out[-1][1] += 1
        else: out.append([x, 1])
    return ' '.join((f'g{-x}' if isgap(x) else f'{x}') + ('' if c == 1 else f'^{c}') for x, c in out)
def follow(b0, log=None, verbose=False, maxj=10**8):
    T = [1] * 36 + [3 * b0]                     # K(0^35; 0; b0) = [D1^35 | 1 | 3b]
    nj = nl = 0
    while nj < maxj:
        if len(T) >= 2:
            E, steps, kind = clear(T)
            if steps > 0:
                nj += 1
                if log: log.write(f'J{nj} {kind} steps={steps} | ' + rle(E) + '\n')
                T = E; continue
        res = literal(T); nl += 1
        if res[0] == 'H':
            if log: log.write(f'HALT {" ".join(res[1])} syms={res[2]} from {rle(T)}\n')
            return 'HALT', nj, nl, ' '.join(res[1])
        T = res[2]
        if log and verbose: log.write(f'  L {res[1]} -> {rle(T)}\n')
    return 'MAX', nj, nl, None
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('b0', type=int); ap.add_argument('--log'); ap.add_argument('-v', action='store_true')
    ap.add_argument('--maxj', type=int, default=10**8)
    a = ap.parse_args()
    lg = open(a.log, 'w', buffering=1) if a.log else None
    try:
        r = follow(a.b0, lg, a.v, a.maxj)
    except (Fail, Unknown, AssertionError) as e:
        r = ('FAIL', repr(e)[:3000])
    print(a.b0, *r, flush=True)
    if lg: lg.write(f'RESULT {r}\n'); lg.close()
