"""jview.py M: follow a crafted round start for S stages and print the loose view (loose.py) of the whole tape word
(far + tokens) at each listed stage output.  usage: python jview.py M --far F --P 19 --c 36 --stages 16,17,18 [--policy big]"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, os
from ilib import stage, rle, expand, SUF
import mf35
from loose import view
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--c', type=int, default=35)
ap.add_argument('--z', type=int, default=37); ap.add_argument('--P', default='19'); ap.add_argument('--stages', default='16,17,18')
ap.add_argument('--far', default=''); ap.add_argument('--policy', default='std'); ap.add_argument('--maxs', type=float, default=1e10)
ap.add_argument('--toks', default='')
a = ap.parse_args()
far = open(a.far).read().strip() if a.far and os.path.exists(a.far) else a.far
want = set(map(int, a.stages.split(',')))
def go():
    toks = expand(a.toks) if a.toks else expand(a.P) + [2, 5] + [1] * a.c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = far + mf35.word_of_tokens(toks) + SUF
    for s in range(max(want) + 1):
        kind, d = stage(a.machine, word, int(a.maxs), a.policy)
        if kind != 'K': print(s, kind, d); return
        if s in want:
            print(s, 'TOKS', rle(d['toks'][:-2])[:300], '| far bits', len(d['far']), flush=True)
            print('   LOOSE', view(d['newword']), flush=True)
        word = d['newword']
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
