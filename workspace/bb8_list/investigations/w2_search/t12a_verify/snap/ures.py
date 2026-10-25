"""Values of iter d (U n) A (n1's CLR output), exact when small, else a fresh atom with an exact residue."""
from vals import *
CAP = 200000
def U_exact(j, A, cap=CAP):
    if j == 0:
        r = 2 * A + 8; return r if r <= cap else None
    x = 4
    for _ in range(A // 3 + 1):
        x = U_exact(j - 1, x, cap)
        if x is None: return None
    return x
def iterU_exact(d, n, A, cap=CAP):
    x = A
    for _ in range(d):
        x = U_exact(n, x, cap)
        if x is None: return None
    return x
def isbig(x): return isinstance(x, Val) and x.huge()
def toint(x): return x.ival() if isinstance(x, Val) else x
def res_of(x, m):
    return x.res(m) if isbig(x) else toint(x) % m
def pow2mod(e, m):
    if not isbig(e): return pow(2, toint(e), m)
    l = lam(m); er = e.res(l)
    while er < v2bound(m) + 8: er += l
    return pow(2, er, m)
def r_iterU(d, n, A, m):
    """residue mod m of iter d (U n) A; d, n, A: int or Val (huge). Assumes real huge values are huge."""
    if m == 1: return 0
    if not isbig(d) and toint(d) == 0: return res_of(A, m)
    if not isbig(n) and toint(n) == 0:
        return (pow2mod(d, m) * (res_of(A, m) + 8) - 8) % m
    if not isbig(n) and toint(n) == 1:
        if not isbig(d) and not isbig(A):
            v = iterU_exact(toint(d), 1, toint(A), 10**6)
            if v is not None: return v % m
        # Y = iter (d-1) (U 1) A ; result = 12 * 2^(Y//3 + 1) - 8, Y = 1 mod 3
        if not isbig(d):
            l = lam(m)
            dd = min(toint(d), 60)     # residues of a tall U1-chain are constant in its length (see NOTES)
            if not isbig(A):
                Y = iterU_exact(dd - 1, 1, toint(A), 10**6)
                if Y is not None:
                    return (12 * pow(2, (Y - 1) // 3 + 1, m) - 8) % m
            yr = r_iterU(dd - 1, 1, A, 3 * l)
            assert yr % 3 == 1, 'U1 input not 1 mod 3'
            e = (yr - 1) // 3 + 1
            while e < v2bound(m) + 8: e += l
            return (12 * pow(2, e, m) - 8) % m
        raise NotImplementedError('iter (huge) (U 1)')
    # n >= 2
    if isbig(n) or isbig(A) or isbig(d):
        return (3 * tau(m) - 8) % m
    d, n, A = toint(d), toint(n), toint(A)
    v = iterU_exact(d, n, A, 10**6)
    if v is not None: return v % m
    # descend: iter d (U n) A = U n (Y), Y = iter (d-1) (U n) A ; U n Y = iter (Y//3+1) (U (n-1)) 4
    Y = iterU_exact(d - 1, n, A, 10**6)
    if Y is None: return (3 * tau(m) - 8) % m      # Y itself huge: tall tower
    return r_iterU(Y // 3 + 1, n - 1, 4, m)
def iterU(d, n, A, note=''):
    """Val of iter d (U n) A"""
    if not isbig(d) and toint(d) == 0: return Val.of(A)
    if not (isbig(d) or isbig(n) or isbig(A)):
        v = iterU_exact(toint(d), toint(n), toint(A))
        if v is not None: return Val(v)
    if not isbig(n) and toint(n) == 0 and not isbig(d) and toint(d) <= 6 and isbig(A):
        p = 2 ** toint(d); return Val.of(A) * p + 8 * (p - 1)
    divs = sorted(set(2 ** a * 3 ** b * 7 ** c for a in range(5) for b in range(0, 7) for c in range(3)))
    for dv in divs:
        m = MB // dv
        try:
            r = r_iterU(d, n, A, m); break
        except ValueError:
            continue
    else:
        raise ValueError('no precision for iterU')
    geU = None
    if (isbig(d) or toint(d) >= 1) and (isbig(A) or toint(A) >= 4): geU = Val.of(n)
    return new_atom('U', r, m, note=note, geU=geU)
