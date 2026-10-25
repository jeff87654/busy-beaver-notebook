"""verify_restart.py MACHINE [--ks 2-30] : for each k, follow from far_k + [0 1^n | 1 | R] and report the stage of the
first clean restart (no far bits, tokens '2 5 1^m'), m, and the depth."""
import sys, threading, argparse
from fstep import stage
from sim import far_of, word_of
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--ks', default='2-20')
ap.add_argument('--n', type=int, default=30); ap.add_argument('--R', type=int, default=19); ap.add_argument('--S', type=int, default=80)
ap.add_argument('--policy', default='std'); ap.add_argument('--maxs', type=float, default=1e8)
a = ap.parse_args()
lo, hi = map(int, a.ks.split('-'))
def go():
    for k in range(lo, hi + 1):
        word = far_of(k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
        res = 'MAX'
        for st in range(a.S):
            kind, d = stage(a.machine, word, int(a.maxs), policy=a.policy)
            if kind != 'K':
                res = f'{kind} {d} at {st}'; break
            toks, far, newword, ev, nz, new = d
            dd = toks[:-2]
            if not far and len(dd) > 2 and dd[0] == 2 and dd[1] == 5:
                m = 0
                for x in dd[2:]:
                    if x != 1: break
                    m += 1
                if m >= 20:
                    res = f'CLEAN at {st}: m={m} depth={nz} toks={dd[:3+m][-3:]}..'; break
            word = newword
        print(f'k={k}: {res}', flush=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
