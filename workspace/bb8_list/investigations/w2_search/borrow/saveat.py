"""saveat.py M S OUT [--k 29 --n 323]: follow M from far_k + [0 1^n|1|19] (std) and save the far bits of stage S's
output (the K-moment word's far part) to OUT, printing the tokens."""
import idle  # noqa: F401  (Idle priority)
import sys, threading, argparse
from ilib import stage, rle, far_of, word_of, SUF
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('S', type=int); ap.add_argument('out')
ap.add_argument('--k', type=int, default=29); ap.add_argument('--n', type=int, default=323)
a = ap.parse_args()
def go():
    w = far_of(a.k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
    for s in range(a.S + 1):
        kind, d = stage(a.M, w, 10**9)
        if kind != 'K': print('end', kind, d); return
        if s == a.S:
            open(a.out, 'w').write(d['far'] + '\n'); print('far', len(d['far']), 'toks', rle(d['toks'][:-2])[:200], d['toks'][-2:]); return
        w = d['newword']
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
