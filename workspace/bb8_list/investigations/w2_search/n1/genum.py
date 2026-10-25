"""genum.py: lazy TNF enumeration of n1 + J0 + new states (K, L[, M]) from a constructed start (default: n1's halting
stage input far_k + [0 1^n | 1 | R]), branching only on free slots actually read; follower stages (literal + jump).
usage: python genum.py --ns 2 --k 5 --n 60 --R 19 --stages 80 --out genum_ns2.tsv"""
import sys, threading, argparse, time
from fstep import stage
from sim import far_of, word_of
from per import per_m
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
ap = argparse.ArgumentParser()
ap.add_argument('--ns', type=int, default=2); ap.add_argument('--k', type=int, default=5)
ap.add_argument('--n', type=int, default=60); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--stages', type=int, default=80); ap.add_argument('--maxs', type=float, default=2e7)
ap.add_argument('--maxnodes', type=int, default=10**6); ap.add_argument('--out', default='genum.tsv')
ap.add_argument('--jzero', default=None, help='fix J0 to this value')
a = ap.parse_args()
NEW = 'KLMN'[:a.ns]
STATES = 'ABCDEFGHIJ' + NEW

def mstr(sl):
    parts = N1.split('_')
    parts[9] = sl.get('J0', '---') + '0LC'
    for q in NEW:
        parts.append(sl.get(q + '0', '---') + sl.get(q + '1', '---'))
    return '_'.join(parts)

def options(sl):
    used = [q for q in NEW if any(v[2] == q for v in sl.values())]
    nxt = [q for q in NEW if q not in used][:1]
    tg = list('ABCDEFGHIJ') + used + nxt
    return [w + d + q for w in '01' for d in 'LR' for q in tg]

def summ(hist):
    """hist entries: (stage, digits+[a,r], event, zeros)"""
    pers = []
    for s, toks, ev, nz in hist:
        for x, m, z in per_m(toks):
            pers.append((s, x, m))
    starts = 0; prev = None
    for s, x, m in pers:
        if prev is None or m > prev:
            starts += 1
        prev = m
    zmax = max([h[3] for h in hist] + [0])
    return pers, starts, zmax

fo = open(a.out, 'w')
nodes = [0]
t0 = time.time()
def leaf(sl, kind, st, hist, extra=''):
    pers, starts, zmax = summ(hist)
    ms = ' '.join(f'{s}:{m}' for s, x, m in pers[:40])
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{starts}\t{zmax}\t{extra}\t{ms}\n'); fo.flush()

def dfs(sl, word, st, hist):
    nodes[0] += 1
    if nodes[0] > a.maxnodes:
        return
    M = mstr(sl)
    while st < a.stages:
        kind, d = stage(M, word, int(a.maxs))
        if kind == 'H':
            q, sym, steps, ones = d
            slot = f'{q}{sym}'
            leaf(sl, 'HALT', st, hist, f'{slot} ones={ones}')
            if q in 'J' + NEW and slot not in sl:
                for o in options(sl):
                    if a.jzero and slot == 'J0' and o != a.jzero: continue
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, st, list(hist))
            return
        if kind != 'K':
            leaf(sl, kind, st, hist, str(d)[:80] if d else ''); return
        toks, far, newword, ev, nz, new = d
        hist.append((st, toks, ev, nz))
        word = newword; st += 1
    leaf(sl, 'MAX', st, hist)

def go():
    w = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
    dfs({}, w, 0, [])
    print('nodes', nodes[0], 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
