"""rtab.py M: round-end class table.  From a crafted round start far + [P 2 5 1^c 0^3 9 1^z | 1 | 1] follow until the
next RSIG (round start), a halt, or S stages.  Reports the next (P', c', z') and the stage count.
usage: python rtab.py M --far FILE|BITS --P '19' --cs 35-48 [--z 37] [--policy std] [--S 200] [--v]"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, os
from ilib import stage, rsig, rle, expand, SUF
import mf35
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--cs', default='35-48'); ap.add_argument('--step', type=int, default=1)
ap.add_argument('--z', type=int, default=37); ap.add_argument('--P', default='19'); ap.add_argument('--Ps', default='')
ap.add_argument('--policy', default='std'); ap.add_argument('--bigk', type=int, default=1)
ap.add_argument('--S', type=int, default=200); ap.add_argument('--maxs', type=float, default=1e9); ap.add_argument('--far', default='')
ap.add_argument('--v', action='store_true'); ap.add_argument('--ctrim', type=int, default=0)
a = ap.parse_args()
far = open(a.far).read().strip() if a.far and os.path.exists(a.far) else a.far
def one(P, c):
    toks = expand(P) + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = far + mf35.word_of_tokens(toks) + SUF
    A = 0; lo = 0
    last = None
    for s in range(a.S):
        kind, d = stage(a.machine, word, int(a.maxs), a.policy, a.bigk, ctrim=a.ctrim)
        if d.get('LO') is not None: lo = min(lo, A + d['LO'])
        if kind != 'K':
            return f'{kind}{d.get("slot","")}@{s}', lo, last
        if a.v: print('   ', s, rle(d['toks'][:-2])[:200], 'far', len(d['far']), flush=True)
        last = rle(d['toks'][:-2])[:200]
        if s > 3:
            rs = rsig(d['toks'])
            if rs:
                return f'RS@{s} P=[{rle(list(rs[0]))}] c={rs[1]} (m14={rs[1]%14}) z={rs[2]} far={len(d["far"])}', lo, None
        A += d['shift']; word = d['newword']
    return 'MAX', lo, last
def go():
    lo_, hi_ = map(int, a.cs.split('-'))
    Ps = a.Ps.split(',') if a.Ps else [a.P]
    for P in Ps:
        for c in range(lo_, hi_ + 1, a.step):
            r, lo, last = one(P, c)
            print(f'P=[{P}] c={c} (m14={c%14}): {r} LO={lo}' + (f' last: {last}' if last else ''), flush=True)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
