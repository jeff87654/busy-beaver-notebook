"""Mini-follower for 10-state extensions of the BB(8) record: follows the real run from the record's first exhaustion
X(b_f, 35) (b_f = 6 mod 840) through literal stages (stage35.exe) and abstract champion jumps (follow2.jump with
numres residues), replacing every huge accumulator by a small representative of its residue class.

Two runs: A (representatives r = R mod 2520, r >= 19; start b = 6, the real class mod 840) and B (r = R mod 36,
r >= 40; start b = 18).  A list whose length differs between A and B depends on a huge value: clearing it is a full
(omega-level) cycle.  A record-type machine halts (run A) after at least one full cycle; B is a regularity check.
Screening only: representatives are single points (no fitting/validation); verify hits with follow2.py.

  python mf35.py MACHINE [--stages 14] [--maxs 30000000] [-v]
  prints RESULT kind stages=.. cycles=.. | per-stage summary   (kind: HALT, TIME, WIDE, FAIL, MAXSTAGES)"""
from __future__ import annotations
import argparse, os, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import follow2
from follow2 import Aff, Fail, jump
from numres import Num

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
TMP = Path(os.environ.get('CLAUDE_JOB_DIR', tempfile.gettempdir())) / 'tmp'
TMP.mkdir(parents=True, exist_ok=True)
STAGE = str(HERE / 'stage35.exe')


def xword(b, n):
    """X(b, n): the record's configuration at the E0 read after the exhaustion K(0^n; 0; b) (closed form, checked)"""
    L = '101' + '011' * (12 * b + 12)
    return L + '0' + '1110101010101010100' + '101' * n, len(L), 'E'


def word_of_tokens(toks):
    return ''.join('10' * m + '1' for m in toks)


import threading
_LOCAL = threading.local()


def _server():
    sv = getattr(_LOCAL, 'sv', None)
    if sv is None or sv.poll() is not None:
        sv = subprocess.Popen([STAGE, '-s'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                              creationflags=LOW)
        _LOCAL.sv = sv
    return sv


import hashlib
_CACHE = {}          # (word hash, head, state, maxs) -> [(mask, used slot strings, result)]
_CLOCK = threading.Lock()
STATS = {'hit': 0, 'miss': 0}
FIXREP = None      # if set: every huge new accumulator is represented by this r-token value (experiments)
REPSEQ = None      # if set (list): the k-th huge new accumulator is represented by REPSEQ[k] (ordered-size experiments)


def _slots(machine):
    return [q[i:i + 3] for q in machine.split('_') for i in (0, 3)]


def run_stage(machine, word, head, state, maxs, maxw=None, rcap=600):
    """one literal stage; results are cached by input and by the values of the slots the stage actually read"""
    maxw = maxw or (4 * len(word) + 20000)
    key = (hashlib.sha1(word.encode()).digest(), head, state, maxs)
    sl = _slots(machine)
    for mask, vals, out in _CACHE.get(key, ()):
        if all(sl[i] == v for i, v in zip(mask, vals)):
            STATS['hit'] += 1
            return out
    sv = _server()
    sv.stdin.write(f'{machine} {state} {head} {maxs} {maxw} {rcap}\n{word}\n')
    sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    if not _:
        return line
    um = int(u, 16)
    mask = tuple(i for i in range(20) if um >> i & 1)
    with _CLOCK:
        if len(_CACHE) > 60000:
            _CACHE.clear()
        _CACHE.setdefault(key, []).append((mask, tuple(sl[i] for i in mask), out))
    STATS['miss'] += 1
    return out


def rep(x: Num, M, LB):
    if x.exact and x.x <= 2000:
        return x.x
    if x.exact:
        return LB + ((x.x - LB) % M)
    from math import gcd
    m = gcd(x.mod, M)
    r = x.res % m
    v = LB + ((r - LB) % m)
    return v


def follow(machine, mode='A', stages=14, maxs=30_000_000, verbose=False, start=None):
    M, LB, b0 = {'A': (2520, 19, 6), 'B': (72, 40, 30), 'C': (360, 100, 126), 'D': (36, 40, 18), 'F': (360, 100, 6), 'G': (2520, 19, 846), 'H': (36, 40, 6), 'K': (72, 80, 6)}[mode]
    word, head, state = start if start else xword(b0, 35)
    hist = []
    sigs = []
    for s in range(stages):
        out = run_stage(machine, word, head, state, maxs)
        if not out:
            return 'FAIL', hist + ['no output']
        f = out.split()
        if f[0] == 'H':
            hist.append(f'H {f[2]}{f[3]} ones={f[4]}')
            return 'HALT', hist
        if f[0] in ('T', 'W'):
            hist.append(f[0])
            return {'T': 'TIME', 'W': 'WIDE'}[f[0]], hist
        # J step | toks | farbits
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        # tokens nearest-first: [2, r, a, d1, ...] -> entries farthest-first, equal neighbours merged
        digits = toks[3:][::-1]
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[2]), Aff(1)), ('D', Aff(toks[1]), Aff(1))]
        tail = [('D', Aff(2), Aff(1))]
        k = len(digits)
        try:
            items, newp, info = jump(left, tail, {}, 1)
        except (Fail, AssertionError, RuntimeError) as ex:
            hist.append(f'J k={k} JUMPFAIL {ex}')
            return 'FAIL', hist
        vals = {p: (REPSEQ.pop(0) if REPSEQ and not v.exact else FIXREP if FIXREP and not v.exact else rep(v, M, LB)) for p, v in newp.items()}
        new = []
        for e in items:
            if e[0] != 'D':
                hist.append('J non-D item'); return 'FAIL', hist
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 3 and new[-2] > 2000:      # an exact but large accumulator: residue representative
            new[-2] = LB + ((new[-2] - LB) % M)
        # zeros at the event (right before a and r) and the list summary
        nz = 0
        for m in new[:-3][::-1]:
            if m != 1:
                break
            nz += 1
        hist.append(f'J k={k} far={"junk" if far else "clean"} ev={info.get("event")} zeros={nz} '
                    f'r={",".join(str(v) for v in vals.values())}')
        if verbose:
            print(s, hist[-1], 'list:', rle(digits[:12]), '...', rle(digits[-12:]), flush=True)
        word = far + word_of_tokens(new)
        head, state = len(word), 'G'
        # affine-loop detection on the event configurations
        blocks = []
        for m in new:
            if blocks and blocks[-1][0] == m:
                blocks[-1][1] += 1
            else:
                blocks.append([m, 1])
        sigs.append((tuple(b[0] for b in blocks), tuple(b[1] for b in blocks) + (len(far),)))
        p = affine_period(sigs)
        if p:
            hist.append(f'LOOP p={p}')
            return 'LOOP', hist
    return 'MAXSTAGES', hist


def affine_period(sigs, maxp=8, reps=3):
    """smallest p such that the last reps*p event configurations repeat in shape with period p and every count
    changes by the same amount per period"""
    n = len(sigs)
    for p in range(1, maxp + 1):
        if n < (reps + 1) * p:
            break
        ok = True
        for t in range(n - p, n):
            a, b_, c = sigs[t], sigs[t - p], sigs[t - 2 * p]
            d = sigs[t - 3 * p]
            if not (a[0] == b_[0] == c[0] == d[0]):
                ok = False; break
            if any(x - y != y - z or y - z != z - w or x < y for x, y, z, w in zip(a[1], b_[1], c[1], d[1])):
                ok = False; break     # a shrinking count is a countdown, not a loop
        if ok:
            return p
    return 0


def zeros_of(h):
    for w in h.split():
        if w.startswith('zeros='):
            return int(w[6:])
    return None


def big_jumps(hist, thr=50):
    """jumps of run A whose borrow crossed >= thr zero digits (with b = 6 representatives a 12b-type run)"""
    return sum(1 for h in hist if h.startswith('J') and (zeros_of(h) or 0) >= thr)


def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(str(v[i]) + (f'*{j - i}' if j - i > 1 else '')); i = j
    return ' '.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('--stages', type=int, default=14)
    ap.add_argument('--maxs', type=int, default=30_000_000)
    ap.add_argument('-v', action='store_true')
    ap.add_argument('--mode', default='AB')
    a = ap.parse_args()
    res = {}
    for mode in a.mode:
        res[mode] = follow(a.machine, mode, a.stages, a.maxs, a.v)
    # full cycles: stages whose jump list length k differs between A and B
    ka = [h for h in res.get('A', ('', []))[1]]
    kb = [h for h in res.get('B', ('', []))[1]]
    cyc = 0
    for x, y in zip(ka, kb):
        if x.startswith('J') and y.startswith('J') and zeros_of(x) != zeros_of(y):
            cyc += 1
    kind = res['A'][0] if 'A' in res else res['B'][0]
    agree = 'A=B' if ('A' in res and 'B' in res and res['A'][0] == res['B'][0] and len(ka) == len(kb)) else 'A!=B'
    print(f'RESULT {kind} stages={len(ka)} cycles={cyc} {agree} | A: ' + ' ; '.join(ka) + ' || B: ' + ' ; '.join(kb))


if __name__ == '__main__':
    main()
