"""Parametric event rules on B-form configurations [L | A] (tape D(L1)..D(Ln) D0 D(A) G>), each checked against the
literal machine (sim.exe, next B-form configuration) on random instances.
   rules.py [NPER] [SEED]"""
import random
import sys
from fw import *

_S = None


def lit(L, A, maxsteps=3 * 10 ** 9):
    global _S
    if _S is None:
        _S = Server(M10, 'Bf', 10 ** 9)
    w, h, q = bword(L, A)
    r = _S.job(w, h, q, maxsteps)
    x = r[-1]
    if x['kind'] == 'BF':
        p = bparse(x['word'], x['rel'])
        return ('B', p[0], p[1], x['step'])
    return (x['kind'], x, None, x.get('step'))


def P6(rng):
    return [6] * rng.randint(0, 4)


def Pany(rng):
    # arbitrary left context: any tokens, ending so that the rule's own tokens are what the scan meets
    return [rng.choice([1, 3, 4, 6, 7, 9, 10, 13]) for _ in range(rng.randint(0, 3))]


def std(rng):
    return 3 * rng.randint(0, 25) + 1


# each rule: name -> (generator(rng) -> (L, A), predictor(L, A) -> (L', A'))
def g_R1(rng):
    t = rng.randint(3, 40); A = rng.randint(0, 60)
    return Pany(rng) + [rng.choice([0, 2, 3, 5, 6, 9])] * rng.randint(0, 1) + [t], A
def p_R1(L, A):
    return L[:-1] + [L[-1] - 3], 2 * A + 8

def g_R2(rng):
    t = rng.randint(3, 40); k = rng.randint(1, 8); A = rng.randint(0, 60)
    return Pany(rng) + [t] + [1] * k, A
def p_R2(L, A):
    j = len(L) - 1
    while L[j] == 1:
        j -= 1
    M = list(L); M[j] -= 3; M[j + 1] = A + 3
    return M, 4

def g_H(rng):
    return [1] * rng.randint(1, 12), std(rng)
def p_H(L, A):
    return [2] + [1] * (2 * A + 4) + [0] + [1] * (len(L) - 1), 6

def g_TL(rng):
    Q = rng.choice([[2], [6] * rng.randint(0, 4) + [9]])
    return Q + [1] * (3 * rng.randint(1, 6)) + [0] + [1] * rng.randint(1, 10), 6
def p_TL(L, A):
    i = L.index(0)
    j = 0
    while L[j] != 1:
        j += 1
    Q = L[:j]; m = i - j; z = len(L) - i - 1
    Q2 = [9] if Q == [2] else Q[:-1] + [6, 9]
    return Q2 + [1] * (m - 3) + [0] + [1] * (z + 2), 6

def g_ED0(rng):
    T = 4 * rng.randint(1, 12) + 1
    A = rng.randint((T - 5) // 2 + 1, (T - 5) // 2 + 30)   # precondition V >= 2
    Y = rng.randint(4, 40)
    return P6(rng) + [Y, T, 0] + [1] * rng.randint(1, 8), A
def p_ED0(L, A):
    i = len(L) - 1 - L[::-1].index(0)
    Y, T = L[i - 2], L[i - 1]; w = len(L) - i - 1
    return L[:i - 2] + [Y - 4, 2, 0, A + 1 - (T - 5) // 2] + [1] * (w + T - 2), 4

def g_S1(rng):
    return [6] * rng.randint(1, 5) + [2, 2, 0, 2] + [1] * rng.randint(1, 10), std(rng)
def p_S1(L, A):
    n = L.index(2); z = len(L) - n - 4
    return [6] * (n - 1) + [3, A + 6, 1, 1, 0] + [1] * z, 6

def g_S2(rng):
    return P6(rng) + [3, rng.randint(3, 60), 1, 1, 0] + [1] * rng.randint(1, 10), 6
def p_S2(L, A):
    i = len(L) - 1 - L[::-1].index(0); z = len(L) - i - 1
    return L[:i - 3] + [L[i - 3] - 3, 8] + [1] * (z + 2), 6

def g_S4(rng):
    return P6(rng) + [3, rng.randint(4, 60), 2, 0, 2] + [1] * rng.randint(1, 10), std(rng)
def p_S4(L, A):
    i = len(L) - 1 - L[::-1].index(0); v = len(L) - i - 2
    return L[:i - 2] + [L[i - 2] - 4, A + 6, 1, 0] + [1] * v, 6

def g_S5(rng):
    return P6(rng) + [3, rng.randint(1, 60), rng.randint(2, 60), 1, 0] + [1] * rng.randint(1, 10), 6
def p_S5(L, A):
    i = len(L) - 1 - L[::-1].index(0); v = len(L) - i - 1
    return L[:i - 2] + [L[i - 2] - 2, 7] + [1] * (v + 1), 4

def g_S6(rng):
    return P6(rng) + [3, rng.randint(3, 60), 2] + [1] * rng.randint(1, 10), std(rng)
def p_S6(L, A):
    j = len(L) - 1
    while L[j] == 1:
        j -= 1
    u = len(L) - j - 1
    return L[:j - 1] + [L[j - 1] - 3, A + 4] + [1] * u, 6


RULES = dict(R1=(g_R1, p_R1), R2=(g_R2, p_R2), H=(g_H, p_H), TL=(g_TL, p_TL), ED0=(g_ED0, p_ED0), S1=(g_S1, p_S1),
             S2=(g_S2, p_S2), S4=(g_S4, p_S4), S5=(g_S5, p_S5), S6=(g_S6, p_S6))


def test(name, n, rng, log=print):
    g, p = RULES[name]
    ok = bad = 0
    for _ in range(n):
        L, A = g(rng)
        exp = p(L, A)
        k, L2, A2, st = lit(L, A)
        if k == 'B' and (L2, A2) == exp:
            ok += 1
        else:
            bad += 1
            if bad <= 5:
                log('  MISMATCH %s: [%s | %d] -> lit %s %s vs rule [%s | %d]' % (
                    name, fmt(L), A, k, ('[%s | %d]' % (fmt(L2), A2)) if k == 'B' else show(L2)[:150], fmt(exp[0]), exp[1]))
    log('%s: %d ok, %d mismatch' % (name, ok, bad))
    return ok, bad


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    names = sys.argv[3].split(',') if len(sys.argv) > 3 else list(RULES)
    for nm in names:
        test(nm, n, rng, log=lambda s: print(s, flush=True))
