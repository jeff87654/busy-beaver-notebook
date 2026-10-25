"""rs1.py M --ks .. --ns .. --Rs .. [--policy]: follow to the first RSIG; print stage, far bits, tokens (P, c, z), jump NEW."""
import sys, threading, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/inplace')
import ilib
from ilib import stage, rsig, far_of, word_of, SUF, rle
from sweep_util import rng
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--ks', default='17'); ap.add_argument('--ns', default='329')
ap.add_argument('--Rs', default='19'); ap.add_argument('--policy', default='std'); ap.add_argument('--S', type=int, default=40); ap.add_argument('--bigk', type=int, default=1)
a = ap.parse_args()
def go():
    for k in rng(a.ks):
        for n in rng(a.ns):
            for R in rng(a.Rs):
                word = far_of(k) + word_of([0] + [1] * n + [1, R]) + SUF
                for st in range(a.S):
                    kind, d = stage(a.M, word, 3 * 10**9, a.policy, bigk=a.bigk)
                    if kind != 'K': print(f'k={k} n={n} R={R}: {kind}{d.get("slot","")}@{st} no RSIG', flush=True); break
                    r = rsig(d['toks'])
                    if r:
                        print(f'k={k} n={n} R={R}: st={st} far={d["far"]} P={list(r[0])} c={r[1]} z={r[2]} NEW={rle(d["new"])}', flush=True); break
                    word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
