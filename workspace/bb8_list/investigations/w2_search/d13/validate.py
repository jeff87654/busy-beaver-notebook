"""validate.py MACHINE [--stages 160] [--big]: robustness screen for a Tier-1 hit.
std: from far_k + [0 1^n|1|19] for (k,n) in {17,29,41} x {41,329} + (17,371) + (17,2849) + (29,371): restarts (c, delta,
stage) and the end (halt slot/stage).  --big: eater only (first restart or halt) for k in {17,77,137}, R = 2539."""
import sys, threading, argparse
from t1lib import run, start_word, far_of, rsig
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--stages', type=int, default=160)
ap.add_argument('--big', action='store_true'); ap.add_argument('--cases', default='')
a = ap.parse_args()
def follow(k, n, pol, S, R0, first_only=False):
    rs = []
    def cb(st, kind, d):
        if kind == 'K':
            s = rsig(d[0][:-2])
            if s and not d[1] and s[1] >= 40 and st > 0:
                rs.append(f'c={s[1]}(d={s[1]-79},%14={s[1]%14})@{st}')
                if first_only: return 1
    kind, st, d, v = run(a.M, start_word([0] + [1] * n + [1, R0], far_of(k)), S, cb=cb, policy=pol, maxs=4 * 10**9)
    end = f'{kind}@{st}' + (f' {d[0]}{d[1]}' if kind == 'H' else '')
    return f'restarts={rs} end={end}'
def go():
    cases = [(17, 41), (29, 41), (41, 41), (17, 329), (29, 329), (41, 329), (17, 371), (29, 371), (17, 2849)]
    if a.cases: cases = [tuple(map(int, c.split(':'))) for c in a.cases.split(',')]
    if not a.big:
        for k, n in cases:
            print(f'std k={k} n={n}: {follow(k, n, "std", a.stages, 19)}', flush=True)
    else:
        for k in (17, 77, 137):
            print(f'big k={k} n=41: {follow(k, 41, "big", 40, 2539, True)}', flush=True)
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(400000)
t = threading.Thread(target=go); t.start(); t.join()
