"""sweep.py M --ks 17 --ns 20-60 --Rs 19 [--policy std] [--S 60]: for each (k,n,R) start far_k + [0 1^n|1|R], follow and
report RSIG list (stage:c:z) and the outcome.  Uses ilib as the stage engine."""
import sys, threading, argparse, time
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/inplace')
import ilib
from ilib import stage, rsig, far_of, word_of, SUF
def rng(s):
    out = []
    for part in s.split(','):
        if '-' in part:
            a, b = part.split('-'); st = 1
            if ':' in b: b, st = b.split(':')
            out += list(range(int(a), int(b) + 1, int(st)))
        else: out.append(int(part))
    return out
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--ks', default='17'); ap.add_argument('--ns', default='329')
ap.add_argument('--Rs', default='19'); ap.add_argument('--policy', default='std'); ap.add_argument('--S', type=int, default=60)
ap.add_argument('--maxs', type=float, default=3e9); ap.add_argument('--start', default=None)
a = ap.parse_args()
def run(k, n, R):
    word = far_of(k) + word_of([0] + [1] * n + [1, R]) + SUF
    rs = []
    for st in range(a.S):
        kind, d = stage(a.M, word, int(a.maxs), a.policy)
        if kind != 'K': return f'{kind}{d.get("slot", "")}@{st}', rs
        r = rsig(d['toks'])
        if r and (not rs or st - rs[-1][0] > 3): rs.append((st, len(r[0]), r[1], r[2]))
        word = d['newword']
    return 'MAX', rs
def go():
    for k in rng(a.ks):
        for n in rng(a.ns):
            for R in rng(a.Rs):
                t = time.time(); out, rs = run(k, n, R)
                print(f'k={k} n={n} R={R}: {out} RS={rs} ({time.time()-t:.0f}s)', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
