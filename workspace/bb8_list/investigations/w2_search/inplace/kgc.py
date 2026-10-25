"""kgc.py M --normal 0-21 --special 22-25 [--ks 17,29,41] [--kmax 4] [--policy std]: k-gram contexts (consecutive
slot reads, kgram.exe) of follower stages from far_k + [0 1^n|1|19]; prints the grams that occur in the special stage
range (for the first k) but in NO normal-range stage of any k (candidate clone-split hooks)."""
import sys, os, subprocess, threading, argparse
from ilib import stage, far_of, word_of, SUF
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--normal', default='0-21'); ap.add_argument('--special', default='22-25')
ap.add_argument('--ks', default='17,29,41'); ap.add_argument('--kmax', type=int, default=4); ap.add_argument('--policy', default='std')
ap.add_argument('--n', type=int, default=41); ap.add_argument('--extra', default='')
a = ap.parse_args()
def kg(M, word):
    p = subprocess.run([os.path.join(HERE, 'kgram.exe'), M, 'G', str(len(word)), str(4 * 10**9), 'G', SUF, '1', str(a.kmax), '600'],
                       input=word, capture_output=True, text=True, creationflags=0x40)
    L = p.stdout.splitlines(); d = {}
    for l in L[1:]:
        _, k, g, c, f = l.split(); d[(int(k), g)] = int(c)
    return L[0] if L else 'none', d
def rng(s): x, y = map(int, s.split('-')); return range(x, y + 1)
def go():
    N = {}; S = {}
    nr, sr = rng(a.normal), rng(a.special)
    for i, k in enumerate(map(int, a.ks.split(','))):
        word = far_of(k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
        for st in range(max(max(nr), max(sr)) + 1):
            if st in nr or (i == 0 and st in sr):
                end, d = kg(a.M, word)
                tgt = N if st in nr else S
                for g, c in d.items(): tgt.setdefault(g, []).append((k, st, c))
            kind, dd = stage(a.M, word, 10**9, a.policy)
            if kind != 'K': print('stop', k, st, kind); break
            word = dd['newword']
        print('k', k, 'normal grams', len(N), flush=True)
    for kk in range(2, a.kmax + 1):
        u = sorted((g, v) for g, v in S.items() if g[0] == kk and g not in N)
        print(f'k={kk}: {len(u)} special-only grams')
        for g, v in u[:40]: print('   ', g[1], v[:4])
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
