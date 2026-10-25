"""benum.py: lazy TNF enumeration of the J0 gadget (J0 + NS new states K, L, M) from a saved pre-J0 word (mkstart.py).
Each node is followed with the follower; branching only on undefined gadget slots that are actually read.  Leaves:
RS (first round-start signature after the J0 read: P, c, z recorded), HALT (base slot / exhausted), T/W/JF/MAX.
Output tsv: machine  kind  stage  P  c  z  note
usage: python benum.py --start st_c7_k9.txt --ns 2 --out be_c7.tsv [--j0 1RK] [--S 12] [--fix K0=1RC]"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, time
from ilib import stage, rsig, rle, N1
ap = argparse.ArgumentParser(); ap.add_argument('--start', required=True); ap.add_argument('--ns', type=int, default=2)
ap.add_argument('--out', required=True); ap.add_argument('--j0', default=''); ap.add_argument('--S', type=int, default=12)
ap.add_argument('--maxs', type=float, default=3e7); ap.add_argument('--fix', default=''); ap.add_argument('--policy', default='std')
ap.add_argument('--maxnodes', type=int, default=10**9)
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
def leaf(sl, kind, st, P='', c='', z='', note=''):
    stats[kind] = stats.get(kind, 0) + 1
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{P}\t{c}\t{z}\t{note}\n'); fo.flush()
def dfs(sl, word, st):
    nodes[0] += 1
    if nodes[0] > a.maxnodes: return
    if nodes[0] % 500 == 0: print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    while st < a.S:
        kind, d = stage(M, word, int(a.maxs), a.policy)
        if kind == 'H':
            slot = d['slot']
            if (slot == 'J0' or slot[0] in NEW) and slot not in sl:
                for o in options(sl):
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, st)
            else:
                leaf(sl, 'HALT', st, note=slot)
            return
        if kind != 'K':
            leaf(sl, kind, st); return
        r = rsig(d['toks'])
        if r and r[1] >= 6:
            leaf(sl, 'RS', st, rle(list(r[0])), r[1], r[2]); return
        word = d['newword']; st += 1
    leaf(sl, 'MAX', st)
def go():
    w = open(a.start).read().strip()
    sl0 = {}
    if a.j0: sl0['J0'] = a.j0
    for kv in filter(None, a.fix.split(',')):
        k_, v_ = kv.split('='); sl0[k_] = v_
    dfs(sl0, w, 0)
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
