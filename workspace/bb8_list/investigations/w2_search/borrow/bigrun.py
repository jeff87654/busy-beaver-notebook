"""bigrun.py M [--S 2600] [--k 29 --n 323]: follow M under the BIG policy (no counter trim) from far_k + [0 1^n|1|19];
print every RSIG, every 100th stage summary, and the last 30 stages in full (true-k round ends)."""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse
from ilib import stage, rsig, rle, far_of, word_of, SUF
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--S', type=int, default=2600)
ap.add_argument('--k', type=int, default=29); ap.add_argument('--n', type=int, default=323); ap.add_argument('--maxs', type=float, default=5e10)
a = ap.parse_args()
def go():
    word = far_of(a.k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
    hist = []
    for s in range(a.S):
        kind, d = stage(a.M, word, int(a.maxs), 'big')
        if kind != 'K':
            print(s, kind, d.get('slot', ''), flush=True); break
        t = rle(d['toks'][:-2]); r = rsig(d['toks'])
        line = f'{s} {t[:240]} | far {len(d["far"])}'
        hist.append(line); hist = hist[-40:]
        if r: print('RSIG', s, 'P=', rle(list(r[0]))[:120], 'c=', r[1], 'z=', r[2], flush=True)
        if s % 100 == 0: print(line[:200], flush=True)
        word = d['newword']
    print('--- last stages'); print('\n'.join(hist))
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
