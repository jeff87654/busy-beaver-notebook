"""endtab.py: BASE round-end table.  For each counter class r (c = 42 + r), run n1 (J0 = halt) from the crafted round
start far + [P 2 5 1^c 0^3 9 1^z|1|1] to the round-end entry (first K-moment 'P 2^k 5 1^m 0^2 X 1^w' with m < 14),
replace k by each requested k', and follow to the J0 read.  Prints the pre-J0 word in loose/periodic form.
usage: python endtab.py --far F --P 31 --rs 0-13 --ks 9,13,17 [--policy std] [--z 37]"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, os
from ilib import stage, rle, expand, SUF, N1
import mf35
from loose import view
from prle import prle
ap = argparse.ArgumentParser(); ap.add_argument('--far', default=''); ap.add_argument('--P', default='31')
ap.add_argument('--rs', default='0-13'); ap.add_argument('--ks', default=''); ap.add_argument('--policy', default='std')
ap.add_argument('--z', type=int, default=37); ap.add_argument('--maxs', type=float, default=2e10); ap.add_argument('--M', default=N1)
ap.add_argument('--S', type=int, default=60); ap.add_argument('--W', type=int, default=600); ap.add_argument('--base', type=int, default=42)
a = ap.parse_args()
far = open(a.far).read().strip() if a.far and os.path.exists(a.far) else a.far
P = expand(a.P)
def entry(c):
    toks = P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = far + mf35.word_of_tokens(toks) + SUF
    for s in range(200):
        kind, d = stage(a.M, word, int(a.maxs), a.policy)
        if kind != 'K': return None
        t = d['toks'][:-2]
        L = len(P)
        if t[:L] == P and len(t) > L + 2 and t[L] == 2:
            i = L
            while t[i] == 2: i += 1
            k = i - L
            if t[i] == 5:
                j = i + 1
                while t[j] == 1: j += 1
                m = j - i - 1
                if m < 14 and t[j:j + 2] == [0, 0] and s > 1 and len(t) > j + 2 and t[j + 2] > 1 and all(v == 1 for v in t[j + 3:]):
                    return k, t[i:], d['toks'][-2:], d['far'], s
        word = d['newword']
    return None
def go():
    lo, hi = map(int, a.rs.split('-'))
    for r in range(lo, hi + 1):
        c = a.base + r
        e = entry(c)
        if e is None: print(f'r={r} c={c}: no entry'); continue
        k0, rest, ar, far2, s = e
        print(f'r={r} c={c}: entry stage {s} k={k0} rest={rle(rest)[:120]} | {ar}', flush=True)
        ks = [k0 + int(x) for x in a.ks.split(',')] if a.ks else [k0]
        for k in ks:
            toks = P + [2] * k + rest + ar
            word = far2 + mf35.word_of_tokens(toks) + SUF
            last = None; out = 'MAX'
            for st in range(a.S):
                kind, d = stage(a.M, word, int(a.maxs), a.policy)
                if kind != 'K':
                    out = f'{kind}{d.get("slot", "")}@{st}'; break
                last = (rle(d['toks'][:-2]), d['newword']); word = d['newword']
            if last:
                lv = prle(view(last[1][len(far2) - 8:]).split()) if len(last[1]) > len(far2) else ''
                print(f'   k={k}: {out}  preJ0 toks: {last[0][:150]}\n      loose(after far): {lv[:a.W]}', flush=True)
            else:
                print(f'   k={k}: {out}', flush=True)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
