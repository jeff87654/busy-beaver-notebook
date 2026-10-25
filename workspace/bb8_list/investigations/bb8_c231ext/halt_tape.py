import idle, sys
from tm import *
for M in (C231, C232):
    T, n = parse(M)
    for a, nd in [(7, 2), (8, 2), (9, 3), (10, 20), (11, 20), (12, 20), (21, 20)]:
        r = Run(T, kword(a, [0]*nd), 0, 4)
        h = r.run(10**8)
        lo, hi, L, c, R = r.view()
        ones = sum(r.tape)
        print(M[-6:], a, nd, 'halt' if h else 'nohalt', r.steps, 'ones', ones, 6*a+7, '| state', chr(65+r.q), '|', rle(L), '[', c, ']', rle(R))
