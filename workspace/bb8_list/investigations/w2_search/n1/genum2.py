"""genum2.py: pruned follower-level lazy TNF enumeration, J0 fixed to one value (-> K), new states K, L[, M].
Leaf kinds: HALT (free slot left undefined), T/W/JF, NOROUND (no Per pattern with m >= MMIN within CUT stages after
the start), MAX.  Rounds: maximal runs of Per detections with x non-decreasing; reported as start-m:end-m:len.
usage: python genum2.py --j0 0LK --ns 2 --k 5 --n 60 --R 19 --stages 45 --cut 18 --out g2_0LK.tsv"""
import sys, threading, argparse, time
from fstep import stage
from sim import far_of, word_of
from per import per_m
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
ap = argparse.ArgumentParser()
ap.add_argument('--j0', required=True); ap.add_argument('--ns', type=int, default=2)
ap.add_argument('--k', type=int, default=5); ap.add_argument('--n', type=int, default=60); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--stages', type=int, default=45); ap.add_argument('--cut', type=int, default=18); ap.add_argument('--mmin', type=int, default=20)
ap.add_argument('--maxs', type=float, default=5e6); ap.add_argument('--out', required=True)
ap.add_argument('--startword', default=None)
a = ap.parse_args()
NEW = 'KLMN'[:a.ns]

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

def rounds(hist):
    rs = []; cur = None
    for s, toks in hist:
        for x, m, z in per_m(toks):
            if cur and x >= cur[3] and m <= cur[2]:
                cur[2] = m; cur[3] = x; cur[4] += 1; cur[5] = s
            else:
                if cur: rs.append(cur)
                cur = [s, m, m, x, 1, s]
    if cur: rs.append(cur)
    return rs

fo = open(a.out, 'w'); nodes = [0]; t0 = time.time()
def leaf(sl, kind, st, hist, extra=''):
    rs = rounds(hist)
    rd = ' '.join(f'{r[0]}-{r[5]}:{r[1]}>{r[2]}:x{r[3]}:n{r[4]}' for r in rs)
    best = max([r[4] for r in rs if r[1] >= a.mmin] + [0])
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{best}\t{extra}\t{rd}\n'); fo.flush()

def dfs(sl, word, st, hist):
    nodes[0] += 1
    M = mstr(sl)
    while st < a.stages:
        if st >= a.cut and not any(m >= a.mmin for s, toks in hist for x, m, z in per_m(toks)):
            leaf(sl, 'NOROUND', st, hist); return
        kind, d = stage(M, word, int(a.maxs))
        if kind == 'H':
            q, sym, steps, ones = d
            slot = f'{q}{sym}'
            leaf(sl, 'HALT', st, hist, f'{slot} ones={ones}')
            if q in 'J' + NEW and slot not in sl:
                for o in options(sl):
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, st, list(hist))
            return
        if kind != 'K':
            leaf(sl, kind, st, hist, (str(d)[:60] if d else '')); return
        toks, far, newword, ev, nz, new = d
        hist.append((st, toks))
        word = newword; st += 1
    leaf(sl, 'MAX', st, hist)

def go():
    w = a.startword or (far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010')
    dfs({'J0': a.j0}, w, 0, [])
    print('nodes', nodes[0], 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
