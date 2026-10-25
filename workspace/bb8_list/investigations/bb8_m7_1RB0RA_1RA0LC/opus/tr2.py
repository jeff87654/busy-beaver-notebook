"""Literal trace from used(n, b): print the tape at every left-end visit (and K-form snapshots), run-compressed."""
import sys
from tr import TT, word

def compress(s, minrep=3):
    out = []
    i = 0
    n = len(s)
    while i < n:
        best = None
        for p in range(1, 13):
            blk = s[i:i + p]
            if len(blk) < p: break
            k = 1
            while s[i + k * p:i + (k + 1) * p] == blk: k += 1
            if k >= minrep and (best is None or k * p > best[0] * best[1] + 0):
                best = (k, p, blk)
        if best and best[0] * best[1] >= 6:
            k, p, blk = best
            out.append('(%s)^%d' % (blk, k)); i += k * p
        else:
            out.append(s[i]); i += 1
    # merge single chars
    res, buf = [], ''
    for t in out:
        if len(t) == 1: buf += t
        else:
            if buf: res.append(buf); buf = ''
            res.append(t)
    if buf: res.append(buf)
    return ' '.join(res)

def trace(w, q, N, mode='L'):
    SZ = 1 << 22
    tape = bytearray(SZ); base = SZ // 2
    for i, ch in enumerate(w): tape[base - len(w) + i] = int(ch)
    p = base; mn, mx = base - len(w), base - 1
    for st in range(N):
        c = tape[p]; t = TT[(q, c)]
        if t is None: print('HALT', st); return
        tape[p] = t[0]; p += t[1]; q = t[2]
        ev = None
        if p < mn: mn = p; ev = 'L'
        elif p > mx: mx = p; ev = 'R'
        if ev and ev in mode:
            lo = mn
            while tape[lo] == 0 and lo < p: lo += 1
            hi = mx
            while tape[hi] == 0 and hi > p: hi -= 1
            s = ''.join(map(str, tape[lo:p])) + '[' + 'ABCDEFGH'[q] + ']' + ''.join(map(str, tape[p:hi + 1]))
            print(st + 1, ev, compress(s))

if __name__ == '__main__':
    n, b, N = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    mode = sys.argv[4] if len(sys.argv) > 4 else 'L'
    trace(word([1] * (n + 1), 3 * b + 2), 1, N, mode)
