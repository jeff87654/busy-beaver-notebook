"""fam.py (never_audit): per-family audit helpers on top of lit.exe (literal) and sym.py (symsim, sound symbolic).
All codings are v-codings (1-runs separated by single 0s, head side last); machines with left K-events are mirrored."""
import subprocess, itertools, collections, os, sys, json, time
from fractions import Fraction as Fr
from sym import *

def lit_k(m, q, steps, every=1, tape=None):
    """literal K-trace: list of (step, v(list of int), z) at (q, R) end events of machine m (already oriented)."""
    args = [LIT, 'kv', m, str(steps), q, 'R', str(every)] + ([tape] if tape else [])
    out = subprocess.run(args, capture_output=True, text=True).stdout.splitlines()
    res = []; tail = out[-1] if out else ''
    for l in out:
        if not l or not l[0].isdigit(): continue
        a, z = l.rsplit('|', 1); f = a.split(); st = int(f[0]); v = []
        for t in f[1:]:
            if '*' in t: x, n = t.split('*'); v += [int(x)] * int(n)
            else: v.append(int(t))
        res.append((st, v, int(z)))
    return res, tail

def orient(m, q_side):
    q, side = q_side
    return (mirror(m), q) if side == 'L' else (m, q)

def top_event(m, steps=2000000):
    out = subprocess.run([LIT, 'ends', m, str(steps), '*', '*', '100000000'], capture_output=True, text=True).stdout.splitlines()
    c = collections.Counter(tuple(l.split(' ', 3)[1:3]) for l in out if l[:1].isdigit())
    return c.most_common(6)

def lin_mod(x, env, m):
    """evaluate Lin or int mod m given symbol residues env (mod M with m | M); fractions must clear"""
    if isinstance(x, int): return x % m
    v = x.ev(env)
    assert v.denominator == 1 or (m % 1 == 0), v
    if v.denominator != 1:
        raise ValueError('fraction')
    return int(v) % m

def symenv(sd):
    """parse symsim symbol descriptions ' X0=H5[r5] X1=...[r7]' -> {X0:5,...} (residues mod MG)"""
    env = {}
    for t in sd.split():
        if '=' in t and t.startswith('X') and '[r' in t:
            k = t.split('=')[0]; r = int(t.rsplit('[r', 1)[1].rstrip(']')); env[k] = r
    return env

def expand(v, env=None):
    """expand blocks with constant counts; leaves symbolic blocks"""
    out = []
    for e in v:
        if isinstance(e, tuple):
            n = e[2]
            if n.isconst(): out += list(e[1]) * int(n.const()); continue
        out.append(e)
    return out

def log(msg, f=None):
    f = f or os.path.join(HERE, 'notes.txt')
    with open(f, 'a') as fh: fh.write(time.strftime('%Y-%m-%d %H:%M:%S ') + msg + '\n')

def detect(m0, steps=3000000):
    """find (oriented machine, Q, side, TF, Z, score) for a single-accumulator v-coding: K = [d.., A] + TF at (Q,R), z = Z.
    score = fraction of consecutive K pairs (same length) that are a plain decrement (one digit -1, A grows)"""
    best = None
    for (q, side), cnt in top_event(m0)[:3]:
        mm = mirror(m0) if side == 'L' else m0
        tr, tail = lit_k(mm, q, steps)
        if len(tr) < 50: continue
        for Z in sorted(set(z for s, v, z in tr)):
            ev = [v for s, v, z in tr if z == Z]
            for TF in ([], [1], [2], [3], [4], [1, 1], [2, 2]):
                n = len(TF)
                kk = [v for v in ev if len(v) > n + 1 and v[len(v) - n:] == TF] if n else [v for v in ev if len(v) > 1]
                if len(kk) < 30: continue
                good = tot = 0
                for a, b in zip(kk, kk[1:]):
                    if len(a) != len(b): continue
                    tot += 1
                    da, db = a[:len(a) - n - 1], b[:len(b) - n - 1]
                    diff = [i for i in range(len(da)) if da[i] != db[i]]
                    if len(diff) == 1 and db[diff[0]] == da[diff[0]] - 1 and diff[0] == len(da) - 1 and b[len(b) - n - 1] > a[len(a) - n - 1]: good += 1
                sc = good / max(tot, 1) * min(1, len(kk) / 200)
                if best is None or sc > best[-1]: best = (mm, q, side, TF, Z, sc)
    return best

def detect2(m0, steps=3000000):
    """like detect() but over both codings V and U10; returns (oriented m, Q, side, TF, Z, coding, score)"""
    from coding import VCoding, U10Coding
    best = None
    for (q, side), cnt in top_event(m0)[:3]:
        mm = mirror(m0) if side == 'L' else m0
        tr, tail = lit_k(mm, q, steps)
        if len(tr) < 50: continue
        for cname, C in (('V', VCoding()), ('U10', U10Coding()), ('U10s2', U10Coding(2)), ('U110', U10Coding(1, 2))):
            for Z in sorted(set(z for s, v, z in tr)):
                ev = [v for s, v, z in tr if z == Z]
                for TF in ([], [1], [2], [3], [4], [1, 1], [2, 2], [0, 2], [2, 1], [1, 2]):
                    n = len(TF); kk = []
                    for v in ev:
                        if n and (len(v) <= n or v[len(v) - n:] != TF): continue
                        try: d, tf = C.decode(v, n)
                        except Exception: continue
                        d = [int(x.const()) if hasattr(x, 'const') else x for x in d]
                        if len(d) >= 2: kk.append(d)
                    if len(kk) < 30: continue
                    good = tot = 0
                    for a, b in zip(kk, kk[1:]):
                        if len(a) != len(b): continue
                        tot += 1
                        da, db = a[:-1], b[:-1]
                        diff = [i for i in range(len(da)) if da[i] != db[i]]
                        if len(diff) == 1 and diff[0] == len(da) - 1 and db[-1] == da[-1] - 1 and b[-1] > a[-1]: good += 1
                    sc = good / max(tot, 1) * min(1, len(kk) / 200)
                    if best is None or sc > best[-1]: best = (mm, q, side, TF, Z, cname, sc)
    return best
