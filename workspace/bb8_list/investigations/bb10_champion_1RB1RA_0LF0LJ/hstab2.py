import sys
import modexact as E
for K in (4, 8, 12, 16, 20, 24):
    E.setK(K)
    prev = None
    for j in range(0, 12):
        hj = E.hmap(j)
        E.orbit(j)
        if hj == prev:
            break
        prev = hj
    r, p, q = E.orbit(j)
    print('K=%d: h_j constant from j=%d on (h_%d == h_%d); distinct values %d; orbit pre/per %d/%d; '
          'U_j(even) = %d, U_j(odd) = %d mod 2^K; X_j = %d' % (K, j - 1, j, j - 1, len(set(hj)), p, q, hj[0], hj[1], E.res(E.Xj(j))))
