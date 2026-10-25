"""bverify2.py CANDS --starts f1:d1,f2:d2,... : for each candidate (bfilter2 output) compute the first RSIG from each
start and the nearest prefix digit x (last P entry >= 3).  Flags 'MOVES' when x changes with the start digit d
(a gadget-made constant does not move; a kept or re-rolled d does).  Output one line per machine."""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse
from ilib import stage, rsig, rle
ap = argparse.ArgumentParser(); ap.add_argument('cands'); ap.add_argument('--starts', required=True); ap.add_argument('--S', type=int, default=8)
a = ap.parse_args()
def first_rs(M, w):
    for s in range(a.S):
        kind, d = stage(M, w, 3 * 10**7)
        if kind != 'K': return None
        r = rsig(d['toks'])
        if r and r[1] >= 6: return list(r[0]), r[1], r[2]
        w = d['newword']
    return None
def near(P):
    idx = [v for v in P if v >= 3]
    return idx[-1] if idx else None
def go():
    sts = [(open(f.split(':')[0]).read().strip(), int(f.split(':')[1])) for f in a.starts.split(',')]
    seen = set()
    for l in open(a.cands):
        x = l.split()
        M = x[1]
        if M in seen: continue
        seen.add(M)
        res = [first_rs(M, w) for w, dd in sts]
        xs = [near(r[0]) if r else None for r in res]
        tag = 'MOVES' if None not in xs and len(set(xs)) > 1 else 'const'
        print(tag, M, x[2], xs, [(rle(r[0])[:60], r[1]) if r else None for r in res], flush=True)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
