"""BB(9)-champion rules R1-R3 (Kd orientation, structure right of the head) and the BB(10) champion's R4.
pred(ds, a, b) -> ('K', (ds, a, b)) | ('HALT',) | None (not predicted: R3 boundary region)."""
from kd import *


def tz(ds):
    """number of leading zero digits (nearest the head) = depth of the first nonzero digit"""
    k = 0
    while k < len(ds) and ds[k] == 0:
        k += 1
    return k


def strip(ds):
    ds = list(ds)
    while ds and ds[-1] == 0:
        ds.pop()
    return tuple(ds)


def r4_ch10(b):
    if b % 2 == 1:
        return ('HALT',)
    m, r = divmod(b, 4)
    return ('K', ((1 if r == 0 else 3,) + (0, 0, 3) * m + (0, 0, 2), 0, 0))


def r4_ch9(b):
    if b % 2 == 1:
        return ('HALT',)
    return ('K', ((0, 1) * (b // 2) + (0, 2), 1, 0))


def pred(ds, a, b, r4=r4_ch10):
    ds = list(ds)
    if a >= 1:
        return ('K', (strip(ds), a - 1, b + 3))
    k = tz(ds)
    if k == len(ds):
        return r4(b)
    if k == 0:
        ds[0] -= 1
        return ('K', (strip(ds), b + 2, 1))
    if 2 * k <= b:
        ds[k] -= 1
        ds = [2] * (k - 1) + [b + 2 - 2 * k] + ds[k:]
        return ('K', (strip(ds), 2, 1))
    if 2 * k == b + 1:
        return ('HALT',)
    return None
