"""Exact step counts from the per-rule step formulas (fitted exactly on every literal check in check_rules.json,
see fit_steps.py):
   R1  X(a,b+1,c) -> X(a+4,b,c)   2a+11      R2  X(a,0,c+1) -> X(1,a+4,c)   2a+14
   R3  X(a,0,0)   -> Y(a+8)       2a+21      R4  Y(3k+3) -> X(1,5,k)        2n+26
   R5  Y(3k+10)   -> X(17,3,k)    2n+105     R6  Y(3k+2) -> halting config  2n+5 (steps executed before the
                                                                              undefined C0 transition)
Composite (b_0 = start counter, b_{j+1} = 4 b_j + 5):
   X(1,b,c+1) -> X(1,4b+5,c)  costs 4b^2+17b+16 ;   X(1,b,0) -> Y(4b+9)  costs 4b^2+17b+23.
Closed form with alpha = b_0 + 5/3 and J = number of c-steps (final counter b_J, n' = 4 b_J + 9):
   sum_{j<=J} (4 b_j^2 + 17 b_j + 16) + 7 = 4 alpha^2 (16^(J+1)-1)/15 + 11 alpha (4^(J+1)-1)/9 - 11 (J+1)/9 + 7.
"""
from fractions import Fraction as Fr
import sys


def x_phase(b0, J):
    """Steps from X(1,b0,J) to Y(4 b_J + 9), exact (closed form)."""
    al = Fr(b0) + Fr(5, 3)
    v = 4 * al * al * (16 ** (J + 1) - 1) / 15 + 11 * al * (4 ** (J + 1) - 1) / 9 - Fr(11 * (J + 1), 9) + 7
    assert v.denominator == 1
    return int(v)


def x_phase_sum(b0, J):
    """Same, by direct summation (check of the closed form)."""
    b = b0; t = 0
    for j in range(J):
        t += 4 * b * b + 17 * b + 16; b = 4 * b + 5
    return t + 4 * b * b + 17 * b + 23


def T_YA(k):          # Y(3k+3) -> Y(4 B(k,5) + 9)
    return 2 * (3 * k + 3) + 26 + x_phase(5, k)


def T_YB(m):          # Y(3m+13) -> Y(4 B(m,33) + 9): R5, three R1 (a = 17, 21, 25), R2 (a = 29), X phase
    return 2 * (3 * m + 13) + 105 + 159 + 72 + x_phase(33, m)


if __name__ == '__main__':
    for b0 in (5, 33, 7):
        for J in range(0, 12):
            assert x_phase(b0, J) == x_phase_sum(b0, J)
    # literal step counts measured by `node trajectory.js ymap 1 20 ...` (trajectory_ymap.txt)
    lit = {3: 240, 6: 3187, 9: 49094, 12: 778841, 15: 12435948, 18: 198874495,
           10: 363, 13: 5302, 16: 82729, 19: 1315388}
    for n, s in sorted(lit.items()):
        pred = T_YA(n // 3 - 1) if n % 3 == 0 else T_YB((n - 13) // 3) if n >= 13 else None
        if n == 10:   # Y(10) = Y(3*0+10) -> X(17,3,0) -> X(29,0,0) -> Y(37): R5 + 3 R1 + R3(a=29)
            pred = 2 * 10 + 105 + 159 + (2 * 29 + 21)
        print('Y(%d): literal %d, formula %d  %s' % (n, s, pred, 'ok' if s == pred else 'MISMATCH'))
    # the halting run: blank -> Y(13): 80 ; Y(13) -> Y(141): T_YB(0) ; Y(141) -> Y(N3): T_YA(46) ; ...
    print('blank -> Y(141):', 80 + T_YB(0), '(literal 5382)')
    def B(c, b):
        for _ in range(c): b = 4 * b + 5
        return b
    N3 = 4 * B(46, 5) + 9
    t = 80 + T_YB(0) + T_YA(46)
    print('blank -> Y(N3) exactly: %d steps (%d digits), N3 = %d' % (t, len(str(t)), N3))
    print('Remaining: T_YB(M3) + T_YB(M4) + T_YB(M5) + (2 N6 + 5) [+1 for the halting transition];')
    print('T_YB(m) = (4/15) n\'^2 + O(n\') with n\' = 4 B(m,33) + 9, so steps = (4/15) N6^2 (1 + o(1)) = (3/5) sigma^2 (1 + o(1)).')
