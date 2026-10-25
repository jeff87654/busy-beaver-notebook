"""Closed forms and magnitudes for 1RB1RH_0LC0LF_0RH1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---.
Y(k,n) = 0^inf 10 (1110)^k 11 (10)^n E>.  Y(k+1,n) -> Y(k,9n+13) in D(n) = 120n^2+400n+344 steps;
Y(0,N) -> 0^inf (10)^(3N+7) E> in pre(N) = 12N^2+70N+101 steps; m = 3N+7 odd: -> Y((m-1)/2, 2) in 10j+23 steps;
m even: halt in 10j+25 steps with j = (m-2)/2 and 3j+7 ones.
Blank tape -> Y(0,2) in 29 steps.  F(k,2) = (29*9^k - 13)/8."""
from decimal import Decimal, getcontext
getcontext().prec = 80
def F(k, x=2):
    for _ in range(k): x = 9 * x + 13
    return x
def D(n): return 120 * n * n + 400 * n + 344
def pre(n): return 12 * n * n + 70 * n + 101
steps = 29
k, resets = 0, []
# reset 0 from Y(0,2): N0 = 2
N0 = 2; m0 = 3 * N0 + 7; assert m0 % 2 == 1; k1 = (m0 - 1) // 2
steps += pre(N0) + 10 * k1 + 23
print('reset 0: Y(0,2), N0 = 2, m0 = %d -> Y(%d,2); step %d' % (m0, k1, steps))
N1 = F(k1); assert N1 == (29 * 9**k1 - 13) // 8
steps += sum(D(F(i)) for i in range(k1)) + pre(N1)
m1 = 3 * N1 + 7; assert m1 % 2 == 1; k2 = (m1 - 1) // 2
steps += 10 * k2 + 23
print('reset 1: Y(%d,2) -> Y(0,N1), N1 = %d (N1 mod 4 = %d), m1 = %d -> Y(k2,2), k2 = %d (odd: %s); step %d'
      % (k1, N1, N1 % 4, m1, k2, k2 % 2 == 1, steps))
assert k2 == (87 * 9**k1 + 9) // 16
# reset 2: N2 = F(k2,2) is odd (parity of F(k,2) = parity of k) -> m2 even -> halt
assert F(1) % 2 == 1 and F(2) % 2 == 0
l9 = Decimal(9).log10()
LN2 = Decimal(k2) * l9 + (Decimal(29) / 8).log10()           # log10 N2 (the -13/8 is negligible)
Ls = Decimal(k2) * l9 + (Decimal(261) / 16).log10()          # log10 sigma, sigma = (261*9^k2 + 115)/16
digits = int(Ls) + 1
mant = Decimal(10) ** (Ls - int(Ls))
print('reset 2: Y(k2,2) -> Y(0,N2), N2 = F(k2,2) = (29*9^k2 - 13)/8 odd, m2 = 3N2+7 even -> halt')
print('log10 N2 = %.6f' % LN2)
print('sigma = (261*9^%d + 115)/16 = (9*N2 + 29)/2 ~ %.6fe%d  (%d decimal digits)' % (k2, mant, int(Ls), digits))
print('log10 sigma = %.6f ; log10 log10 sigma = %.6f  => sigma ~ 10^10^%.4f' % (Ls, Ls.log10(), Ls.log10()))
# steps: dominated by the last phase: sum D(n_i) ~ 1.5 N2^2, pre(N2) ~ 12 N2^2 => ~13.5 N2^2 ~ (2/3) sigma^2
Lt = Decimal('13.5').log10() + 2 * LN2
print('steps ~ 13.5*N2^2 ~ 10^%.6f  (~ (2/3) sigma^2 = 10^%.6f)' % (Lt, (Decimal(2) / 3).log10() + 2 * Ls))
print('2^^5 = 2^65536 ~ 10^19728.3 < sigma < 2^^6 ~ 10^10^19727.78 ; 10^^2 = 10^10 < sigma < 10^^3 = 10^10^10')
