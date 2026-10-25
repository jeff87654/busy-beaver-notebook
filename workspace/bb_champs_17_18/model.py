"""Abstract model of the BB(17)/BB(18) Jacobzheng champions (rules verified on crafted tapes by test_*.py).
Tape at an engine start:  1^3 B> 1^l1 0 1^l2 0 ... 1^ln 0 0 1^c 0 1^d   (list l, counters c, d)."""
class Big(Exception): pass
def engine(l, cap=None):
    """A-G: returns exit (A, p): tape 1^A (01)^p 0 H> ..."""
    l = list(l)
    while True:
        A = 3 * l[0]; p = 1; i = 1
        while i < len(l) and l[i] == 1: p += 1; i += 1
        if i == len(l): return A, p
        if cap and (A > cap or len(l) > cap): raise Big()
        l = [1] * (p - 1) + [A + 1, l[i] - 1] + l[i + 1:]
def layer(A, p, c, d):
    """H..Q after an engine exit. returns ('HALT', A, p) or (new list, c, d)."""
    if c >= 1: return [1] * ((A - 1) // 2 + p - 1) + [2], c - 1, d       # H,I,J,K: decrement c, rebuild list
    if d == 1: return ('HALT', A, p)                                     # L,M: M reads 0
    if d >= 2: return [2], A + 2 * p + 2, d - 2                           # L,M,N,O: d-=2, merge -> c
    return [2], 3, A + 2 * p + 3                                         # L,P,Q,O: d==0, merge -> d
def run(l, c, d, maxev=50, cap=10**6):
    ev = []
    for _ in range(maxev):
        if len(l) > cap or max(l) > cap: ev.append(('BIG', len(l), max(l))); return ev
        try: A, p = engine(l, cap)
        except Big: ev.append(('BIG',)); return ev
        ev.append(('exit', A, p, c, d))
        r = layer(A, p, c, d)
        if r[0] == 'HALT': ev.append(r); return ev
        l, c, d = r
    return ev
