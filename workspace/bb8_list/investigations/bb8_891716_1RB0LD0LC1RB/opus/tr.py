"""Concrete tracer: start F(W,b) (tape order), print the tape (RLE) at every left->right turn (local leftmost point)."""
import sys, os
TM = os.environ.get('TM', "1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
def parse(tm):
    d = {}
    for i, t in enumerate(tm.split('_')):
        for s in (0, 1):
            x = t[3*s:3*s+3]
            d[(i, s)] = None if x == '---' else (int(x[0]), x[1], 'ABCDEFGH'.index(x[2]))
    return d
D = parse(TM)
def fword(W, b):
    # tape order: for digits far..near: 0 (10)^d ; then 0 (10)^(2b+1) 011  (W nearest first)
    s = ''
    for d in reversed(W):
        s += '10' * d + '0'
    s += '10' * (2 * b + 1) + '011'
    return '1' + s     # leading marker 1 so the far end is visible (stands for t)
def rle(s):
    out = []; i = 0
    while i < len(s):
        best = None
        for L in (1, 2, 4, 5):
            u = s[i:i+L]
            if len(u) < L: continue
            j = i
            while s[j:j+L] == u: j += L
            n = (j - i) // L
            if n >= 3 and (best is None or n * L > best[1] * len(best[0])):
                best = (u, n)
        if best:
            out.append('(%s)^%d' % best); i += best[1] * len(best[0])
        else:
            out.append(s[i]); i += 1
    return ' '.join(out)
def show(tape, pos, q, lo=None, hi=None):
    lo = min(min(tape), pos) if lo is None else lo
    hi = max(max(tape), pos) if hi is None else hi
    s = ''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1))
    return rle(s[:pos-lo]) + ' [' + 'ABCDEFGH'[q] + '] ' + rle(s[pos-lo:])
def run(W, b, N=10**6, mode='turn'):
    w = fword(W, b)
    tape = {i: int(c) for i, c in enumerate(w)}
    pos = len(w); q = 1
    lastdir = None
    for n in range(N):
        s = tape.get(pos, 0)
        t = D[(q, s)]
        if t is None:
            print('HALT', n); return
        wr, dr, nq = t
        tape[pos] = wr
        if mode == 'turn' and lastdir == 'L' and dr == 'R':
            print(n, show(tape, pos, q))
        lastdir = dr
        pos += 1 if dr == 'R' else -1
        q = nq
        # K event: state B, head on blank right of everything, suffix 011
        if q == 1 and n > 5 and pos > max(k for k, v in tape.items() if v) and [tape.get(pos-i, 0) for i in (1, 2, 3)] == [1, 1, 0]:
            print('K at', n + 1, show(tape, pos, q)); return
if __name__ == '__main__':
    W = [int(x) for x in sys.argv[1].split(',')]
    b = int(sys.argv[2])
    run(W, b)
