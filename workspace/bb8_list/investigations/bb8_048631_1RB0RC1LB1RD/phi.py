def push(a):
    r = a % 5
    if r in (3, 4): return (3, (2*a-6,))
    if r in (0, 2): return (2, (2*a-4,))
    return (2, (1, 2*a-5))
def phi(a, ts):
    ts = tuple(ts)
    if a >= 4:
        a2, L = push(a)
        return (a2, L + ts)
    # a in {2,3}
    m = 0
    while m < len(ts) and ts[m] <= 2: m += 1
    P = ts[:m]; s = sum(P)
    A = a + m + 1
    if m < len(ts):
        t = ts[m]; assert t >= 3
        tail = ((t-2,) if t-2 >= 1 else ()) + ts[m+1:]
    else:
        tail = ()
    u = 2*m - s                      # number of 1s in P
    E = 2*a + s + 2
    if u % 10 == 0:
        return (E//2, tail)          # includes P all 2s (u = 0): pending head (A; tail)
    r = A % 5
    if r in (3, 4): return (3, (E-6,) + tail)
    if r in (0, 2): return (2, (E-4,) + tail)
    return (2, (1, E-5) + tail)
