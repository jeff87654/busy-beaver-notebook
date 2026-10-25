"""Stable-depth check for a general modulus N (not only powers of 2): h_j constant in j and depending only on parity."""
import sys
import modexact as E
for N in [3, 5, 7, 9, 2 ** 6 * 3 * 5 * 7, 2 ** 8 * 9 * 5 * 7 * 11]:
    E.setK(1)
    E.M = N
    E.K = 0
    prev = None
    try:
        for j in range(0, 14):
            hj = E.hmap(j)
            E.orbit(j)
            if hj == prev:
                break
            prev = hj
        r, p, q = E.orbit(j)
        vals = sorted(set(hj))
        par_only = all(hj[x] == hj[x % 2] for x in range(N))
        print('N=%d: h_j stable from j=%d; values %s; depends only on parity: %s; orbit pre/per %d/%d' %
              (N, j - 1, vals[:4], par_only, p, q))
    except AssertionError as e:
        print('N=%d: assertion %s' % (N, e))
