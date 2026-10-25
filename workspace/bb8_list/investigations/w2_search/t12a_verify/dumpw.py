"""dumpw.py M OUTPREFIX [start options as r2sweep]: follow and save each stage's input word (stage s input -> OUT_s.txt)."""
import sys, threading, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/inplace')
import ilib
from ilib import stage, word_of, SUF, rle, far_of
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('out'); ap.add_argument('--word', default=None)
ap.add_argument('--k', type=int, default=17); ap.add_argument('--n', type=int, default=329); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--S', type=int, default=60); ap.add_argument('--policy', default='std')
a = ap.parse_args()
def go():
    word = open(a.word).read().strip() if a.word else far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + SUF
    for st in range(a.S):
        open(f'{a.out}_{st}.txt', 'w').write(word)
        kind, d = stage(a.M, word, 3 * 10**9, a.policy)
        if kind != 'K': print(st, kind, d.get('slot')); return
        open(f'{a.out}_{st}.k', 'w').write(' '.join(map(str, d['toks'])) + '\n' + d['far'] + '\n')
        word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
