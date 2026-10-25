"""rdep.py M WPREFIX s r-list [--S 40]: take the stage-s input word, replace its accumulator token r, follow (ilib) to the
first RSIG / halt; print (c, P, z).  Shows which stage's accumulator feeds the restart counter."""
import sys, threading
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/inplace')
import ilib, lsimpy
from ilib import stage, rsig
from sweep_util import rng
M, pre, s0, rl = sys.argv[1], sys.argv[2], int(sys.argv[3]), rng(sys.argv[4])
S = int(sys.argv[5]) if len(sys.argv) > 5 else 40
def go():
    w = open(f'{pre}_{s0}.txt').read().strip()
    far, t = lsimpy.parse_k(w[:-1])
    for r in rl:
        word = far + lsimpy.word_of(t[:-1] + [r]) + '1010'; out = 'MAX'
        for st in range(S):
            kind, d = stage(M, word, 4 * 10**10, 'std')
            if kind != 'K': out = f'{kind}{d.get("slot","")}@{s0+st}'; break
            g = rsig(d['toks'])
            if g: out = f'RSIG@{s0+st} P={list(g[0])} c={g[1]} z={g[2]}'; break
            word = d['newword']
        print(f's={s0} r={r}: {out}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
