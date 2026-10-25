"""Parametric rules of M3J's specials, each checked literally on random instances (both size orders).
   rules_j.py N SEED [names]"""
import random, sys
from fw import *

_S = None


def lit(L, A, maxsteps=3 * 10 ** 10):
    global _S
    if _S is None:
        _S = Server(M10, 'Bf', 1)
    w, h, q = bword(L, A)
    x = _S.job(w, h, q, maxsteps)[-1]
    if x['kind'] == 'BF':
        p = bparse(x['word'], x['rel']); return 'B', p[0], p[1], x
    return x['kind'], None, None, x


def pairs(a, b, k):
    return [a, b] * k


def rngA(rng):
    return rng.choice([rng.randint(1, 30) * 3 + 1, 40 + 120 * rng.randint(0, 6)])


def P9(rng):
    return [9] * rng.randint(1, 4)


# --- stage 0 ---
def g_TL5(rng):
    Q = rng.choice([[2], [9] * rng.randint(0, 4) + [12]])
    return Q + [1] * (5 * rng.randint(1, 4) + 4) + [0] + [1] * rng.randint(1, 10), 6
def p_TL5(L, A):
    i = L.index(0); j = 0
    while L[j] != 1:
        j += 1
    Q = L[:j]; m = i - j; z = len(L) - i - 1
    Q2 = [12] if Q == [2] else Q[:-1] + [9, 12]
    return Q2 + [1] * (m - 5) + [0] + [1] * (z + 2), 6

def g_TLE(rng):
    return [9] * rng.randint(0, 5) + [12, 1, 1, 1, 1, 0] + [1] * rng.randint(1, 10), 6
def p_TLE(L, A):
    j = L.index(12); z = len(L) - j - 6
    return L[:j] + [9, 11] + [1] * (z + 2), 6

# --- after the first clearing ---
def g_Sa(rng):
    return [9] * rng.randint(1, 5) + [8, 0] + [1] * rng.randint(1, 10), rngA(rng)
def p_Sa(L, A):
    j = L.index(8); z = len(L) - j - 2
    return L[:j - 1] + [5, 3, 0, 3, A + 1] + [1] * (z + 2), 6

def g_Sb(rng):
    X = 4 * rng.randint(3, 60) + 2
    return P9(rng) + [5, 3, 0, 3, X, 0] + [1] * rng.randint(1, 10), rngA(rng)
def p_Sb(L, A):
    j = L.index(5); X = L[j + 4]; w = len(L) - j - 6
    return L[:j] + [2, 7, 0, 0, 3, 3] + pairs(0, 3, (X - 10) // 4) + [0, A + 1] + [1] * (w + 2), 6

def g_Sc(rng):
    X = 4 * rng.randint(2, 80) + 2
    return P9(rng) + [2, 7, 0, 0, 3, 3] + pairs(0, 3, rng.randint(2, 12)) + [0, X, 0] + [1] * rng.randint(2, 10), rngA(rng)
def p_Sc(L, A):
    i = len(L) - 1 - L[::-1].index(0); X = L[i - 1]; w = len(L) - i - 1
    # L[..i-2] ends with (0 3)^m; drop the last two pairs, then 0 0 5 (1 0)^((X-4)/2) 0 1 (A+3) 1 0
    head = L[:i - 2 - 4]
    return head + [0, 0, 5] + pairs(1, 0, (X - 4) // 2) + [0, 1, A + 3, 1, 0] + [1] * (w - 1), 6

def g_Sd(rng):
    Y = rngA(rng) + 3
    return P9(rng) + [2, 7, 0, 0, 3, 3, 0, 3, 0, 0, 5] + pairs(1, 0, rng.randint(10, 40)) + [0, 1, Y, 1, 0] + [1] * rng.randint(1, 10), 6
def p_Sd(L, A):
    i = len(L) - 1 - L[::-1].index(0); w = len(L) - i - 1
    Y = L[i - 2]
    head = L[:i - 4]          # ... (1 0)^p
    return head[:-18] + [0, 1, 4, 1, 1, 1, 0, 3, 0, Y + 8, 0] + [1] * (w + 2), 6

def g_Se(rng):
    Y = 4 * rng.randint(3, 60) + 3
    return P9(rng) + [2, 7, 0, 0, 3, 3, 0, 3, 0, 0, 5, 1, 0, 1, 0, 0, 1, 4, 1, 1, 1, 0, 3, 0, Y, 0] + [1] * rng.randint(1, 10), 6
def p_Se(L, A):
    i = len(L) - 1 - L[::-1].index(0); Y = L[i - 1]; w = len(L) - i - 1
    head = L[:i - 8]          # ends with ... 0, 1  (before 4 1 1 1 0 3 0 Y 0)
    return head + [1, 7, 1, 1, 0, 3, 3] + pairs(0, 3, (Y - 11) // 4) + [0, 7] + [1] * (w + 2), 6

def g_Sf(rng):
    return P9(rng) + [2, 7, 0, 0, 3, 3] + pairs(0, 3, rng.randint(2, 12)) + [0, 4, 0] + [1] * rng.randint(2, 10), rngA(rng)
def p_Sf(L, A):
    i = len(L) - 1 - L[::-1].index(0); w = len(L) - i - 1
    head = L[:i - 6]
    return head + [0, 0, 5, 0, 1, A + 3, 1, 0] + [1] * (w - 1), 6

def g_Sg(rng):
    Y = rngA(rng) + 3
    return P9(rng) + [2, 7, 0, 0, 3, 3] + pairs(0, 3, rng.randint(1, 10)) + [0, 0, 5, 0, 1, Y, 1, 0] + [1] * rng.randint(3, 10), 6
def p_Sg(L, A):
    i = len(L) - 1 - L[::-1].index(0); w = len(L) - i - 1; Y = L[i - 2]
    head = L[:i - 7]          # ... (0 3)^n
    return head[:-1] + [2, 1, 1, Y, 1, 1, 1, 1, 0, 0, 9] + [1] * (w - 2), 4

def g_Sh(rng):
    Y = rngA(rng) + 3
    return P9(rng) + [2, 7, 0, 0, 3, 3, 0, 3, 0, 2, 1, 1, Y, 1, 1, 1, 1, 0, 0, 0] + [1] * rng.randint(1, 10), rngA(rng)
def p_Sh(L, A):
    i = len(L) - 1 - L[::-1].index(0); w = len(L) - i - 1
    return L[:i - 6] + [1, 0, 1, A + 1] + [1] * (w + 1), 4


RULES = dict(TL5=(g_TL5, p_TL5), TLE=(g_TLE, p_TLE), Sa=(g_Sa, p_Sa), Sb=(g_Sb, p_Sb), Sc=(g_Sc, p_Sc), Sd=(g_Sd, p_Sd),
             Se=(g_Se, p_Se), Sf=(g_Sf, p_Sf), Sg=(g_Sg, p_Sg), Sh=(g_Sh, p_Sh))


def test(name, n, rng):
    g, p = RULES[name]
    ok = bad = 0
    for _ in range(n):
        L, A = g(rng)
        exp = p(L, A)
        k, L2, A2, x = lit(L, A)
        if k == 'B' and (L2, A2) == exp:
            ok += 1
        else:
            bad += 1
            if bad <= 3:
                print('  MISMATCH %s: [%s | %d] -> %s vs rule [%s | %d]' % (name, fmt(L), A, ('[%s | %d]' % (fmt(L2), A2)) if k == 'B' else show(x)[:150], fmt(exp[0]), exp[1]), flush=True)
    print('%s: %d ok, %d mismatch' % (name, ok, bad), flush=True)


if __name__ == '__main__':
    n = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]))
    for nm in (sys.argv[3].split(',') if len(sys.argv) > 3 else RULES):
        test(nm, n, rng)
