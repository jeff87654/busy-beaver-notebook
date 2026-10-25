"""t12enum.py: lazy TNF enumeration of n1 + J0 + 2 new states (K, L) WITHOUT the in-place left limit (by default),
at the real depth class.  Copied from inplace/ienum.py; changes: --noleft (default on), absolute leftmost visited (lo)
and leftmost CHANGED (mw) cells recorded per RSIG and per leaf, --seed restricts the first branched slot's value
(one K0 subtree per run, for a resumable queue).
Start: far_k + [0 1^n | 1 | R] (default k=29, n=323, R=19; real k1 and depth are 29 mod 42, h14verify addendum).
Leaves: HALT (undefined slot read; then branch), T, W, JF, MAX, NORS, NOEND, RS<maxrs>, LEFT (only with --left).
Output tsv: machine kind stage nRS rsigs extra; rsig = stage:P<len>:c<c>:z<z>:lo<lo>:mw<mw>
usage: python t12enum.py --j0 0RK --seed 0RL --out tree.tsv"""
import idle  # noqa: F401  (Idle priority, correct HANDLE types)
import sys, threading, argparse, time
from ilib import stage, rsig, far_of, word_of, N1, SUF
ap = argparse.ArgumentParser()
ap.add_argument('--j0', required=True); ap.add_argument('--ns', type=int, default=2)
ap.add_argument('--k', type=int, default=29); ap.add_argument('--n', type=int, default=323); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--cut', type=int, default=50)
ap.add_argument('--left', action='store_true'); ap.add_argument('--lch', type=int, default=8); ap.add_argument('--lvs', type=int, default=4)
ap.add_argument('--maxs', type=float, default=2e7); ap.add_argument('--out', required=True); ap.add_argument('--fix', default='')
ap.add_argument('--seed', default=''); ap.add_argument('--maxrs', type=int, default=3); ap.add_argument('--maxnodes', type=int, default=10**9)
a = ap.parse_args()
NEW = 'KLMN'[:a.ns]
BIG = 1 << 60

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
    rss = ' '.join(f'{s}:P{len(P)}:c{c}:z{z}:lo{lo}:mw{mw}' for s, P, c, z, lo, mw in rs)
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{len(rs)}\t{rss}\t{extra}\n'); fo.flush()

def dfs(sl, word, A, st, rs, minlo, minmw, depth):
    nodes[0] += 1
    if nodes[0] > a.maxnodes: return
    if nodes[0] % 200 == 0:
        print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    ll = -A - a.lch if a.left else -BIG
    while True:
        last = rs[-1][0] if rs else 0
        lim = last + (a.cut + 6 * rs[-1][2] // 14 if rs else a.cut)
        if st > lim:
            leaf(sl, 'NORS' if not rs else 'NOEND', st, rs, f'lo={minlo} mw={minmw}'); return
        kind, d = stage(M, word, int(a.maxs), ll=(-A - a.lch if a.left else -BIG), lvs=a.lvs)
        if d.get('LO') is not None: minlo = min(minlo, A + d['LO'])
        if d.get('MW') is not None and d['MW'] < 10**17: minmw = min(minmw, A + d['MW'])
        if kind == 'H':
            slot = d['slot']
            leaf(sl, 'HALT', st, rs, f'{slot} lo={minlo} mw={minmw}')
            if (slot[0] == 'J' or slot[0] in NEW) and slot not in sl:
                opts = options(sl)
                if depth == 0 and a.seed:
                    opts = [o for o in opts if o in a.seed.split(',')]
                for o in opts:
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, A, st, list(rs), minlo, minmw, depth + 1)
            return
        if kind != 'K':
            leaf(sl, 'LEFT' if kind == 'L' else kind, st, rs, f'lo={minlo} mw={minmw}'); return
        r = rsig(d['toks'])
        if r and st > 0 and r[1] >= 6 and (not rs or st - rs[-1][0] > 3):
            rs.append((st, r[0], r[1], r[2], minlo, minmw))
            if len(rs) >= a.maxrs:
                leaf(sl, f'RS{len(rs)}', st, rs, f'lo={minlo} mw={minmw}'); return
        A += d['shift']; word = d['newword']; st += 1

def go():
    import os
    hold = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hold')
    while os.path.exists(hold): time.sleep(20)   # 'hold' file: pause the queue between subtrees
    w = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + SUF
    sl0 = {'J0': a.j0}
    for kv in filter(None, a.fix.split(',')):
        k_, v_ = kv.split('='); sl0[k_] = v_
    dfs(sl0, w, 0, 0, [], 0, BIG, 0)
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(128 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
