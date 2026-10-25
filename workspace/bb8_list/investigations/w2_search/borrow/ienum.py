"""ienum.py: lazy TNF enumeration of n1 + J0 + NS new states, screening for IN-PLACE restarts.
Start: round-1 end config far_k + [0 1^n | 1 | R] (default k=17, n=41, R=19), followed with ilib (igstage) and a LEFT
LIMIT: a stage that changes a cell left of abs -LCH or visits left of abs -(LCH+LVS) (abs 0 = the far region's left end)
is a leaf 'LEFT'.  Every round-start signature RSIG (P 2 5 1^c 0^3 9 1^z) is recorded; following continues after a
restart (so round-2 ends are seen).  Leaves: HALT (undefined slot read; then branch), LEFT, T, W, JF, MAX, NORS (no RSIG
within CUT stages of the start / last RSIG + its round length).  Output tsv: machine kind stage nRS rsigs extra
usage: python ienum.py --j0 1RK --ns 3 --out ie_1RK.tsv [--fix K0=0LC,..] [--k 17 --n 41 --R 19]"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, time
from ilib import stage, rsig, far_of, word_of, N1, SUF
import mf35
ap = argparse.ArgumentParser()
ap.add_argument('--j0', required=True); ap.add_argument('--ns', type=int, default=2)
ap.add_argument('--k', type=int, default=17); ap.add_argument('--n', type=int, default=41); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--cut', type=int, default=40); ap.add_argument('--cmin', type=int, default=20)
ap.add_argument('--lch', type=int, default=8); ap.add_argument('--lvs', type=int, default=4)
ap.add_argument('--maxs', type=float, default=2e7); ap.add_argument('--out', required=True); ap.add_argument('--fix', default='')
ap.add_argument('--maxrs', type=int, default=3); ap.add_argument('--maxnodes', type=int, default=10**9)
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

fo = open(a.out, 'w'); nodes = [0]; t0 = time.time(); stats = {}
def leaf(sl, kind, st, rs, extra=''):
    stats[kind] = stats.get(kind, 0) + 1
    rss = ' '.join(f'{s}:P{len(P)}:c{c}:z{z}' for s, P, c, z in rs)
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{len(rs)}\t{rss}\t{extra}\n'); fo.flush()

def dfs(sl, word, A, st, rs, minlo):
    nodes[0] += 1
    if nodes[0] > a.maxnodes: return
    if nodes[0] % 200 == 0:
        print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    while True:
        last = rs[-1][0] if rs else 0
        lim = last + (a.cut + 6 * rs[-1][2] // 14 if rs else a.cut)
        if st > lim:
            leaf(sl, 'NORS' if not rs else 'NOEND', st, rs, f'minlo={minlo}'); return
        kind, d = stage(M, word, int(a.maxs), ll=-A - a.lch, lvs=a.lvs)
        if d.get('LO') is not None: minlo = min(minlo, A + d['LO'])
        if kind == 'H':
            slot = d['slot']
            leaf(sl, 'HALT', st, rs, f'{slot} minlo={minlo}')
            if (slot[0] == 'J' or slot[0] in NEW) and slot not in sl:
                for o in options(sl):
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, A, st, list(rs), minlo)
            return
        if kind != 'K':
            leaf(sl, 'LEFT' if kind == 'L' else kind, st, rs, f'minlo={minlo} MW={d.get("MW")}'); return
        r = rsig(d['toks'])
        if r and st > 0 and r[1] >= 6 and (not rs or st - rs[-1][0] > 3):
            rs.append((st, r[0], r[1], r[2]))
            if len(rs) >= a.maxrs:
                leaf(sl, f'RS{len(rs)}', st, rs, f'minlo={minlo}'); return
        A += d['shift']; word = d['newword']; st += 1

def go():
    w = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + SUF
    sl0 = {'J0': a.j0}
    for kv in filter(None, a.fix.split(',')):
        k_, v_ = kv.split('='); sl0[k_] = v_
    dfs(sl0, w, 0, 0, [], 0)
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
