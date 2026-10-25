"""rules.py -- event rules of the c35 exception machine on B-form token lists, with exact or Huge values.

A B-form list is [t_0, ..., t_m, 0, y]  (tape 0^inf D(t_0)..D(t_m) D(0) D(y) G>, D(n) = 1 (01)^n).
Values are Python ints (exact) or H objects (huge, known only modulo M; always >= 2^62).

classify(t) returns an Event: name, lo (leftmost index read or written), and apply() -> new list.
Every rule here is checked against the literal machine by check_rules.py (exact small values).
"""
from num import H, add, dbl_add, mod3, ge, r1star, is_huge


class Unknown(Exception):
    pass


class Need(Exception):
    """the event reads a token left of the given list"""
    pass


def scan_ones(t, i):
    j = 0
    while i >= 0 and t[i] == 1:
        i -= 1; j += 1
    return i, j


def tail(k, y, c_k0_mul, c_k0_add, c_borrow):
    """standard borrowed-digit tail: k == 0 -> [0, c_mul*y + c_add]; k >= 1 -> [y + c_borrow, 1^(k-1), 0, 4]"""
    if k == 0:
        return [0, dbl_add(y, c_k0_add) if c_k0_mul == 2 else add(y, c_k0_add)]
    return [add(y, c_borrow)] + [1] * (k - 1) + [0, 4]


class Event:
    def __init__(self, name, lo, newlist):
        self.name, self.lo, self.newlist = name, lo, newlist


def classify(t):
    t = list(t)
    assert t[-2] == 0, t
    y = t[-1]
    i, k = scan_ones(t, len(t) - 3)
    if i < 0:
        raise Need('all ones k=%d' % k)
    x = t[i]
    if ge(x, 3):
        if k == 0:
            xe, y2 = r1star(x, y)
            return Event('R1*', i, t[:i] + [xe, 0, y2])
        return Event('R2', i, t[:i] + [add(x, -3), add(y, 3)] + [1] * (k - 1) + [0, 4])
    if x == 0:
        wi, j = scan_ones(t, i - 1)
        if wi < 0:
            raise Need('S0 j=%d k=%d' % (j, k))
        w = t[wi]
        if w == 2:
            # [u, 2, 1^j, 0, ...]: u >= 3 -> [u-3, 4, 0, 1^j, tail];  u = 0, v >= 9 -> [v-4, 3, 2, 0, 1^j, tail]
            ui = wi - 1
            if ui < 0:
                raise Need('S0 w=2')
            u = t[ui]
            if ge(u, 3):
                return Event('S0w2', ui, t[:ui] + [add(u, -3), 4, 0] + [1] * j + tail(k, y, 2, 4, 1))
            if u == 0:
                if ui - 1 < 0:
                    raise Need('S0 w=2 u=0')
                v = t[ui - 1]
                if ge(v, 9):
                    return Event('S0w2u0', ui - 1, t[:ui - 1] + [add(v, -4), 3, 2, 0] + [1] * j + tail(k, y, 2, 4, 1))
                if v == 0:
                    # [vv, 0, 0, 2, 1^j, 0, ...] -> [vv-4, 2, 0, 3, 0, 1^j, tail]
                    if ui - 2 < 0:
                        raise Need('S0 w=2 u=0 v=0')
                    vv = t[ui - 2]
                    if ge(vv, 9):
                        return Event('S0w2u0v0', ui - 2, t[:ui - 2] + [add(vv, -4), 2, 0, 3, 0] + [1] * j + tail(k, y, 2, 4, 1))
                    raise Unknown('S0 w=2 u=0 v=0 vv=%s j=%d k=%d' % (vv, j, k))
                raise Unknown('S0 w=2 u=0 v=%s j=%d k=%d' % (v, j, k))
            raise Unknown('S0 w=2 u=%s j=%d k=%d' % (u, j, k))
        if j >= 1:
            if ge(w, 4):
                return Event('S0j', wi, t[:wi] + [add(w, -4), 3] + [1] * j + tail(k, y, 2, 4, 1))
            if w == 3 and j == 1:
                ui = wi - 1
                if ui < 0:
                    raise Need('S0 j=1 w=3')
                if t[ui] == 0:
                    if ui - 1 < 0:
                        raise Need('S0 j=1 w=3 u=0')
                    v = t[ui - 1]
                    if ge(v, 9):
                        # [v, 0, 3, 1, 0, 1^k, 0, y] -> [v-3, y+6, 1, 1^k, 0, 4]
                        return Event('S0j1w3u0', ui - 1, t[:ui - 1] + [add(v, -3), add(y, 6), 1] + [1] * k + [0, 4])
            raise Unknown('S0 j=%d w=%s k=%d' % (j, w, k))
        if ge(w, 4):
            return Event('S0', wi, t[:wi] + [add(w, -4), 3] + tail(k, y, 2, 4, 1))
        ui = wi - 1
        if ui < 0 and w in (0, 2, 3):
            raise Need('S0 w=%s' % w)
        u = t[ui] if ui >= 0 else None
        if w == 3:
            if u is not None and ge(u, 3):
                return Event('S0w3', ui, t[:ui] + [add(u, -3), 5, y] + [1] * k + [0, 4])
            if u == 0:
                if ui - 1 < 0:
                    raise Need('S0 w=3 u=0')
                v = t[ui - 1]
                if ge(v, 9):
                    # [v, 0, 3, 0, 1^k, 0, y] -> [v-4, 3, 3, y, 1^k, 0, 4]
                    return Event('S0w3u0', ui - 1, t[:ui - 1] + [add(v, -4), 3, 3, y] + [1] * k + [0, 4])
                if v == 2:
                    if ui - 2 < 0:
                        raise Need('S0 w=3 u=0 v=2')
                    vv = t[ui - 2]
                    if ge(vv, 9):
                        # [vv, 2, 0, 3, 0, 1^k, 0, y] -> [vv-3, 4, 0, 3, y, 1^k, 0, 4]
                        return Event('S0w3u0v2', ui - 2, t[:ui - 2] + [add(vv, -3), 4, 0, 3, y] + [1] * k + [0, 4])
            raise Unknown('S0 w=3 u=%s k=%d' % (u, k))
        if w == 0:
            if u is not None and ge(u, 4):
                return Event('S0w0', ui, t[:ui] + [add(u, -4), 2, 0] + tail(k, y, 2, 6, 2))
            raise Unknown('S0 w=0 u=%s k=%d' % (u, k))
        raise Unknown('S0 w=%s' % w)
    if x == 2:
        wi, j = scan_ones(t, i - 1)
        if wi < 0:
            raise Need('S2 j=%d k=%d' % (j, k))
        w = t[wi]
        if j == 0 and ge(w, 3):
            return Event('S2', wi, t[:wi] + [add(w, -3), add(y, 4)] + [1] * k + [0, 6])
        if j == 1 and ge(w, 3):
            return Event('S2w1', wi, t[:wi] + [add(w, -3), add(y, 5), 0] + [1] * k + [0, 6])
        if j == 0 and w == 0:
            ui, jj = scan_ones(t, wi - 1)
            if ui < 0:
                raise Need('S2 w=0')
            if ge(t[ui], 4):
                return Event('S2w0', ui, t[:ui] + [add(t[ui], -4), 3] + [1] * jj + [add(y, 2)] + [1] * k + [0, 6])
            raise Unknown('S2 w=0 jj=%d u=%s k=%d' % (jj, t[ui] if ui >= 0 else None, k))
        if j == 0 and w == 2 and k == 0:
            ui = wi - 1
            if ui < 0:
                raise Need('S2 w=2')
            if ge(t[ui], 3):
                return Event('S2w2', ui, t[:ui] + [add(t[ui], -1), add(y, 1), 5, 0, 4])
            raise Unknown('S2 w=2 u=%s k=0' % (t[ui] if ui >= 0 else None))
        raise Unknown('S2 j=%d w=%s k=%d' % (j, w, k))
    raise Unknown('x=%s' % x)
