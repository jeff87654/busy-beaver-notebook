"""Closed forms (sympy) for the reset-to-reset step counts of R1 / R2, derived from the literally verified
per-rule step counts (check_R.py):  O: 4a+5 (a odd), D: 4b+8, C2: 8a^2+73a+165, C1 (R1): 8a^2+121a+536,
C0 (R2): 8a+26, and the Z-phase prefixes."""
import sympy as sp
q, i = sp.symbols('q i', integer=True, positive=True)
s2 = lambda a: 8*a**2 + 73*a + 165
s1 = lambda a: 8*a**2 + 121*a + 536
seq = lambda A, i: (A*4**i - 23)/sp.Integer(3)
def tot(prefix, A, m, last):
    # prefix + sum_{i=0}^{m-1} s2(a_i) + last(a_m)
    S = sp.summation(sp.expand(s2(seq(A, i))), (i, 0, m - 1))
    return sp.simplify(sp.expand(prefix + S + last(seq(A, m))))
out = {}
out['R1 ZZ2 (n=6q+2, q>=2)'] = tot(24*q + 259, 104, q - 2, s1)
out['R1 ZZ4 (n=6q+4, q>=2)'] = tot(24*q + 473, 128, q - 2, s1)
out['R2 ZZ4 (n=6q+4, q>=1)'] = tot(24*q + 267, 104, q - 1, lambda a: 8*a + 26)
out['R2 ZZ0 (n=6q,   q>=2)'] = tot(24*q + 447, 110, q - 1, lambda a: 8*a + 26)
for k, v in out.items():
    v2 = sp.nsimplify(sp.expand(sp.powsimp(sp.expand(v.rewrite(sp.exp)), force=True)))
    e = sp.expand(v)
    print(k, ':', e)
    print('   values q=1..5:', [e.subs(q, t) for t in range(1, 6)])
