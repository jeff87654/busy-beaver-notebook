"""Parametric period rules of n1, checked literally on random instances (both size orders).  Far(k,m) is the far
region produced by P2 from [2^k,5,1^m,0^3,1,P,0,1^w|R]; it must not depend on P, R, w.
   rules_n1.py N SEED [names]"""
import random, sys
from fw import *
from n1sim import literal, flab

FARS = {}


def big_or_small(rng):
    return 40 + 120 * rng.randint(0, 40) if rng.random() < 0.5 else 3 * rng.randint(1, 20) + 1


def g_P1(rng):
    k, m, n = rng.randint(1, 25), rng.randint(7, 60), rng.randint(2, 40)
    return '', [2] * k + [5] + [1] * m + [0, 0, 2] + [1] * n, big_or_small(rng)
def p_P1(far, L, A):
    k = L.index(5); m = L.index(0) - k - 1; n = len(L) - k - m - 4
    return far, [2] * (k + 2) + [5] + [1] * (m - 6) + [0, 0, 0, 1, A + 3] + [1] * n, 6

def g_P2(rng):
    k, m, w = rng.randint(1, 25), rng.randint(7, 60), rng.randint(1, 40)
    P = 40 + 120 * rng.randint(0, 25)        # deep class: = 1 mod 3
    R = big_or_small(rng)
    return '', [2] * k + [5] + [1] * m + [0, 0, 0, 1, P, 0] + [1] * w, R
def p_P2(far, L, R):
    k = L.index(5); m = L.index(0) - k - 1; P = L[-L[::-1].index(0) - 2]; w = len(L) - L.index(P) - 2
    return ('FAR', k, m), [2, R + 1] + [1] * (w + (2 * P + 4) // 3 - 1), 4

def g_P3(rng):
    k, m, w = rng.randint(1, 25), rng.randint(7, 60), rng.randint(1, 40)
    far = getfar(k, m)
    return far, [2, 2] + [1] * w, big_or_small(rng), (k, m)
def p_P3(far, L, A, km):
    k, m = km; w = len(L) - 2
    return '', [2] * (k + 2) + [5] + [1] * (m - 6) + [0, 0, A + 5] + [1] * w, 6

def g_P4(rng):
    k, m, w = rng.randint(1, 25), rng.randint(3, 60), rng.randint(1, 40)
    Q = 42 + 120 * rng.randint(0, 25)        # = F + 2, = 0 mod 3
    return '', [2] * k + [5] + [1] * m + [0, 0, Q, 0] + [1] * w, big_or_small(rng)
def p_P4(far, L, R):
    k = L.index(5); m = L.index(0) - k - 1; Q = L[k + 1 + m + 2]; w = len(L) - (k + 1 + m + 4)
    return '', [2] * k + [5] + [1] * (m - 2) + [0, 0, R + 1] + [1] * (w + 2 * Q // 3 + 1), 4


def getfar(k, m):
    if (k, m) not in FARS:
        L = [2] * k + [5] + [1] * m + [0, 0, 0, 1, 40, 0, 1, 1, 1]
        kind, res, st, evs = literal('', L, 40, 10 ** 10)
        assert kind == 'B', kind
        FARS[(k, m)] = res[0]
    return FARS[(k, m)]


def test(name, n, rng):
    ok = bad = 0
    for _ in range(n):
        if name == 'P3':
            far, L, A, km = g_P3(rng); exp = p_P3(far, L, A, km)
        else:
            far, L, A = globals()['g_' + name](rng); exp = globals()['p_' + name](far, L, A)
        kind, res, st, evs = literal(far, L, A, 10 ** 11)
        good = False
        if kind == 'B':
            f2, L2, A2 = res
            if isinstance(exp[0], tuple):      # P2: far must equal Far(k, m)
                _, k, m = exp[0]
                good = (L2, A2) == (exp[1], exp[2]) and f2 == getfar(k, m)
            else:
                good = (f2, L2, A2) == exp
        ok += good; bad += (not good)
        if not good and bad <= 3:
            print('  MISMATCH', name, flab(far, L, A)[:150], '->', kind, flab(*res)[:150] if kind == 'B' else str(res)[:150], 'exp', exp[1][:12], exp[2], flush=True)
    print('%s: %d ok, %d mismatch' % (name, ok, bad), flush=True)


if __name__ == '__main__':
    n = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]))
    for nm in (sys.argv[3].split(',') if len(sys.argv) > 3 else ['P1', 'P2', 'P3', 'P4']):
        test(nm, n, rng)
