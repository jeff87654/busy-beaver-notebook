import sys
from canon import run_from, word_P, word_Q
for kind in 'PQ':
    for r in range(3):
        for a in range(0, 8):
            n = 30 + r
            w = word_P(a, n) if kind == 'P' else word_Q(a, n)
            res = run_from(w, maxsteps=3*10**6)
            print(kind, a, n, res[:4])
