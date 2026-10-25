"""try14_verify.py CANDS: strict kept-digit check for the 14-state borrow search.
For each candidate (bfilter2 output), compute the first RSIG from the three class-12 starts
d = 31, 37, 43.  KEEP: nearest digit x == d-3 at all three, identical prefix shape after
replacing x, identical counter.  SLOPE1: x increases by 6 per step, same shape and counter.
Everything else is reported as dec/const/irreg/none."""
import idle  # noqa: F401

import sys, threading, argparse
from ilib import stage, rsig, rle

STARTS = [('st_c12_k21.txt', 31), ('st_c12_k21_d37.txt', 37), ('st_c12_k21_d43.txt', 43)]
ap = argparse.ArgumentParser(); ap.add_argument('cands'); ap.add_argument('--S', type=int, default=8)
a = ap.parse_args()

def first_rs(M, w):
    for s in range(a.S):
        try:
            kind, d = stage(M, w, 3 * 10**7)
        except Exception as ex:
            print('err', M, str(ex)[:80], flush=True); return None
        if kind != 'K': return None
        r = rsig(d['toks'])
        if r and r[1] >= 6: return list(r[0]), r[1], r[2]
        w = d['newword']
    return None

def near(P):
    idx = [v for v in P if v >= 3]
    return idx[-1] if idx else None

def shape(P, x):
    return ['X' if v == x else v for v in P]

def go():
    sts = [(open(f).read().strip(), dd) for f, dd in STARTS]
    seen = set()
    for l in open(a.cands):
        x = l.split()
        if len(x) < 2: continue
        M = x[1]
        if M in seen: continue
        seen.add(M)
        res = [first_rs(M, w) for w, dd in sts]
        if any(r is None for r in res):
            print('none', M, [None if r is None else near(r[0]) for r in res], flush=True); continue
        xs = [near(r[0]) for r in res]
        cs = [r[1] for r in res]
        shapes = [shape(r[0], v) for r, v in zip(res, xs)]
        same_shape = shapes[0] == shapes[1] == shapes[2]
        same_c = cs[0] == cs[1] == cs[2]
        if xs == [28, 34, 40] and same_shape and same_c:
            tag = 'KEEP'
        elif xs[1] - xs[0] == 6 and xs[2] - xs[1] == 6 and same_shape and same_c:
            tag = 'SLOPE1'
        elif xs[2] < xs[0]:
            tag = 'dec'
        elif len(set(xs)) == 1:
            tag = 'const'
        else:
            tag = 'irreg'
        print(tag, M, xs, cs, [rle(r[0])[:80] for r in res], flush=True)

sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
