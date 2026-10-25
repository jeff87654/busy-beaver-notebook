"""nscan.py MACHINE --k 17 --ns 28-40 [--R 19]: restart test over the depth n (and optional R list)."""
import sys, threading, argparse
from fstep import stage
from nfol import run_stage
from sim import far_of, word_of
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--k', type=int, default=17)
ap.add_argument('--ns', default='28-40'); ap.add_argument('--Rs', default='19'); ap.add_argument('--S', type=int, default=60)
a = ap.parse_args()
lo, hi = map(int, a.ns.split('-'))
def go():
    for R in [int(x) for x in a.Rs.split(',')]:
        for n in range(lo, hi + 1):
            word = far_of(a.k) + word_of([0] + [1] * n + [1, R]) + '1010'
            res = 'MAX'; used = 0
            for st in range(a.S):
                out, u = run_stage(a.machine, word, len(word), 'G', 10**8); used |= u
                kind, d = stage(a.machine, word, 10**8)
                if kind != 'K':
                    res = f'{kind} {d} at {st}'; break
                toks, far, newword, ev, nz, new = d
                dd = toks[:-2]
                if not far and len(dd) > 2 and dd[0] == 2 and dd[1] == 5:
                    m = sum(1 for _ in iter(lambda: None, 0)) if False else next((i for i, x in enumerate(dd[2:]) if x != 1), 0)
                    res = f'CLEAN at {st}: m={m} depth={nz}'; break
                word = newword
            slots = ' '.join(f'{"ABCDEFGHIJKLMNOP"[i//2]}{i%2}' for i in range(20, 32) if used >> i & 1)
            print(f'R={R} n={n} (n mod 6 = {n % 6}): {res}  newslots={slots}', flush=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
