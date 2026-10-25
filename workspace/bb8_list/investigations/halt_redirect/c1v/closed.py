"""closed.py: check the closed form of one cycle with the abstract R1-R3 process: in u = 2(r+5)/3 units, one borrow at
depth k (k zero tokens nearer than the borrowed token) followed by the full clearing of the deposit maps u -> 2^^^(k+1) u."""
def proc(digs, a, r):
    """digs nearest-first; run R1-R3 until the borrow would need the token beyond digs; return r"""
    d = list(digs)
    while True:
        if a >= 4: a -= 3; r = 2 * r + 5; continue
        assert a == 1
        j = 0
        while j < len(d) and d[j] == 1: j += 1
        if j == len(d): return r
        d[j] -= 3
        if j == 0: a = 2 * r + 5
        else: d[j - 1] = 2 * r + 5
        r = 1
def U(r): assert (2 * (r + 5)) % 3 == 0; return 2 * (r + 5) // 3
# depth 0: [4 | 1 | r] (the 4 is borrowed once)
for r in (1, 4, 7, 10, 19, 40):
    out = proc([4], 1, r); assert U(out) == 2 ** U(r), (r, out)
# depth 1: [4, 1 | 1 | r]  -> 2^^U
def tet(n):
    x = 1
    for _ in range(n): x = 2 ** x
    return x
for r in (1,):
    out = proc([1, 4], 1, r); assert U(out) == tet(U(r)), (r, out)
# depth 2 with r = 1: u = 4 -> 2^^^4 = 2^^65536 : too big; check 2^^^3 = 2^^4 = 65536 via u = 3? u must be >= 4.
print('closed form u -> 2^(k+1 arrows) u verified for k = 0 (6 values) and k = 1 (u = 4: 2^^4 = 65536)')
