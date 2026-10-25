"""Literal run from an arbitrary configuration; report K-form snapshots (P11 + tokens + (10)^r + 111001, head B on blank)."""
import sys
from tr import TT

def parseK(cells, P=True, tail='111001'):
    s = ''.join(map(str, cells))
    if not s.endswith(tail): return None
    s = s[:-len(tail)]
    if P:
        if not s.startswith('11'): return None
        s = s[2:]
    toks = []; i = 0
    while True:
        j = 0
        while s.startswith('10', i): i += 2; j += 1
        if i == len(s): return toks, j
        if s[i] == '1': toks.append(j); i += 1; continue
        return None

def run(left, q, right, N, maxsnap=1, want_state=1):
    """left: cells left of head (left-to-right order), right: head cell and cells to its right."""
    SZ = 2 * N + len(left) + len(right) + 10 if N < 4_000_000 else 8_000_000
    tape = bytearray(SZ); base = SZ // 2
    for i, ch in enumerate(left): tape[base - len(left) + i] = int(ch)
    for i, ch in enumerate(right): tape[base + i] = int(ch)
    p = base; mn = base - len(left); mx = base + len(right) - 1
    out = []
    for st in range(N):
        c = tape[p]; t = TT[(q, c)]
        if t is None: out.append(('HALT', st)); return out
        tape[p] = t[0]; p += t[1]; q = t[2]
        if p < mn: mn = p
        if p > mx: mx = p
        if q == want_state and tape[p] == 0 and p > mx - 1:
            hi = p - 1
            lo = mn
            while lo < hi and tape[lo] == 0: lo += 1
            r = parseK(tape[lo:p])
            if r is not None:
                out.append((st + 1, r[0], r[1]))
                if len(out) >= maxsnap: return out
    out.append(('NOT', N))
    return out
