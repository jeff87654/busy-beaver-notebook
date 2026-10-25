"""Number theory for huge n1 values: Carmichael lambda, stable power towers, residues of iter d (U n) A."""
from math import gcd
from functools import lru_cache
def factor(m):
    f = {}; p = 2
    while p * p <= m:
        while m % p == 0: f[p] = f.get(p, 0) + 1; m //= p
        p += 1
    if m > 1: f[m] = f.get(m, 0) + 1
    return f
def lcm(a, b): return a // gcd(a, b) * b
@lru_cache(None)
def lam(m):
    if m == 1: return 1
    r = 1
    for p, e in factor(m).items():
        if p == 2: l = 1 if e == 1 else 2 if e == 2 else 2 ** (e - 2)
        else: l = (p - 1) * p ** (e - 1)
        r = lcm(r, l)
    return r
def v2bound(m):
    """exponent e0 such that 2^e mod m is periodic with period lam(m) for e >= e0"""
    e = 0
    while m % 2 == 0: m //= 2; e += 1
    return max(e, 1)
@lru_cache(None)
def tau(m):
    """2^^h mod m for h -> infinity (stable value)"""
    if m == 1: return 0
    l = lam(m); t = tau(l)
    e = t
    while e < v2bound(m) + 64: e += l
    return pow(2, e, m)
def tower_exact(h):
    v = 1
    for _ in range(h): v = 2 ** v
    return v
def stable_height(m):
    """smallest h with 2^^h' = tau(m) mod m for all h' >= h (checked for h' up to h+8 via the recursion)"""
    for h in range(1, 60):
        ok = True
        for hh in range(h, h + 6):
            if tower_mod(hh, m) != tau(m): ok = False; break
        if ok: return h
    raise ValueError
def tower_mod(h, m):
    if m == 1: return 0
    if h <= 4: return tower_exact(h) % m
    l = lam(m)
    e = tower_mod(h - 1, l)
    # 2^^(h-1) >= 65536 >= v2bound for h-1 >= 4
    while e < v2bound(m): e += l
    return pow(2, e, m)
