"""j0win.py M STAGES [--policy std] [--W 30] [--maxs 1e8]: for each listed follower stage, run the stage's input word
literally (sim.py) and print the tape window around the head at every J0 read (and the next 12 gadget-state reads)."""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse
from ilib import stage, far_of, word_of, SUF
from sim import Sim
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('stages'); ap.add_argument('--policy', default='std')
ap.add_argument('--W', type=int, default=30); ap.add_argument('--maxs', type=float, default=3e6); ap.add_argument('--n', type=int, default=41)
ap.add_argument('--k', type=int, default=17)
a = ap.parse_args()
want = set(map(int, a.stages.split(',')))
def show(s, tag):
    lo = s.h - a.W; hi = s.h + a.W
    t = ''.join(map(str, s.t[lo:hi]))
    print(flush=True, *[f'   {tag} step={s.steps}: {t[:a.W]}[{s.q}{s.t[s.h]}]{t[a.W+1:]}'])
def go():
    word = far_of(a.k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
    for st in range(max(want) + 1):
        if st in want:
            print('stage', st)
            sm = Sim(a.M, word); cnt = [0]
            def stop(S):
                if S.q == 'J' and S.t[S.h] == 0:
                    show(S, 'J0'); cnt[0] += 1
                elif S.q >= 'K':
                    show(S, S.q + str(S.t[S.h]))
                return cnt[0] > 3
            sm.run(int(a.maxs), stop)
        kind, d = stage(a.M, word, 10**9, a.policy)
        if kind != 'K': print('end', kind); return
        word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
