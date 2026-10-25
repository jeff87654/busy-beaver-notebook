"""j0lit.py M: build the crafted round start, follow to stage S (follower), then run stage S literally and print the tape
window at every read of a state >= J (gadget/halt-side states).  usage: python j0lit.py M --far F --P 19 --c 36 --S 17"""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, os
from ilib import stage, rle, expand, SUF
import mf35
from sim import Sim
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--c', type=int, default=35)
ap.add_argument('--z', type=int, default=37); ap.add_argument('--P', default='19'); ap.add_argument('--S', type=int, default=17)
ap.add_argument('--far', default=''); ap.add_argument('--W', type=int, default=40); ap.add_argument('--maxs', type=float, default=1e8)
ap.add_argument('--states', default='JK'); ap.add_argument('--max', type=int, default=200); ap.add_argument('--toks', default='')
a = ap.parse_args()
far = open(a.far).read().strip() if a.far and os.path.exists(a.far) else a.far
def go():
    toks = expand(a.toks) if a.toks else expand(a.P) + [2, 5] + [1] * a.c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = far + mf35.word_of_tokens(toks) + SUF
    for s in range(a.S):
        kind, d = stage(a.machine, word, int(a.maxs))
        word = d['newword']
    print('stage', a.S, 'word len', len(word))
    sm = Sim(a.machine, word); base = sm.pad; cnt = [0]
    def stop(S):
        if S.q in a.states:
            lo = S.h - a.W; hi = S.h + a.W
            t = ''.join(map(str, S.t[lo:hi]))
            print(f'  {S.q}{S.t[S.h]} step={S.steps} pos={S.h - base}: {t[:a.W]}[{S.t[S.h]}]{t[a.W+1:]}')
            cnt[0] += 1
        return cnt[0] > a.max
    r = sm.run(int(a.maxs), stop)
    print(r, sm.steps)
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
