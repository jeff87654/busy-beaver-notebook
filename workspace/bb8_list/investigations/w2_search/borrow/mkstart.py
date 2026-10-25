"""mkstart.py: build a pre-J0 word: crafted round start far + [P 2 5 1^c 0^3 9 1^z|1|1], run n1 (J0 = halt) to the
round-end entry, add KADD to the 2-run there, then run to the last K-moment before the J0 read; save that word.
usage: python mkstart.py --P 31 --c 35 --out st_c7.txt [--kadd 0] [--far p11_far7.txt] [--z 37] [--policy std]
Also: --round1 K,N,R saves the round-1 end word far_K + [0 1^N|1|R] instead."""
import idle  # noqa: F401  (Idle priority)

import sys, threading, argparse, os
from ilib import stage, rle, expand, SUF, N1, far_of, word_of
import mf35
ap = argparse.ArgumentParser(); ap.add_argument('--far', default='p11_far7.txt'); ap.add_argument('--P', default='31')
ap.add_argument('--c', type=int, default=35); ap.add_argument('--z', type=int, default=37); ap.add_argument('--kadd', type=int, default=0)
ap.add_argument('--policy', default='std'); ap.add_argument('--out', required=True); ap.add_argument('--maxs', type=float, default=2e10)
ap.add_argument('--round1', default='')
a = ap.parse_args()
def go():
    if a.round1:
        k, n, R = map(int, a.round1.split(','))
        w = far_of(k) + word_of([0] + [1] * n + [1, R]) + SUF
        open(a.out, 'w').write(w + '\n'); print('round1 word', len(w)); return
    far = open(a.far).read().strip() if os.path.exists(a.far) else a.far
    P = expand(a.P)
    toks = P + [2, 5] + [1] * a.c + [0, 0, 0, 9] + [1] * a.z + [1, 1]
    word = far + mf35.word_of_tokens(toks) + SUF
    added = False; last = None
    for s in range(300):
        kind, d = stage(N1, word, int(a.maxs), a.policy)
        if kind == 'H':
            print('J0 read in stage', s, 'pre-J0 toks:', rle(last[0])[:200] if last else None)
            open(a.out, 'w').write(word + '\n'); return
        if kind != 'K': print('fail', kind); return
        t = d['toks'][:-2]
        if not added and a.kadd:
            L = len(P)
            if t[:L] == P and len(t) > L + 2 and t[L] == 2:
                i = L
                while t[i] == 2: i += 1
                if t[i] == 5:
                    j = i + 1
                    while t[j] == 1: j += 1
                    m = j - i - 1
                    if m < 14 and t[j:j + 2] == [0, 0] and s > 1 and t[j + 2] > 1 and all(v == 1 for v in t[j + 3:]):
                        t2 = P + [2] * (i - L + a.kadd) + t[i:] + d['toks'][-2:]
                        d['newword'] = d['far'] + mf35.word_of_tokens(t2) + SUF; added = True
                        print('entry at stage', s, 'k', i - L, '->', i - L + a.kadd)
        last = (d['toks'][:-2],)
        word = d['newword']
    print('no J0')
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
