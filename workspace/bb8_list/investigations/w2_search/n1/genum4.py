"""genum3.py: lazy TNF search for a CLEAN-RESTART gadget: J0 + new states (K, L[, M]) such that from every test start
far_k + [0 1^n | 1 | R] (k in KS) the follower reaches, within S stages, a K-moment with NO far bits whose token list
starts '2 5 1^m' with m >= MMIN (n1's own round start; the no-far world gives m = 4R+3).
A node fails at the first test that ends otherwise (T/W/JF/MAX, or a HALT on a free slot that is then branched).
usage: python genum3.py --ns 2 --ks 5,2,3,4,6,7,8,9,10,11 --n 30 --R 19 --S 40 --out g3.tsv [--j0 0LK]"""
import sys, threading, argparse, time
from fstep import stage
from sim import far_of, word_of
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
ap = argparse.ArgumentParser()
ap.add_argument('--ns', type=int, default=2); ap.add_argument('--ks', default='5,2,3,4,6,7,8,9,10,11')
ap.add_argument('--n', type=int, default=30); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--S', type=int, default=40); ap.add_argument('--mmin', type=int, default=50)
ap.add_argument('--maxs', type=float, default=5e6); ap.add_argument('--out', required=True)
ap.add_argument('--j0', default=None); ap.add_argument('--stuck', type=int, default=8); ap.add_argument('--broad', action='store_true')
a = ap.parse_args()
NEW = 'KLMN'[:a.ns]
KS = [int(x) for x in a.ks.split(',')]

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

from per import per_m
def clean(toks, far):
    if a.broad:
        return any(m >= a.mmin for x, m, z in per_m(toks))
    if far: return False
    d = toks[:-2]
    if len(d) < 3 or d[0] != 2 or d[1] != 5: return False
    m = 0
    for x in d[2:]:
        if x != 1: break
        m += 1
    return m >= a.mmin

fo = open(a.out, 'w'); nodes = [0]; t0 = time.time(); stats = {}
def rec(sl, kind, ti, st, extra=''):
    stats[kind] = stats.get(kind, 0) + 1
    if kind in ('PASS',) or ti >= 2:
        fo.write(f'{mstr(sl)}\t{kind}\t{ti}\t{st}\t{extra}\n'); fo.flush()

def dfs(sl):
    nodes[0] += 1
    if nodes[0] % 200 == 0:
        print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    for ti, k in enumerate(KS):
        word = far_of(k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
        ok = False; lastfar = None; same = 0
        for st in range(a.S + 3 * k):
            kind, d = stage(M, word, int(a.maxs))
            if kind == 'H':
                q, sym, steps, ones = d
                slot = f'{q}{sym}'
                if q in 'J' + NEW and slot not in sl:
                    rec(sl, 'BRANCH', ti, st, slot)
                    for o in options(sl):
                        if slot == 'J0' and a.j0 and o != a.j0: continue
                        s2 = dict(sl); s2[slot] = o
                        dfs(s2)
                    return
                rec(sl, 'HALT', ti, st, slot); return
            if kind != 'K':
                rec(sl, kind, ti, st); return
            toks, far, newword, ev, nz, new = d
            if clean(toks, far):
                ok = True; break
            if far and far == lastfar:
                same += 1
                if same >= a.stuck:
                    rec(sl, 'STUCK', ti, st); return
            else:
                same = 0; lastfar = far
            word = newword
        if not ok:
            rec(sl, 'MAX', ti, a.S + 3 * k); return
    rec(sl, 'PASS', len(KS), 0)

sys.setrecursionlimit(100000); threading.stack_size(64 * 1024 * 1024)
def go():
    dfs({'J0': a.j0} if a.j0 else {})
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
t = threading.Thread(target=go); t.start(); t.join()
