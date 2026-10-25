"""bscan.py: follow machines from far_k + [0 1^n|1|R] (or a crafted round start) and record every RSIG with its FULL
prefix P; flag prefix digits that are decremented (borrowed) across consecutive rounds.
usage: python bscan.py --ms FILE (one machine per line, first tsv field) [--k 29 --n 323 --R 19] [--S 300] [--out X.tsv]
Output tsv: machine, outcome, nRS, maxrun (longest chain of consecutive borrows of one prefix digit), rsig list."""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, time
from ilib import stage, rsig, far_of, word_of, SUF, rle, expand
import mf35
ap = argparse.ArgumentParser(); ap.add_argument('--ms', required=True); ap.add_argument('--k', type=int, default=29)
ap.add_argument('--n', type=int, default=323); ap.add_argument('--R', type=int, default=19); ap.add_argument('--S', type=int, default=300)
ap.add_argument('--maxs', type=float, default=5e7); ap.add_argument('--out', default='bscan.tsv'); ap.add_argument('--policy', default='std')
ap.add_argument('--maxrs', type=int, default=12)
a = ap.parse_args()

def borrow_chain(rs):
    """longest run of consecutive RSIG pairs in which the prefix keeps a digit x (>= 3) that is x-3 in the next
    prefix (aligned from the LEFT end of P = far side); returns (maxrun, list of decremented values)"""
    best = 0; cur = 0; hist = []
    for i in range(len(rs) - 1):
        P, Q = rs[i][1], rs[i + 1][1]
        hit = None
        for j in range(min(len(P), len(Q))):
            if P[j] >= 3 and Q[j] == P[j] - 3 and all(P[t] == Q[t] for t in range(j)):
                hit = (j, P[j]); break
        if hit: cur += 1; hist.append(hit)
        else: cur = 0
        best = max(best, cur)
    return best, hist

def run(M):
    word = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + SUF
    rs = []; out = 'MAX'; st = 0
    for st in range(a.S):
        kind, d = stage(M, word, int(a.maxs), a.policy)
        if kind != 'K':
            out = f'{kind}{d.get("slot", "")}@{st}'; break
        r = rsig(d['toks'])
        if r and r[1] >= 6 and (not rs or st - rs[-1][0] > 3):
            rs.append((st, list(r[0]), r[1], r[2]))
            if len(rs) >= a.maxrs: out = 'NRS'; break
        word = d['newword']
    return out, rs

def go():
    ms = [l.split('\t')[0].strip() for l in open(a.ms) if l.strip()]
    import os
    done = set(l.split('	')[0] for l in open(a.out)) if os.path.exists(a.out) else set()
    ms = [m for m in ms if m not in done]
    fo = open(a.out, 'a'); t0 = time.time()
    for i, M in enumerate(ms):
        out, rs = run(M)
        mr, hist = borrow_chain(rs)
        rss = ' '.join(f'{s}:[{rle(P) if len(P) < 12 else rle(P[:3]) + "..(" + str(len(P)) + ").." + rle(P[-3:])}]:c{c}:z{z}' for s, P, c, z in rs)
        fo.write(f'{M}\t{out}\t{len(rs)}\t{mr}\t{hist}\t{rss}\n'); fo.flush()
        if mr >= 2: print('HIT', M, out, mr, hist, rss[:300], flush=True)
        if i % 20 == 0: print(i, len(ms), '%.0fs' % (time.time() - t0), flush=True)
    print('DONE', len(ms), '%.0fs' % (time.time() - t0))
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
