"""enumD.py (from enum12.py): START = [far_K] + [PRE.. 2 5 1^c 0^3 9 1^z|1|R] (default PRE = 100, K = 0): the
class-12 end BORROWS 3 from the prefix digit D; does a gadget restart class 12 in place keeping D-3 as the prefix?
Leaf DDEC = RSIG whose prefix contains D-d (1<=d<=12); followed to MAXRS round starts (prefix digit sequence logged).
Original enum12 doc: lazy TNF enumeration of n1 + J0 + NS new states AT A CLASS-12 ROUND END that re-meets an old far region.
Start: far_K + [2 5 1^c 0^3 9 1^z | 1 | R] (class-12 counter c), followed with n1 to its J0 read at the old far tail
(abs 5K+22).  Gadget slots are branched lazily.  Every round-start signature (RSIG) is recorded with the far region's
leading D2 count kD2 and whether the far REST (bits after the D2 run) equals the original 44-bit tail.
Leaf kinds: EAT (RSIG with kD2 < K), KEEP (RSIG, kD2 == K), HALT/T/W/JF/NORS, ...; after an EAT-RSIG in class 12 the
machine is followed to MAXRS round starts.  Output tsv: machine kind stage rsigs(st:kD2:tailok:Plen:c:z) extra
usage: python enum12.py --out X.tsv [--ns 2] [--K 29 --c 40 --z 29 --R 19] [--fix J0=..,K0=..]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading, argparse, time, ctypes
from fl import stage, rsig, far_of, word_of, N1, SUF, FAR_TAIL
from farfol import fark
import mf35
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
ap = argparse.ArgumentParser()
ap.add_argument('--ns', type=int, default=2); ap.add_argument('--K', type=int, default=0); ap.add_argument('--pre', default='100'); ap.add_argument('--c', type=int, default=40)
ap.add_argument('--z', type=int, default=29); ap.add_argument('--R', type=int, default=19); ap.add_argument('--cut', type=int, default=30)
ap.add_argument('--maxs', type=float, default=5e7); ap.add_argument('--out', required=True); ap.add_argument('--fix', default='')
ap.add_argument('--maxrs', type=int, default=4); ap.add_argument('--maxnodes', type=int, default=10**9); ap.add_argument('--j0', default=''); ap.add_argument('--eatby', type=int, default=15)
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

RID = {FAR_TAIL: 0}
def rid(r):
    if r not in RID:
        RID[r] = len(RID); open(a.out + '.rest', 'a').write('%d %s' % (RID[r], r) + chr(10))
    return RID[r]
fo = open(a.out, 'a'); nodes = [0]; t0 = time.time(); stats = {}
def leaf(sl, kind, st, rs, extra=''):
    stats[kind] = stats.get(kind, 0) + 1
    rss = ' '.join(f'{s}:{kd}:{rid(tok)}:{".".join(map(str, P[-6:]))}:{c}:{z}' for s, kd, tok, P, c, z in rs)
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{rss}\t{extra}\n'); fo.flush()

ST0 = [0]; PRE0 = [int(x) for x in a.pre.split(',')] if a.pre else []
def dfs(sl, word, st, rs, minmw):
    nodes[0] += 1
    if nodes[0] > a.maxnodes: return
    if nodes[0] % 500 == 0:
        print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    while True:
        last = rs[-1][0] if rs else 0
        lim = (last + a.cut + 6 * rs[-1][4] // 14) if rs else ST0[0] + a.cut
        if st > lim:
            leaf(sl, 'NORS' if not rs else 'NOEND', st, rs, f'mw={minmw}'); return
        if not rs and st > ST0[0] + a.eatby and minmw >= 5 * a.K:
            leaf(sl, 'NOEAT', st, rs, f'mw={minmw}'); return
        kind, d = stage(M, word, int(a.maxs))
        if d.get('MW') is not None and d['MW'] < 10**17: minmw = min(minmw, d['MW'])
        if kind == 'H':
            slot = d['slot']
            if (slot[0] == 'J' or slot[0] in NEW) and slot not in sl:
                leaf(sl, 'HALT', st, rs, f'{slot} mw={minmw}')
                for o in options(sl):
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, st, list(rs), minmw)
            else:
                leaf(sl, 'HALTX', st, rs, f'{slot}')
            return
        if kind != 'K':
            leaf(sl, kind, st, rs, f'mw={minmw}'); return
        if st > ST0[0] + 2 and PRE0 and not any(max(PRE0) - 12 <= t < max(PRE0) for t in d['toks'][:-2]):
            leaf(sl, 'DGONE', st, rs, f'mw={minmw}'); return
        r = rsig(d['toks'])
        if r and r[1] >= 6 and (not rs or st - rs[-1][0] > 3):
            kd, rest = fark(d['far'])
            rs.append((st, kd, rest[:400], r[0], r[1], r[2]))
            D0 = max(PRE0) if PRE0 else 0
            ok = any(D0 - 12 * len(rs) <= t < D0 for t in r[0])
            if not ok or len(rs) >= a.maxrs or r[1] % 14 != a.c % 14:
                leaf(sl, ('DDEC%d' % len(rs)) if ok else ('DKEEP' if D0 in r[0] else 'RS'), st, rs, f'mw={minmw}'); return
        word = d['newword']; st += 1

def go():
    PRE = [int(x) for x in a.pre.split(',')] if a.pre else []
    w = (far_of(a.K) if a.K else '') + mf35.word_of_tokens(PRE + [2, 5] + [1] * a.c + [0, 0, 0, 9] + [1] * a.z + [1, a.R]) + SUF
    st = 0
    while True:   # n1 stages up to the J0 read
        kind, d = stage(N1, w, int(a.maxs))
        if kind != 'K': break
        w0 = w; w = d['newword']; st += 1
    print('J0 stage', st, kind, d.get('slot'), flush=True); ST0[0] = st
    sl0 = {}
    for kv in filter(None, a.fix.split(',')):
        k_, v_ = kv.split('='); sl0[k_] = v_
    if a.j0:
        sl0['J0'] = a.j0; dfs(sl0, w, st, [], 10**18)
    else:
        for o in options(sl0):
            s2 = dict(sl0); s2['J0'] = o; dfs(s2, w, st, [], 10**18)
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
