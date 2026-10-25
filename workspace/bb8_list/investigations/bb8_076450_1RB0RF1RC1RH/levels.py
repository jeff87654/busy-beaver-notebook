"""Trajectory, sigma and step count from the verified rules (exact integers; no simulation).

Rules (M(p,x,y) = P (0110)^x 1010 (0101)^(y+1) H>0100, L(p,X) = P (0110)^X F>1101, P = p 10101000):
  Init  : blank -> L(1,11)                          1166 steps
  Start : L(p,x+5) -> M(p,x,272)                    317150 steps
  Mstep : M(p,x+3,y) -> M(p,x,36y+452)              5328y^2 + 135536y + 861686 steps
  End1  : M(1,0,y) -> L(11010010,y+8)               72y + 786 steps
  End2  : M(p,2,y) -> halt, sigma = ones(P)+72y+891 5328y^2 + 132872y + 828190 steps
"""
import math, sys
sys.set_int_max_str_digits(0)
from fractions import Fraction as Fr

def y_of(j):          # y after j Mstep's from 272: y_j = (9972*36^j - 452)/35
    v = 9972 * 36 ** j - 452
    assert v % 35 == 0
    return v // 35

def sum_steps(J):
    """sum_{j<J} 5328 y_j^2 + 135536 y_j + 861686, exactly, by geometric sums"""
    g1 = (36 ** J - 1) // 35                  # sum 36^j
    g2 = (36 ** (2 * J) - 1) // (36 ** 2 - 1)  # sum 36^(2j)
    # y_j = (a q^j - b)/35 with a = 9972, b = 452
    a, b = 9972, 452
    s1 = Fr(a * g1 - b * J, 35)
    s2 = Fr(a * a * g2 - 2 * a * b * g1 + b * b * J, 35 * 35)
    tot = 5328 * s2 + 135536 * s1 + 861686 * J
    assert tot.denominator == 1
    return tot.numerator

def log10(n):
    s = str(n) if n < 10 ** 5000 else None
    if s is not None:
        return math.log10(n)
    k = n.bit_length() - 60
    return math.log10(n >> k) + k * math.log10(2)

if __name__ == '__main__':
    # level 1: L(1,11) -> M(1,6,272) -> (2 Msteps) -> M(1,0,y_2)
    assert (11 - 5) % 3 == 0
    J1 = (11 - 5) // 3
    y1 = y_of(J1)
    print('level 1: X = 11, x = 6 = 3*%d + 0, ends at M(1,0,%d)' % (J1, y1))
    X2 = y1 + 8
    x2 = X2 - 5
    J2, r2 = divmod(x2, 3)
    print('level 2: X = %d, x = %d = 3*%d + %d  (prefix 11010010)' % (X2, x2, J2, r2))
    assert r2 == 2 and J2 == 123079
    # generally: y_j = 36 y + 452 = 2 mod 3 for j >= 1, so X2 - 5 = y + 3 = 2 mod 3: End2 applies
    print('y_j mod 3 for j>=1:', {y_of(j) % 3 for j in range(1, 6)})
    yJ = y_of(J2)
    sigma = 72 * yJ + 898          # ones(P) = 7 for P = 11010010 10101000
    steps = (1166 + 317150 + sum_steps(J1) + (72 * y1 + 786)
             + 317150 + sum_steps(J2) + (5328 * yJ * yJ + 132872 * yJ + 828190))
    ls = log10(sigma)
    print('final y = (9972*36^%d - 452)/35, %d digits' % (J2, len(str(yJ))))
    print('sigma = 72y + 898 = (717984*36^%d - 1114)/35' % J2)
    assert sigma * 35 == 717984 * 36 ** J2 - 1114
    print('sigma: %d digits, log10 = %.6f, leading digits %s' % (len(str(sigma)), ls, str(sigma)[:12]))
    print('steps: log10 = %.6f, leading digits %s, %d digits' % (log10(steps), str(steps)[:12], len(str(steps))))
