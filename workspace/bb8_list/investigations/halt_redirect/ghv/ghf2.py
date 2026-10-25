"""Two-frame follower for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH (gh0LH verifier).
A configuration is (frame, T) with T = [t1..tn, a, r]:
  G-frame word: D(t1)..D(tn) D(a) D(r) 10101010, head on the blank right, state G
  B-frame word: D(t1)..D(tn) D(a) (10)^r 01,      head on the blank right, state B
Abstract counters (rules checked literally by rulecheck2.py, all left contexts):
  G: R1 [a+3|r]->[a|2r+6]; R2 [X+3|1|r]->[X|2r+7|0]; R3 [Y+3,1^k|1|r]->[Y,2r+7,1^(k-1)|1|0]
  B: R1B [a+3|r]->[a|2r+6]; R2B [X+3|0|r]->[X|r|6]
Everything else (events) runs literally (kst2.exe) with representatives res mod 2520 (+SHIFT for the affine check).
A borrow from a huge token (r = 0 mod 3) is shortcut: token -> its residue mod 3, right part cleared, accumulator -> U (G) / UB (B).
  python ghf2.py B0 [--log FILE] [-v]"""
import sys, subprocess, argparse
import hval
from hval import Huge, U, UB, mk, mod, lin, r1, M
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
BUD = 3000; SHIFT = 360; MLIT = 2520
class Fail(Exception): pass
def D(m): return '10' * m + '1'
def word(fr, T):
    if fr == 'G': return ''.join(D(x) for x in T) + '10101010'
    return ''.join(D(x) for x in T[:-1]) + '10' * T[-1] + '01'
_sv = None
def kst(w, st, maxs=20_000_000_000):
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen(['./kst2.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               bufsize=1, creationflags=IDLE)
    _sv.stdin.write(f'{w} {len(w)} {st} {maxs}\n'); _sv.stdin.flush()
    return _sv.stdout.readline().split()
def r1any(a, r):
    ra = mod(a, 3)
    return r1(lin(1, a, 1 - ra), r), ra
def clearG(T):
    toks, a, r = list(T[:-2]), T[-2], T[-1]
    steps = 0
    while True:
        if not isinstance(a, Huge) and a in (0, 2): return toks + [a, r], steps, f'G-ABLK{a}', len(toks)
        if a != 1:
            r, a = r1any(a, r); steps += 1; continue
        i = len(toks) - 1
        while i >= 0 and toks[i] == 1: i -= 1
        if i < 0: return toks + [1, r], steps, 'G-LEFT', -1
        t = toks[i]
        if not isinstance(t, Huge) and t in (0, 2): return toks + [1, r], steps, f'G-BLK{t}', i
        if (isinstance(t, Huge) or steps > BUD) and mod(r, 3) == 0:
            j = i
            while j >= 0 and mod(toks[j], 3) == 1: j -= 1
            n = len(toks)
            if j < 0: return [1] * n + [1, U], steps + 1, 'G-LEFT*', -1
            return toks[:j] + [mod(toks[j], 3)] + [1] * (n - j - 1) + [1, U], steps + 1, f'G-BLK{mod(toks[j], 3)}*', j
        toks[i] = lin(1, t, -3); steps += 1
        if i + 1 < len(toks): toks[i + 1] = lin(2, r, 7)
        else: a = lin(2, r, 7)
        r = 0
def clearB(T):
    toks, a, r = list(T[:-2]), T[-2], T[-1]
    steps = 0
    while True:
        if not isinstance(a, Huge) and a in (1, 2): return toks + [a, r], steps, f'B-ABLK{a}', len(toks)
        if a != 0:
            r, a = r1any(a, r); steps += 1; continue
        if not toks: return [0, r], steps, 'B-LEFT', -1
        t = toks[-1]
        if not isinstance(t, Huge) and t in (0, 1, 2): return toks + [0, r], steps, f'B-BLK{t}', len(toks) - 1
        if (isinstance(t, Huge) or steps > BUD) and mod(r, 3) == 0:
            toks[-1] = mod(t, 3)
            return toks + [0, hval.UB], steps + 1, f'B-BLK{mod(t, 3)}*', len(toks) - 1
        toks[-1] = lin(1, t, -3); a = r; r = 6; steps += 1
def literal(fr, T):
    hs = sorted({x.res for x in T if isinstance(x, Huge)})
    def rep(x, shift=None):
        if not isinstance(x, Huge): return x
        k = hs.index(x.res)
        return x.res % MLIT + (SHIFT if shift == k else 0)
    outs = []
    for sh in [None] + list(range(len(hs))):
        o = kst(word(fr, [rep(x, sh) for x in T]), fr)
        if not o: raise Fail('kst2 gave no output')
        outs.append(o)
        if o[0] != 'K': break
    o = outs[0]
    if o[0] == 'H':
        if any(x[0] != 'H' or x[2:4] != o[2:4] for x in outs[1:]): raise Fail(f'halt not uniform {outs}')
        return ('H', o, hs)
    if o[0] != 'K': raise Fail(f'literal: {o[:3]} from {fr} {rle(T)}')
    nfr = o[1]; base = list(map(int, o[4:]))
    res = list(base)
    for k, oo in enumerate(outs[1:]):
        if oo[0] != 'K' or oo[1] != nfr: raise Fail(f'shift run {k}: {oo[:3]} vs {nfr}')
        sv = list(map(int, oo[4:]))
        if len(sv) != len(base): raise Fail(f'token count depends on huge #{k}: {len(base)} vs {len(sv)}; from {fr} {rle(T)}')
        for p, (u, v) in enumerate(zip(base, sv)):
            if u != v:
                if (v - u) % SHIFT: raise Fail(f'non-affine dependence pos {p}: {u} {v}')
                c = (v - u) // SHIFT
                rho = hs[k] % MLIT
                coef, const = res[p] if isinstance(res[p], tuple) else ({}, u)
                coef = dict(coef); coef[k] = c; res[p] = (coef, const - c * rho)
    out = []
    for x in res:
        if isinstance(x, tuple):
            coef, const = x
            out.append(Huge(sum(c * hs[k] for k, c in coef.items()) + const))
        else:
            out.append(x)
    return ('K', nfr, int(o[2]), out)
def rle(T):
    out = []
    for x in T:
        if out and out[-1][0] == x: out[-1][1] += 1
        else: out.append([x, 1])
    return ' '.join(f'{x}' if c == 1 else f'{x}^{c}' for x, c in out)
def follow(b0, log=None, verbose=False, maxj=10**8):
    fr, T = 'G', [1] * 36 + [3 * b0]
    nj = 0; nl = 0
    while nj < maxj:
        if len(T) >= 2:
            E, steps, kind, fp = (clearG if fr == 'G' else clearB)(T)
            if steps > 0:
                nj += 1
                if log:
                    log.write(f'J{nj} {kind} steps={steps} len={len(T)} | {fr} ' + rle(E) + '\n')
                T = E
                continue
        res = literal(fr, T); nl += 1
        if res[0] == 'H':
            if log: log.write(f'HALT {res[1]} hs={res[2]} from {fr} {rle(T)}\n')
            return 'HALT', nj, nl, ' '.join(res[1])
        fr, T = res[1], res[3]
        if log and verbose: log.write(f'  L {res[2]} -> {fr} {rle(T)}\n')
    return 'MAX', nj, nl, None
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('b0', type=int); ap.add_argument('--log'); ap.add_argument('-v', action='store_true')
    ap.add_argument('--maxj', type=int, default=10**8)
    a = ap.parse_args()
    lg = open(a.log, 'w', buffering=1) if a.log else None
    try:
        r = follow(a.b0, lg, a.v, a.maxj)
    except Fail as e:
        r = ('FAIL', str(e)[:3000])
    print(a.b0, *r, flush=True)
    if lg: lg.write(f'RESULT {r}\n'); lg.close()
