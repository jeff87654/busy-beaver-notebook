"""rtrace.py M: like rtab for one (P, c) but prints every stage: tokens, far length, gadget slots read (states >= J).
usage: python rtrace.py M --far FILE --P '19' --c 35 [--z 37] [--policy std] [--S 40]"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, os
from ilib import stage, rsig, rle, expand, SUF
import mf35
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--c', type=int, default=35)
ap.add_argument('--z', type=int, default=37); ap.add_argument('--P', default='19'); ap.add_argument('--policy', default='std')
ap.add_argument('--bigk', type=int, default=1); ap.add_argument('--S', type=int, default=40); ap.add_argument('--maxs', type=float, default=1e9)
ap.add_argument('--far', default=''); ap.add_argument('--W', type=int, default=220); ap.add_argument('--toks', default='')
ap.add_argument('--showfar', action='store_true')
a = ap.parse_args()
far = open(a.far).read().strip() if a.far and os.path.exists(a.far) else a.far
QS = 'ABCDEFGHIJKLMNOP'
def slots(u):
    return ' '.join(QS[i // 2] + str(i % 2) for i in range(32) if (u >> i) & 1 and i >= 18)
def go():
    toks = expand(a.toks) if a.toks else expand(a.P) + [2, 5] + [1] * a.c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = far + mf35.word_of_tokens(toks) + SUF
    for s in range(a.S):
        kind, d = stage(a.machine, word, int(a.maxs), a.policy, a.bigk)
        if kind != 'K':
            print(s, kind, d.get('slot', ''), d.get('steps', ''), slots(d.get('U', 0))); return
        rs = rsig(d['toks'])
        print(s, rle(d['toks'][:-2])[:a.W], '| a r', d['toks'][-2:], 'far', len(d['far']), '[' + slots(d['U']) + ']', ('RSIG c=%d' % rs[1]) if rs else '', flush=True)
        if a.showfar: print('   FAR', d['far'][-300:])
        word = d['newword']
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
