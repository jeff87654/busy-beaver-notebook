"""tm.py: tiny literal TM helpers. parse(table)->dict; run(table, tape(str), pos, state, maxsteps, stop=callable)"""
def parse(s):
    rows = s.split('_'); M = {}
    for i, r in enumerate(rows):
        for c in range(2):
            x = r[3*c:3*c+3]
            if x[0] == '-' or x[2] in 'Z': M[(chr(65+i), c)] = None
            else: M[(chr(65+i), c)] = (int(x[0]), 1 if x[1] == 'R' else -1, x[2])
    return M
def run(M, tape=None, pos=0, q='A', maxsteps=10**7, stop=None):
    T = bytearray(1 << 22); off = 1 << 21
    if tape:
        for i, ch in enumerate(tape): T[off + i] = int(ch)
    p = off + pos; t = 0; lo = hi = p
    if tape: lo, hi = off, off + len(tape) - 1
    while t < maxsteps:
        c = T[p]; tr = M[(q, c)]
        if stop and stop(T, p, q, t, lo, hi, off): return ('STOP', t, T, p, q, lo, hi, off)
        if tr is None: return ('HALT', t, T, p, q, lo, hi, off)
        T[p] = tr[0]; p += tr[1]; q = tr[2]; t += 1
        if p < lo: lo = p
        if p > hi: hi = p
    return ('RUN', t, T, p, q, lo, hi, off)
def show(T, p, q, lo, hi):
    a = lo
    while a < p and T[a] == 0: a += 1
    b = hi
    while b > p and T[b] == 0: b -= 1
    return ''.join(str(T[i]) for i in range(a, p)) + '[' + q + str(T[p]) + ']' + ''.join(str(T[i]) for i in range(p + 1, b + 1))
