"""cscan.py MACHINE --cs 23-80 : start from the round-start config [2 5 1^c 0 0 0 9 1^32 | 1 | 1] (no far) and follow
until the next round start / halt / junk; report the outcome per counter c."""
import sys, threading, argparse
from fstep import stage
from nfol import mf35
from per import per_m
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--cs', default='23-80'); ap.add_argument('--S', type=int, default=80)
ap.add_argument('--step', type=int, default=1)
a = ap.parse_args()
lo, hi = map(int, a.cs.split('-'))
def go():
    for c in range(lo, hi + 1, a.step):
        toks = [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * 32 + [1, 1]
        word = mf35.word_of_tokens(toks) + '1010'
        res = 'MAX'; hist = []
        for st in range(a.S):
            kind, d = stage(a.machine, word, 10**8)
            if kind != 'K':
                res = f'{kind} {d} at {st}'; break
            t, far, newword, ev, nz, new = d
            dd = t[:-2]
            if st > 3:
                pm = [p for p in per_m(t) if p[1] >= 6]
                started = [p for p in pm if p[0] == 1]
                if started and (not hist or True):
                    i = dd.index(5) if 5 in dd else 0
                    pre = dd[:max(0, i - 1)]
                    res = f'RESTART at {st}: c2={started[0][1]} depth={nz} far={len(far)} prefix={pre[:8]}'; break
            word = newword
        print(f'c={c} (c mod 14={c % 14}, mod 42={c % 42}): {res}', flush=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
