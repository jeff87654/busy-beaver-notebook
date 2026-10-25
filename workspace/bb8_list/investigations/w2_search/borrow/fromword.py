"""fromword.py M WORDFILE [--S 30] [--policy std]: follow a machine from a saved word; print stages (tokens) and RSIGs."""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse
from ilib import stage, rsig, rle
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('w'); ap.add_argument('--S', type=int, default=30)
ap.add_argument('--policy', default='std'); ap.add_argument('--maxs', type=float, default=1e9); ap.add_argument('--W', type=int, default=200)
ap.add_argument('--q', action='store_true')
a = ap.parse_args()
QS = 'ABCDEFGHIJKLMNOP'
def go():
    word = open(a.w).read().strip()
    for s in range(a.S):
        kind, d = stage(a.M, word, int(a.maxs), a.policy)
        u = d.get('U', 0); sl = ' '.join(QS[i // 2] + str(i % 2) for i in range(32) if (u >> i) & 1 and i >= 18)
        if kind != 'K': print(s, kind, d.get('slot', ''), sl); return
        r = rsig(d['toks'])
        if not a.q or r: print(s, rle(d['toks'][:-2])[:a.W], '|', d['toks'][-2:], 'far', len(d['far']), '[' + sl + ']', ('RSIG P=%s c=%d z=%d' % (rle(list(r[0])), r[1], r[2])) if r else '', flush=True)
        word = d['newword']
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
