"""The real run after the record, composed from the verified rules (rules.py predictors) and the standard-clearing
macro (esim2.macro: a token x>=3 at depth>=1 is consumed down to x mod 3, accumulator := a fresh deep value).
Deep accumulator values are kept as distinct placeholders (fresh big numbers = 1 mod 3, even); only token positions
and counts are tracked exactly.  chain.py B  (small B; counts are affine in B)"""
import sys
from fw import fmt
from rules import p_H, p_TL, p_ED0, p_S1, p_S2, p_S4, p_S5, p_S6, p_R2

FRESH = [10 ** 6 + 6 * k for k in range(0, 100)]   # placeholders A_k = 10^6+6k: = 1 mod 3, even
fi = 0


def fresh():
    global fi
    fi += 1
    return FRESH[fi]


def clr(L, A, log):
    """standard dynamics in macro form until a special: returns (L, A)."""
    while True:
        t = L[-1]
        if t >= 3:   # R1-run on the first digit
            n = t // 3
            L = L[:-1] + [t % 3]; A = fresh(); log.append('R1-run(%d units)' % n)
            continue
        if t != 1:
            return L, A
        j = len(L) - 1
        while j >= 0 and L[j] == 1:
            j -= 1
        if j < 0 or L[j] < 3:
            return L, A
        if A % 3 != 1:          # one exact R2 (deposit A+3), then continue
            L, A = p_R2(L, A); log.append('R2(nonstd A)'); continue
        depth = len(L) - 1 - j - 1   # zeros nearer than the deposit position
        log.append('CLR(D%d at pos %d, %d units, depth %d -> D%d)' % (L[j], len(L) - j, L[j] // 3, depth, L[j] % 3))
        L = list(L); L[j] = L[j] % 3; A = fresh()


def show(tag, L, A):
    s = fmt([x if x < 10 ** 5 else 'BIG%d' % ((x - 10 ** 6) // 6) for x in L]) if False else None
    out = []
    for x, c in __import__('fw').rle(L):
        k0 = (x - 10 ** 6 + 2) // 6
        t = ('D%d' % x) if x < 10 ** 5 else 'D[A%d%+d]' % (k0, x - (10 ** 6 + 6 * k0))
        out.append(t if c == 1 else '%s^%d' % (t, c))
    k0 = (A - 10 ** 6 + 2) // 6
    a = ('%d' % A) if A < 10 ** 5 else 'A%d%+d' % (k0, A - (10 ** 6 + 6 * k0))
    print('%-28s [%s | %s]' % (tag, ' '.join(out), a))


B = int(sys.argv[1])
A0 = 6 * B + 4
L, A = [1] * 36, A0
show('record end B(2B+1;0^36)', L, A)
L, A = p_H(L, A); show('H', L, A)
k = 0
while True:
    i = L.index(0); j = 0
    while L[j] != 1:
        j += 1
    if i - j < 3:
        break
    L, A = p_TL(L, A); k += 1
show('TL x%d' % k, L, A)
L, A = p_ED0(L, A); show('ED0 (T=9)', L, A)
log = []
while L[-1] == 1 and A == 4:
    j = len(L) - 1
    while L[j] == 1:
        j -= 1
    if L[j] < 3 or (L[j] == 4 and L[j - 1] != 2 and False):
        break
    if L[j] in (5, 7):
        L, A = p_R2(L, A)
    else:
        break
show('rebuild (R2 chain)', L, A)
log = []; L, A = clr(L, A, log); show('first full cycle', L, A); print('   ', log[-2:], len(log), 'macro ops')
for nm, f in [('S1', p_S1), ('S2', p_S2)]:
    L, A = f(L, A); show(nm, L, A)
log = []; L, A = clr(L, A, log); show('R2 + CLR(9)', L, A); print('   ', log)
L, A = p_ED0(L, A); show('ED0 (T=5)', L, A)
log = []; L, A = clr(L, A, log); show('CLR', L, A); print('   ', log)
L, A = p_S4(L, A); show('S4', L, A)
L, A = p_S5(L, A); show('S5', L, A)
log = []; L, A = clr(L, A, log); show('CLR', L, A); print('   ', log)
L, A = p_S6(L, A); show('S6', L, A)
log = []; L, A = clr(L, A, log); show('R2 + CLR(9)', L, A); print('   ', log)
i = len(L) - 1 - L[::-1].index(0)
print('second ED0: T = L[i-1] (=A_S6+1), transit A+1; zeros w2 =', len(L) - i - 1, ' (8B+55 =', 8 * B + 55, ')',
      ' N6 =', L.index(3), '(4B+1 =', 4 * B + 1, ')')
