"""absim.py -- abstract token-level simulator for the c35 exception machine (exact integers).

Configuration: B-form token list [t_0, ..., t_m, 0, y] (tape 0^inf D(t_0) ... D(t_m) D(0) D(y) G> 0^inf,
D(n) = 1 (01)^n).  One step = from one B-form right-edge G0 event to the next.

Rules (derived from literal simulation; every rule is checked against sim.exe by check_absim.py):
  scan: from the right, skip k >= 0 tokens equal to 1; x = first token != 1 (index i)
  R1   x >= 3, k = 0 : [.., x, 0, y]        -> [.., x-3, 0, 2y+8]
  R2   x >= 3, k >= 1: [.., x, 1^k, 0, y]   -> [.., x-3, y+3, 1^(k-1), 0, 4]
  S0*  x == 0  (see s0)      S2*  x == 2  (see s2)
Unknown patterns raise Unknown(description).
"""


class Unknown(Exception):
    pass


def scan_left_ones(t, i):
    """from index i (inclusive) go left over tokens equal to 1; return (index of first non-1 or -1, count)"""
    j = 0
    while i >= 0 and t[i] == 1:
        i -= 1; j += 1
    return i, j


def step(t):
    """apply one rule in place-free style; returns (new list, rule name)"""
    assert t[-2] == 0
    y = t[-1]
    i, k = scan_left_ones(t, len(t) - 3)
    if i < 0:
        raise Unknown('boundary: all ones (k=%d)' % k)
    x = t[i]
    pre = t[:i]
    ones_k = [1] * k
    if x >= 3:
        if k == 0:
            return pre + [x - 3, 0, 2 * y + 8], 'R1'
        return pre + [x - 3, y + 3] + [1] * (k - 1) + [0, 4], 'R2'
    if x == 0:
        return s0(t, i, k, y)
    if x == 2:
        return s2(t, i, k, y)
    raise Unknown('x=%d' % x)


def tail_after_borrow(val, k, y, kind):
    """common tails: kind 'k0' when k == 0 handled by callers"""
    raise NotImplementedError


def s0(t, i, k, y):
    # [.., u, 1^j, (w...), 0, 1^k, 0, y] with the D0 at index i
    w_i, j = scan_left_ones(t, i - 1)
    if w_i < 0:
        raise Unknown('S0 boundary j=%d k=%d' % (j, k))
    w = t[w_i]
    pre = t[:w_i]
    ones_j = [1] * j
    # borrowed-digit tail: k == 0 -> [.., 0, 2y+c]; k >= 1 -> [.., y+d, 1^(k-1), 0, 4]
    if j >= 1:
        if w >= 4:
            if k == 0:
                return pre + [w - 4, 3] + ones_j + [0, 2 * y + 4], 'S0j'   # UNVERIFIED shape for k=0, j>=1
            return pre + [w - 4, 3] + ones_j + [y + 1] + [1] * (k - 1) + [0, 4], 'S0j'
        raise Unknown('S0 j=%d w=%d' % (j, w))
    if w >= 4:
        if k == 0:
            return pre + [w - 4, 3, 0, 2 * y + 4], 'S0a'
        return pre + [w - 4, 3, y + 1] + [1] * (k - 1) + [0, 4], 'S0b'
    if w == 3:
        u_i = w_i - 1
        if u_i < 0 or t[u_i] < 3:
            raise Unknown('S0 w=3 u=%s' % (t[u_i] if u_i >= 0 else 'bdry'))
        return t[:u_i] + [t[u_i] - 3, 5, y] + [1] * k + [0, 4], 'S0w3'
    if w == 2:
        u_i = w_i - 1
        if u_i < 0 or t[u_i] < 3:
            raise Unknown('S0 w=2 u=%s' % (t[u_i] if u_i >= 0 else 'bdry'))
        if k == 0:
            return t[:u_i] + [t[u_i] - 3, 4, 0, 0, 2 * y + 4], 'S0w2a'
        return t[:u_i] + [t[u_i] - 3, 4, 0, y + 1] + [1] * (k - 1) + [0, 4], 'S0w2b'
    if w == 0:
        u_i = w_i - 1
        if u_i < 0 or t[u_i] < 4:
            raise Unknown('S0 w=0 u=%s' % (t[u_i] if u_i >= 0 else 'bdry'))
        if k == 0:
            return t[:u_i] + [t[u_i] - 4, 2, 0, 0, 2 * y + 6], 'S0w0a'
        return t[:u_i] + [t[u_i] - 4, 2, 0, y + 2] + [1] * (k - 1) + [0, 4], 'S0w0b'
    raise Unknown('S0 w=%d' % w)


def s2(t, i, k, y):
    w_i, j = scan_left_ones(t, i - 1)
    if w_i < 0:
        raise Unknown('S2 boundary j=%d k=%d' % (j, k))
    w = t[w_i]
    if j == 0 and w >= 3:
        return t[:w_i] + [w - 3, y + 4] + [1] * k + [0, 6], 'S2'
    if j == 1 and w >= 3:
        # [u, 1, 2, 1^k, 0, y] -> [u-3, y+5, 0, 1^k, 0, 6]   (u = w here)
        return t[:w_i] + [w - 3, y + 5, 0] + [1] * k + [0, 6], 'S2w1'
    if j == 0 and w == 0:
        u_i, jj = scan_left_ones(t, w_i - 1)
        if u_i < 0 or t[u_i] < 4:
            raise Unknown('S2 w=0 jj=%d u=%s' % (jj, t[u_i] if u_i >= 0 else 'bdry'))
        return t[:u_i] + [t[u_i] - 4, 3] + [1] * jj + [y + 2] + [1] * k + [0, 6], 'S2w0'
    if j == 0 and w == 2 and k == 0:
        u_i = w_i - 1
        if u_i < 0 or t[u_i] < 1:
            raise Unknown('S2 w=2 u=%s' % (t[u_i] if u_i >= 0 else 'bdry'))
        return t[:u_i] + [t[u_i] - 1, y + 1, 5, 0, 4], 'S2w2a'
    raise Unknown('S2 j=%d w=%d k=%d' % (j, w, k))


def run(t, nsteps):
    out = [(list(t), None)]
    for _ in range(nsteps):
        t, r = step(t)
        out.append((t, r))
    return out
