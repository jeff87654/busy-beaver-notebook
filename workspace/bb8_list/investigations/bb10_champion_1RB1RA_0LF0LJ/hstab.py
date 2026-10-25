import sys
import modexact as E
K = int(sys.argv[1]) if len(sys.argv) > 1 else 10
E.setK(K)
prev = None
for j in range(0, 80):
    hj = E.hmap(j)
    r, p, q = E.orbit(j)
    distinct = len(set(hj))
    x = E.res(E.Xj(j))
    print(j, 'T', E.T[j], 'orbit pre/per', p, q, 'distinct values', distinct, 'X mod M', x, 'same as prev' if hj == prev else '')
    prev = hj
