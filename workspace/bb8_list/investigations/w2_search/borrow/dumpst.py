"""dumpst.py MACHINE STAGE [--policy std] [--k 17 --n 41 --R 19]: print far bits and tokens at the K-moment of STAGE"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse
from ilib import stage, far_of, word_of, SUF, rle
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('S', type=int); ap.add_argument('--policy', default='std')
ap.add_argument('--k', type=int, default=17); ap.add_argument('--n', type=int, default=41); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--maxs', type=float, default=2e9)
a = ap.parse_args()
def go():
    word = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + SUF
    for st in range(a.S + 1):
        kind, d = stage(a.M, word, int(a.maxs), a.policy)
        if kind != 'K': print(kind, d); return
        if st == a.S:
            print('FAR', d['far']); print('TOKS', rle(d['toks'][:-2]), '|', d['toks'][-2:]); return
        word = d['newword']
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
