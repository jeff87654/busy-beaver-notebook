"""Level map on (prefix, b mod 220), b = A - 8 for a level start L(p, A).
Within a level: P1 -> P2 -> Q1 -> P1 with a: -5, 0, -6 and n: N_J = (831*8^J - 215)/7 at the J-th P1.
End at P1 (r = b mod 11 <= 4, a = r, n = N_J) or at Q1 (r >= 5, a = r - 5, n = 4 N_J + 90)."""
import sys
sys.set_int_max_str_digits(0)

def NJ(J):
    x = 831 * 8**J - 215
    assert x % 7 == 0
    return x // 7

def Yto(M):
    if M % 3 == 0: return ('p2', 2 * M // 3)
    if M % 3 == 1: return ('p1', (2 * M + 1) // 3)
    return ('p3', (2 * M - 7) // 3)

def div(x, d):
    assert x % d == 0, (x, d)
    return x // d

# end outcomes: (prefix, kind, a) -> function n -> ('HALT',) | (prefix', A')
END = {
    ('p1', 'P', 0): lambda n: Yto(n + 14),
    ('p1', 'P', 1): lambda n: Yto(2 * n + 30),
    ('p1', 'P', 2): lambda n: ('p2', div(2 * (2 * n + 49), 3)),
    ('p1', 'P', 3): lambda n: ('p2', div(8 * n + 136, 3)),
    ('p1', 'P', 4): lambda n: ('HALT',),
    ('p1', 'Q', 0): lambda n: Yto(n + 5),
    ('p1', 'Q', 1): lambda n: Yto(n + 12),
    ('p1', 'Q', 2): lambda n: Yto(2 * n + 26),
    ('p1', 'Q', 3): lambda n: ('HALT',),
    ('p1', 'Q', 4): lambda n: ('p2', div(8 * n + 136, 3)),
    ('p1', 'Q', 5): None,
    ('p2', 'P', 0): lambda n: Yto(n + 15),
    ('p2', 'P', 1): lambda n: ('HALT',),
    ('p2', 'P', 2): lambda n: ('HALT',),
    ('p2', 'P', 3): lambda n: ('p2', div(4 * n + 86, 3)),
    ('p2', 'P', 4): lambda n: Yto(4 * n + 117),
    ('p2', 'Q', 0): lambda n: ('p1', div(2 * n + 7, 3)),
    ('p2', 'Q', 1): lambda n: Yto(n + 13),
    ('p2', 'Q', 2): lambda n: ('HALT',),
    ('p2', 'Q', 3): lambda n: ('HALT',),
    ('p2', 'Q', 4): lambda n: Yto(2 * n + 42),
    ('p2', 'Q', 5): lambda n: Yto(4 * n + 90),
}

def level_end(p, b):
    """exact: returns (kind, a, n) at the end of the level with b = A - 8 (A >= 8)."""
    J, r = divmod(b, 11)
    if r <= 4: return ('P', r, NJ(J))
    return ('Q', r - 5, 4 * NJ(J) + 90)

def step_exact(p, b):
    kind, a, n = level_end(p, b)
    f = END.get((p, kind, a))
    if f is None: return ('UNKNOWN', (p, kind, a))
    out = f(n)
    if out[0] == 'HALT': return ('HALT', (p, kind, a, n))
    return (out[0], out[1] - 8)

def step_mod(p, bm):
    """bm = b mod 220 with b huge: returns (p', b' mod 220) using a representative J* = J (mod 20), J* >= 20."""
    J, r = divmod(bm, 11)          # J here is J mod 20
    res = []
    for Jstar in (J + 20, J + 40, J + 60):
        bstar = 11 * Jstar + r
        out = step_exact(p, bstar)
        if out[0] in ('HALT', 'UNKNOWN'):
            res.append(out[:1] + (out[1][:3],))
        else:
            res.append((out[0], out[1] % 220))
    assert res[0] == res[1] == res[2], res
    return res[0]

if __name__ == '__main__':
    # exact levels 2, 3 from the literal trajectory: L(p1, 69)
    p, b = 'p1', 69 - 8
    for k in (2, 3):
        J, r = divmod(b, 11)
        print('level %d: %s b=%d (A=%d) J=%d r=%d' % (k, p, b, b + 8, J, r))
        p, b = step_exact(p, b)
    # level 4 exactly (851k digits), then mod 220
    J, r = divmod(b, 11)
    print('level 4: %s b mod 220 = %d, r=%d, J mod 20=%d, A has %d digits' % (p, b % 220, r, J % 20, len(str(b))))
    bm = b % 220
    seen = {}
    for k in range(4, 60):
        J, r = divmod(bm, 11)
        key = (p, bm)
        print('level %d: %s b mod 220=%d r=%d J mod 20=%d' % (k, p, bm, r, J))
        if key in seen:
            print('cycle back to level', seen[key]); break
        seen[key] = k
        out = step_mod(p, bm)
        if out[0] in ('HALT', 'UNKNOWN'):
            print('  ->', out); break
        p, bm = out
