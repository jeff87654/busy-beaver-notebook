"""Literal trace: print the tape at every turn where the head leaves the written region (or reaches a K-form snapshot)."""
import sys, re
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
TT = {}
for i, part in enumerate(M.split('_')):
    for s in range(2):
        t = part[3 * s:3 * s + 3]
        TT[(i, s)] = None if t == '---' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)

def D(m): return '10' * m + '1'
def word(toks, r, P=True, tail='111001'):
    return ('11' if P else '') + ''.join(D(m) for m in toks) + '10' * r + tail

def comp(s):
    """compress a 0/1 string into tokens: D(m) and runs."""
    out = []
    i = 0
    # greedy parse as (10)^m 1 tokens
    return s

def run(w, q, N, every=None, lo_print=True):
    SZ = len(w) + 2 * N // 1 + 10 if N < 10**6 else 4 * 10**6
    tape = bytearray(SZ)
    base = SZ // 2
    for i, ch in enumerate(w):
        tape[base - len(w) + i] = int(ch)
    p = base
    mn, mx = base - len(w), base - 1
    events = []
    for st in range(N):
        c = tape[p]
        t = TT[(q, c)]
        if t is None:
            events.append((st, 'HALT', p))
            return events
        tape[p] = t[0]
        p += t[1]
        q = t[2]
        if p < mn or p > mx:
            mn = min(mn, p); mx = max(mx, p)
            lo = mn
            while lo < mx and tape[lo] == 0: lo += 1
            hi = mx
            while hi > lo and tape[hi] == 0: hi -= 1
            s = ''.join(map(str, tape[lo:hi + 1]))
            side = 'L' if p < lo + 1 else 'R'
            events.append((st + 1, 'ABCDEFGH'[q], side, s, p - lo))
    return events

def rl(s):
    """run-length view of blocks"""
    return re.sub(r'((10)+)', lambda m: '(10)^%d ' % (len(m.group(1)) // 2), s)

if __name__ == '__main__':
    n, b, N = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    w = word([1] * (n + 1), 3 * b + 2)
    for e in run(w, 1, N):
        if e[1] == 'HALT': print(e); break
        st, q, side, s, pos = e
        print(st, q, side, pos, rl(s))
