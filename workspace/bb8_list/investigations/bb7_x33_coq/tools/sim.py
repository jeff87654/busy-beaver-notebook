"""sim.py: literal simulator for X = 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE.
K(runs) = 1^r0 0 1^r1 0 ... 0 1^rn  with the head in A on the blank right after (blank elsewhere).
nxt(runs) runs to the next K event (A, reading 0, right of all ones) or the halt."""
import idle  # noqa
import sys
X = '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE'
def parse(M):
    tr = {}
    for q, blk in enumerate(M.split('_')):
        for c in range(2):
            t = blk[3*c:3*c+3]
            tr[(q, c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
    return tr
TR = parse(X)
def word(runs):
    return '0'.join('1' * r for r in runs)
def nxt(runs, maxsteps=10**8, size=1 << 20, tr=TR):
    w = word(runs)
    T = bytearray(size + 2 * len(w)); off = len(T) // 2 - len(w)
    for i, ch in enumerate(w): T[off + i] = ch == '1'
    p = off + len(w); q = 0; hi = off + len(w) - 1
    while hi >= off and not T[hi]: hi -= 1
    for st in range(1, maxsteps + 1):
        c = T[p]; t = tr[(q, c)]
        if t is None:
            return ('HALT', st - 1, sum(T), q, p, T)
        T[p] = t[0]
        if t[0] and p > hi: hi = p
        p += t[1]; q = t[2]
        if p <= 0 or p >= len(T) - 1: return ('EDGE', st, None)
        if q == 0 and p > hi and T[p] == 0:
            while hi >= 0 and not T[hi]: hi -= 1
            if p > hi:
                lo = 0
                while not T[lo]: lo += 1
                s = bytes(T[lo:p]).replace(b'\x00', b'0').replace(b'\x01', b'1').decode()
                return ('K', st, [len(x) for x in s.split('0')], p - hi - 1)
    return ('TIMEOUT', maxsteps)
def blank_run(maxsteps):
    return nxt([], maxsteps)
if __name__ == '__main__':
    r = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 and sys.argv[1] else []
    for i in range(int(sys.argv[2]) if len(sys.argv) > 2 else 10):
        o = nxt(r)
        print(o[:2], o[2] if o[0] == 'K' else o[2:4], o[3] if o[0] == 'K' else '')
        if o[0] != 'K': break
        r = o[2]
