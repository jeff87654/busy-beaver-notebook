"""bverify.py: re-test benum/bfilter hits on alternative start words (different prefix digit d): the first RSIG must
keep the alternative borrowed digit (d'-3) nearest.  usage: python bverify.py HITS.txt --starts st_a.txt:34,st_b.txt:40"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse
from ilib import stage, rsig, rle
ap = argparse.ArgumentParser(); ap.add_argument('hits'); ap.add_argument('--starts', required=True); ap.add_argument('--S', type=int, default=16)
a = ap.parse_args()
B = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_'
def first_rs(M, w):
    for s in range(a.S):
        kind, d = stage(M, w, 3 * 10**7)
        if kind != 'K': return None
        r = rsig(d['toks'])
        if r and r[1] >= 6: return list(r[0]), r[1], r[2]
        w = d['newword']
    return None
def go():
    sts = [(f.split(':')[0], int(f.split(':')[1])) for f in a.starts.split(',')]
    words = [(open(f).read().strip(), dd) for f, dd in sts]
    seen = set()
    for l in open(a.hits):
        x = l.split()
        if len(x) < 2: continue
        M = x[1] if x[1].startswith('1RB') else B + x[1]
        if M in seen: continue
        seen.add(M)
        ok = True; res = []
        for w, dd in words:
            r = first_rs(M, w)
            res.append(r)
            if not r: ok = False; continue
            P = r[0]
            if dd not in P: ok = False; continue
            j = len(P) - 1 - P[::-1].index(dd)
            if not all(v < 3 for v in P[j + 1:]): ok = False
        print('PASS' if ok else 'fail', M.replace(B, ''), [(rle(r[0]), r[1], r[2]) if r else None for r in res], flush=True)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
