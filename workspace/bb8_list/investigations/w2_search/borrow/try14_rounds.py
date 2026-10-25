"""try14_rounds.py MACHINE [--start WORD] [--policy std|big] [--stages N]: follow quietly and
print every RSIG (round start) with its stage index, prefix, counter and depth.  Used to test
whether a kept-digit candidate borrows the same digit again in round 2."""
import idle  # noqa: F401

import sys, threading, argparse
from ilib import stage, rsig, rle

ap = argparse.ArgumentParser(); ap.add_argument('machine')
ap.add_argument('--start', default='st_c12_k21.txt'); ap.add_argument('--policy', default='std')
ap.add_argument('--stages', type=int, default=400); ap.add_argument('--maxs', type=float, default=3e7)
a = ap.parse_args()

def go():
    w = open(a.start).read().strip()
    for s in range(a.stages):
        kind, d = stage(a.machine, w, int(a.maxs), a.policy)
        if kind != 'K':
            print(s, kind, d.get('slot', ''), flush=True); return
        r = rsig(d['toks'])
        if r:
            print(s, 'RSIG P=', rle(list(r[0])), 'c=', r[1], 'z=', r[2], flush=True)
        w = d['newword']
    print('MAX stages', a.stages)

sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
