"""Segment-by-segment literal checks of the real run in the real residue classes.
Deep accumulators are represented by A_deep (mod MOD) representatives; B by B (mod MOD) representatives (small).
   realshape.py MOD"""
import sys
from fw import *
from res import A_deep, B_rec
from rules import p_H, p_TL, p_ED0, p_S1, p_S2, p_S4, p_S5, p_S6, p_R2

srv = Server(M10, 'Bf', 1)
MOD = int(sys.argv[1]) if len(sys.argv) > 1 else 120
ad = A_deep(MOD); br = B_rec(MOD)
okc = badc = 0


def lit(L, A, ms=10 ** 12):
    w, h, q = bword(L, A)
    x = srv.job(w, h, q, ms)[-1]
    if x['kind'] == 'BF':
        p = bparse(x['word'], x['rel']); return 'B', p[0], p[1], x
    return x['kind'], None, None, x


def chk(tag, L, A, exp):
    global okc, badc
    k, L2, A2, x = lit(L, A)
    good = k == 'B' and (L2, A2) == exp
    okc += good; badc += (not good)
    if not good:
        print('  MISMATCH', tag, k, show(x)[:200] if k != 'B' else '[%s | %d]' % (fmt(L2), A2), 'expected [%s | %d]' % (fmt(exp[0]), exp[1]))
    return L2, A2


print('MOD', MOD, 'A_deep rep', ad, 'B rep', br)
# Seg0: record end -> start of the first full cycle, literal through every intermediate B-form
for B in sorted(set([0, 1, 2, 3, br, br + MOD] if br + MOD < 400 else [0, 1, 2, 3, 6, 126])):
    L, A = [1] * 36, 6 * B + 4
    exp = p_H(L, A); L, A = chk('H B=%d' % B, L, A, exp)
    while True:
        i = L.index(0); j = 0
        while L[j] != 1:
            j += 1
        if i - j < 3:
            break
        exp = p_TL(L, A); L, A = chk('TL B=%d' % B, L, A, exp)
    exp = p_ED0(L, A); L, A = chk('ED0(T=9) B=%d' % B, L, A, exp)
    while True:
        j = len(L) - 1
        while L[j] == 1:
            j -= 1
        if L[j] not in (5, 7) or L[-1] != 1:
            break
        exp = p_R2(L, A); L, A = chk('rebuild R2 B=%d' % B, L, A, exp)
    want = [6] * (4 * B + 2) + [2, 2, 0, 2] + [4] * (8 * B + 49) + [7]
    print('Seg0 B=%d: reached [%s | %d]  as derived: %s' % (B, fmt(L)[:80], A, (L, A) == (want, 4)))
# Seg1..Seg5 with constructed deep values
for B in [br, br + MOD, 0, 1]:
    for k in range(3):
        A1 = ad + MOD * (k + 1); A2 = ad + MOD * (k + 2); Ap = ad + MOD * (k + 3); App = ad + MOD * (k + 40) ; Appp = ad + MOD * k
        if Appp == 0: Appp = ad + MOD
        P = [6] * (4 * B + 1)
        # Seg1: S1, S2, first R2 (A=6)
        L, A = [6] * (4 * B + 2) + [2, 2, 0, 2] + [1] * (8 * B + 50), A1
        L, A = chk('S1', L, A, p_S1(L, A)); L, A = chk('S2', L, A, p_S2(L, A)); L, A = chk('R2(A=6)', L, A, p_R2(L, A))
        s1 = (L, A) == (P + [3, A1 + 3, 5, 9] + [1] * (8 * B + 51), 4)
        # Seg2: ED0 with T=5
        L, A = P + [3, A1 + 3, 5, 0] + [1] * (8 * B + 51), A2
        L, A = chk('ED0(T=5)', L, A, p_ED0(L, A))
        s2 = (L, A) == (P + [3, A1 - 1, 2, 0, A2 + 1] + [1] * (8 * B + 54), 4)
        # Seg3: S4, S5
        L, A = P + [3, A1 - 1, 2, 0, 2] + [1] * (8 * B + 54), Ap
        L, A = chk('S4', L, A, p_S4(L, A)); L, A = chk('S5', L, A, p_S5(L, A))
        s3 = (L, A) == (P + [3, A1 - 5, Ap + 4, 7] + [1] * (8 * B + 55), 4)
        # Seg4: S6, R2(A=6)
        L, A = P + [3, A1 - 5, 2] + [1] * (8 * B + 56), App
        L, A = chk('S6', L, A, p_S6(L, A)); L, A = chk('R2(A=6)', L, A, p_R2(L, A))
        s4 = (L, A) == (P + [3, A1 - 8, App + 1, 9] + [1] * (8 * B + 55), 4)
        print('Seg1-4 B=%d k=%d: %s %s %s %s' % (B, k, s1, s2, s3, s4), flush=True)
print('rule checks: %d ok, %d mismatch' % (okc, badc))
