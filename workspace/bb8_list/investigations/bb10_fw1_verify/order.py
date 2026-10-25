"""Literal confirmation of the period-internal order with realistic sizes (transit << token):
from the S6 input [6^n, 3, C, 2, 1 | A''] (one zero, so the D9 clearing is a depth-0 R1-run: A''' = 88) the machine
does S6 -> R2 (deposit 9) -> D9 consumed (A''' = 88) -> unpack of D(A''+1) with transit 89 -> exhausted -> HALT.
Prints the B-forms met and the outcome.   order.py A''1,A''2,..."""
import sys
from fw import *
srv = Server(M10, 'Bf', 1)
for App in [int(x) for x in sys.argv[1].split(',')]:
    for n, C in [(1, 152), (3, 5192)]:
        L, A = [6] * n + [3, C, 2, 1], App
        seq = []
        for _ in range(10):
            w, h, q = bword(L, A)
            x = srv.job(w, h, q, 10 ** 12)[-1]
            if x['kind'] != 'BF':
                it, idx, off = tokpos(x['word'], x['rel'])
                seq.append('%s step %d (%s%d), prefix intact %s, tail %s' % (x['kind'], x['step'], x['q'], x['c'],
                           it[:n + 2] == [6] * n + [3, C - 3], fmt(it[idx:])[:80]))
                break
            L, A = bparse(x['word'], x['rel'])
            seq.append('[%s | %d]' % (fmt([t if t < 10 ** 4 or t == App + 1 or t == App + 4 else -1 for t in L]), A))
        print("A''=%d n=%d C=%d:" % (App, n, C), ' -> '.join(seq), flush=True)
srv.close()
