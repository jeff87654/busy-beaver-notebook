"""tower.py -- stable residues of power towers: tower_res(m) = 2^^h mod m for all sufficiently large h."""
from num import carmichael
from functools import lru_cache


@lru_cache(None)
def tower_res(m):
    if m == 1:
        return 0
    l = carmichael(m)
    e = tower_res(l)
    E = e
    while E < 200:
        E += l
    return pow(2, E, m)


def chain_depth(m):
    d = 0
    while m > 1:
        m = carmichael(m); d += 1
    return d
