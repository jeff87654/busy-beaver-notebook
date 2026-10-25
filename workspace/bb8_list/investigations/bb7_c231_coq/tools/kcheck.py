import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq')
import idle
M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
def parse(m):
    t = {}
    for i, g in enumerate(m.split('_')):
        for s in range(2):
            e = g[3*s:3*s+3]
            t[(i, s)] = None if e[2] in '-HZ' else (int(e[0]), 1 if e[1]=='R' else -1, ord(e[2])-65)
    return t
def ktape(ds, a, b):
    # right of head (head on first cell), nearest-first digits
    r = [0, 1] + [1,1]*b + [0,0] + [1,1]*a + [0,0]
    for d in ds: r += [1,1]*d + [0,0]
    r += [1]
    return r
def kparse(cells):
    # cells: list from head to last nonzero; returns (ds,a,b) or None
    if len(cells) < 3 or cells[0] != 0 or cells[1] != 1: return None
    i = 2; vals = []
    n = len(cells)
    while True:
        c = 0
        while i + 1 < n and cells[i] == 1 and cells[i+1] == 1: c += 1; i += 2
        if i == n - 1 and cells[i] == 1 and c == 0: break
        if i + 1 < n and cells[i] == 0 and cells[i+1] == 0: vals.append(c); i += 2
        else: return None
    if len(vals) < 2: return None
    return (vals[2:], vals[1], vals[0])
def run_k(ds, a, b, m=M1, maxsteps=10**8, stop_any_E=True):
    T = parse(m)
    r = ktape(ds, a, b)
    off = 10**6
    tape = bytearray(2*off + len(r) + 10**6)
    for i, v in enumerate(r): tape[off + i] = v
    pos = off; q = 4; n = 0; lo = off; hi = off + len(r) - 1
    while n < maxsteps:
        s = tape[pos]
        tr = T[(q, s)]
        if tr is None:
            return ('H', n, q, pos, tape, lo, hi)
        w, d, q2 = tr
        tape[pos] = w; pos += d; q = q2; n += 1
        if pos < lo: lo = pos
        if pos > hi: hi = pos
        if q == 4 and tape[pos] == 0 and all(tape[i] == 0 for i in range(lo, pos)):
            # trim right
            h = hi
            while h > pos and tape[h] == 0: h -= 1
            k = kparse(list(tape[pos:h+1]))
            if k is not None:
                return ('K', n, k)
    return ('T', n)
def ones(tape, lo, hi): return sum(tape[lo:hi+1])
if __name__ == '__main__':
    print(run_k([1]*20, 1, 2))
