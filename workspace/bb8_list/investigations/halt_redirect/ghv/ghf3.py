"""Gap-aware follower (ghf3; items: tokens >= 0 or Huge, gaps 0^k stored as -k) for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH (gh0LH verifier).
Configuration = token list [t1..tn, a, r] + tail (10)^4, head on the blank right, state G (a K-moment).
Abstract counter (champion rules R1-R3, assumed for all left contexts): exact while small; a borrow from a huge
token (or a long run) is shortcut structurally: tokens right of the failing token -> D1, failing token -> t mod 3,
accumulator -> U (the attracting residue).  Events (borrow fails at D0/D2 or at the left end) are run literally by
kst.exe with representatives rho = res mod 2520 + 2520*j; one extra run per huge value identifies affine outputs.
Fails loudly on anything unexpected.
  python ghf.py B0 [--stages N] [--log FILE] [--mlit 2520]"""
import sys, subprocess, argparse
from hval import Huge, U, mk, mod, lin, r1, M, Unknown
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
class Fail(Exception): pass
def D(m): return '0' * (-m) if (not isinstance(m, Huge) and m < 0) else '10' * m + '1'
TAIL = '10101010'
_sv = None
def kst(word, maxs=4_000_000_000):
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen(['./kst3.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               bufsize=1, creationflags=IDLE)
    _sv.stdin.write(f'{word} {len(word)} G {maxs}\n'); _sv.stdin.flush()
    return _sv.stdout.readline().split()
BUD = 3000
SHIFT = 360
BASEK = 0
def isgap(x): return not isinstance(x, Huge) and x < 0
def clear(T):
    """abstract champion process on the tokens right of the last gap"""
    g = len(T) - 1
    while g >= 0 and not isgap(T[g]): g -= 1
    if g >= len(T) - 2: raise Fail('gap inside [a|r]')
    E, steps, kind, fp, huge = clear0(T[g + 1:])
    return T[:g + 1] + E, steps, kind + ('/gap' if g >= 0 and fp < 0 and kind.startswith('LEFT') else ''), (fp + g + 1 if fp >= 0 else fp), huge
def clear0(T):
    toks, a, r = list(T[:-2]), T[-2], T[-1]
    steps = 0; huge = False
    while True:
        if not isinstance(a, Huge) and a in (0, 2): return toks + [a, r], steps, f'ABLK{a}', len(toks), huge
        if a != 1:
            ra = mod(a, 3)
            r = r1(lin(1, a, 1 - ra), r); a = ra; steps += 1   # R1 iterated: a -> a mod 3
            continue
        i = len(toks) - 1
        while i >= 0 and toks[i] == 1: i -= 1
        if i < 0: return toks + [1, r], steps, 'LEFT', -1, huge
        t = toks[i]
        if not isinstance(t, Huge) and t in (0, 2): return toks + [1, r], steps, f'BLK{t}', i, huge
        if (isinstance(t, Huge) or steps > BUD) and mod(r, 3) == 0:
            j = i
            while j >= 0 and mod(toks[j], 3) == 1: j -= 1
            n = len(toks)
            if j < 0: return [1] * n + [1, U], steps, 'LEFT*', -1, True
            return toks[:j] + [mod(toks[j], 3)] + [1] * (n - j - 1) + [1, U], steps, f'BLK{mod(toks[j],3)}*', j, True
        toks[i] = lin(1, t, -3); steps += 1
        if i + 1 < len(toks): toks[i + 1] = lin(2, r, 7)
        else: a = lin(2, r, 7)
        r = 0
def literal(T, mlit):
    """run literally from K-config T to the next K-moment; huge values via representatives"""
    hs = sorted({x.res for x in T if isinstance(x, Huge)}); hsm = {}
    for x in T:
        if isinstance(x, Huge): hsm[hs.index(x.res)] = __import__('math').gcd(hsm.get(hs.index(x.res), x.mod), x.mod)
    def rep(x, shift=None):
        if not isinstance(x, Huge): return x
        k = hs.index(x.res)
        return x.res % mlit + mlit * BASEK + (SHIFT if shift == k else 0)
    outs = []
    for sh in [None] + list(range(len(hs))):
        w = ''.join(D(rep(x, sh)) for x in T) + TAIL
        o = kst(w)
        if not o: raise Fail('kst.exe gave no output (crash?) on config ' + rle(T))
        outs.append(o)
        if o[0] != 'K': break
    o = outs[0]
    if o[0] == 'H':
        if any(x[0] != 'H' or x[2:4] != o[2:4] for x in outs[1:]): raise Fail(f'halt not uniform {outs}')
        return ('H', o)
    if o[0] != 'K': raise Fail(f'literal: {o}')
    base = list(map(int, o[3:]))
    res = [x for x in base]
    for k, oo in enumerate(outs[1:]):
        if oo[0] != 'K': raise Fail(f'shift run {k}: {oo[:3]}')
        sv = list(map(int, oo[3:]))
        if len(sv) != len(base): raise Fail(f'token count depends on huge #{k}: {len(base)} vs {len(sv)}')
        for p, (u, v) in enumerate(zip(base, sv)):
            if u != v:
                if u < 0 or v < 0: raise Fail(f'gap depends on huge: {u} {v}')
                from fractions import Fraction
                c = Fraction(v - u, SHIFT)
                if c.denominator not in (1, 2, 3, 4, 6): raise Fail(f'non-affine dependence pos {p}: {u} {v}')
                rho = hs[k] % mlit + mlit * BASEK
                prev = res[p]
                if isinstance(prev, tuple): coef, const = prev
                else: coef, const = {}, u
                coef = dict(coef); coef[k] = c; const = const - c * rho
                res[p] = (coef, const)
    out = []
    from fractions import Fraction
    for x in res:
        if isinstance(x, tuple):
            coef, const = x
            q = 1
            for c in coef.values(): q = q * Fraction(c).denominator // __import__('math').gcd(q, Fraction(c).denominator)
            md = M
            for k in coef: md = __import__('math').gcd(md, hsm[k])
            num = sum(int(c * q) * hs[k] for k, c in coef.items()) + int(const * q)
            if md % q or num % q: raise Fail(f'fractional affine output not resolvable: q={q} md={md}')
            out.append(Huge((num % md) // q, md // q))
        else:
            out.append(x)
    return ('K', int(o[1]), out)
def rle(T):
    out = []
    for x in T:
        if out and out[-1][0] == x: out[-1][1] += 1
        else: out.append([x, 1])
    return ' '.join(f'{x}' if c == 1 else f'{x}^{c}' for x, c in out)
def follow(b0, stages=10**7, log=None, mlit=2520, verbose=False):
    T = [1] * 36 + [3 * b0]                     # K(0^35; 0; b0) = [D1^35 | 1 | 3b]
    njump = 0; nlit = 0; litsteps = 0
    while njump < stages:
        ok = len(T) >= 2
        if ok:
            E, steps, kind, fp, huge = clear(T)
            if steps > 0:
                njump += 1
                if log: log.write(f'J{njump} {kind} huge={int(huge)} steps={steps} | ' + rle(E) + chr(10))
                T = E
                continue
        res = literal(T, mlit); nlit += 1
        if res[0] == 'H':
            if log: log.write(f'HALT {res[1]}\n')
            return 'HALT', njump, nlit, res[1]
        litsteps += res[1]
        T = res[2]
        if log and verbose: log.write(f'  L {res[1]} -> {rle(T)}\n')
    return 'MAX', njump, nlit, None
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('b0', type=int); ap.add_argument('--stages', type=int, default=10**7)
    ap.add_argument('--log'); ap.add_argument('--mlit', type=int, default=2520); ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    lg = open(a.log, 'w', buffering=1) if a.log else None
    try:
        r = follow(a.b0, a.stages, lg, a.mlit, a.v)
    except (Fail, Unknown, AssertionError) as e:
        r = ('FAIL', str(e)[:3000])
    print(a.b0, *r, flush=True)
    if lg: lg.write(f'RESULT {r}\n'); lg.close()
