"""genum5.py: follower-level lazy TNF enumeration aimed at Tier 1 (rounds then halt), any restart type.
Start: the follower's own stage-37 input of n1 at b0 = 6 (far_17 + [0 1^329 | 1 | 19]) unless --k/--n given.
Period signature (n1's 6-stage period): a K-moment 'P 2^x 5 1^m 0^2 45 1^z'; a CHAIN is a sequence of signatures
with the same prefix P, x -> x+4, m -> m-14.  Leaf kinds HALT/T/W/JF/MAX/NOROUND (no signature with m >= MMIN
within CUT stages of the start or of the last chain end).
usage: python genum5.py --j0 0LK --ns 2 --stages 120 --out g5_0LK.tsv"""
import sys, threading, argparse, time
from fstep import stage
from sim import far_of, word_of
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
ap = argparse.ArgumentParser()
ap.add_argument('--j0', required=True); ap.add_argument('--ns', type=int, default=2)
ap.add_argument('--k', type=int, default=17); ap.add_argument('--n', type=int, default=329); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--stages', type=int, default=120); ap.add_argument('--cut', type=int, default=30); ap.add_argument('--mmin', type=int, default=20)
ap.add_argument('--maxs', type=float, default=2e7); ap.add_argument('--out', required=True); ap.add_argument('--fix', default='')
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

def sig(toks):
    """'P 2^x 5 1^m 0 0 45 1^z | a r' -> (P, x, m, z) or None"""
    d = toks[:-2]
    z = 0
    while z < len(d) and d[len(d) - 1 - z] == 1: z += 1
    i = len(d) - 1 - z
    if i < 3 or d[i] != 45 or d[i-1] != 0 or d[i-2] != 0: return None
    j = i - 3; m = 0
    while j >= 0 and d[j] == 1: m += 1; j -= 1
    if j < 0 or d[j] != 5: return None
    j -= 1; x = 0
    while j >= 0 and d[j] == 2: x += 1; j -= 1
    if x == 0: return None
    return (tuple(d[:j+1]), x, m, z)

def chains(sigs):
    """sigs: list of (stage, P, x, m, z); returns list of chains [start_stage, end_stage, m0, m_end, length, z0, z_end]"""
    out = []; cur = None
    for s, P, x, m, z in sigs:
        if cur and P == cur[7] and x == cur[8] + 4 and m == cur[3] - 14:
            cur[1] = s; cur[3] = m; cur[4] += 1; cur[6] = z; cur[8] = x
        else:
            if cur: out.append(cur)
            cur = [s, s, m, m, 1, z, z, P, x]
    if cur: out.append(cur)
    return out

fo = open(a.out, 'w'); nodes = [0]; t0 = time.time(); stats = {}
def leaf(sl, kind, st, sigs, extra=''):
    stats[kind] = stats.get(kind, 0) + 1
    ch = chains(sigs)
    good = [c for c in ch if c[4] >= 2]
    cs = ' '.join(f'{c[0]}-{c[1]}:m{c[2]}>{c[3]}:L{c[4]}:z{c[5]}>{c[6]}:P{len(c[7])}' for c in ch if c[4] >= 2)
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{len(good)}\t{extra}\t{cs}\n'); fo.flush()

def dfs(sl, word, st, sigs, lastact):
    nodes[0] += 1
    if nodes[0] % 200 == 0:
        print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    while st < a.stages:
        if st - lastact > a.cut:
            leaf(sl, 'NOROUND', st, sigs); return
        kind, d = stage(M, word, int(a.maxs))
        if kind == 'H':
            q, sym, steps, ones = d
            slot = f'{q}{sym}'
            leaf(sl, 'HALT', st, sigs, f'{slot} ones={ones}')
            if q in 'J' + NEW and slot not in sl:
                for o in options(sl):
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, st, list(sigs), lastact)
            return
        if kind != 'K':
            leaf(sl, kind, st, sigs, (str(d)[:60] if d else '')); return
        toks, far, newword, ev, nz, new = d
        sg = sig(toks)
        if sg and sg[2] >= 6:
            sigs.append((st,) + sg); lastact = st
        word = newword; st += 1
    leaf(sl, 'MAX', st, sigs)

def go():
    w = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
    sl0 = {'J0': a.j0}
    for kv in filter(None, a.fix.split(',')):
        k_, v_ = kv.split('='); sl0[k_] = v_
    dfs(sl0, w, 0, [], 0)
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
