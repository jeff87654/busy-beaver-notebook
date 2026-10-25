"""umask.py M S0 S1 [--policy]: slots read (U mask) per stage S0..S1 from far_17 + [0 1^41|1|19]"""
import sys, threading
from ilib import stage, far_of, word_of, SUF, rle
M, s0, s1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); pol = sys.argv[4] if len(sys.argv) > 4 else 'std'
Q = 'ABCDEFGHIJKLMNOP'
def go():
    word = far_of(17) + word_of([0] + [1] * 41 + [1, 19]) + SUF
    for st in range(s1 + 1):
        kind, d = stage(M, word, 10**9, pol)
        u = d['U']; sl = ' '.join(f'{Q[i // 2]}{i % 2}' for i in range(32) if u >> i & 1)
        if st >= s0: print(st, kind, sl, '|', rle(d.get('toks', [])[:-2])[:80])
        if kind != 'K': return
        word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
