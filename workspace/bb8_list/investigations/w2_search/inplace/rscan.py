"""rscan.py MACHINE: from a no-far round start [P 2 5 1^c 0^3 9 1^z | 1 | 1], follow until the next round-start
signature (RSIG) and report c, the next (P', c', z'), stages, and the leftmost visited/changed cell relative to the
start word's first cell.  usage: python rscan.py M --cs 100-160 [--step 14] [--z 95] [--P '78 6'] [--policy std]"""
import sys, threading, argparse
from ilib import stage, rsig, rle, expand, SUF
import mf35
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--cs', default='100-160'); ap.add_argument('--step', type=int, default=1)
ap.add_argument('--z', type=int, default=95); ap.add_argument('--P', default=''); ap.add_argument('--policy', default='std')
ap.add_argument('--S', type=int, default=400); ap.add_argument('--maxs', type=float, default=1e8); ap.add_argument('--far', default='')
ap.add_argument('--verbose', action='store_true')
a = ap.parse_args()
def one(c):
    toks = expand(a.P) + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = a.far + mf35.word_of_tokens(toks) + SUF
    A = 0; lo = 0; mw = 10**18
    for s in range(a.S):
        kind, d = stage(a.machine, word, int(a.maxs), a.policy)
        if d.get('LO') is not None: lo = min(lo, A + d['LO'])
        if d.get('MW') is not None and d['MW'] < 10**17: mw = min(mw, A + d['MW'])
        if kind != 'K':
            return f'{kind} {d.get("slot","")} at {s}', lo, mw
        if a.verbose: print('   ', s, rle(d['toks'][:-2])[:150], 'far', len(d['far']), 'LO', A + d['LO'], flush=True)
        if s > 0:
            rs = rsig(d['toks'])
            if rs and (s > 3):
                return f'RESTART at {s}: P={list(rs[0])} c={rs[1]} z={rs[2]} far={len(d["far"])}', lo, mw
        A += d['shift']; word = d['newword']
    return 'MAX', lo, mw
def go():
    lo_, hi_ = map(int, a.cs.split('-'))
    for c in range(lo_, hi_ + 1, a.step):
        r, lo, mw = one(c)
        print(f'c={c} (mod14={c%14} mod42={c%42}): {r}  LO={lo} MW={mw}', flush=True)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
