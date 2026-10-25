"""Run from 0^inf G>0 <word> 0^inf to the next left-edge G0 configuration (blank tape left of head).
Prints steps, resulting word, and the max position (relative to word start) visited."""
import sys
from lit import parse, MAIN, compress
T = parse(MAIN)
G = 6

def run(word, maxsteps=10**8, tm=None):
    TT = parse(tm) if tm else T
    n = len(word)
    pad = 2 * n + 64
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1
    st = G
    steps = 0
    maxpos = pos; lo = pos
    while True:
        e = TT[st][tape[pos]]
        if e is None:
            return ('HALT', steps, None, maxpos - pad, 'ABCDEFGH'[st] + str(tape[pos]))
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos > maxpos: maxpos = pos
        if pos < lo: lo = pos
        if pos <= 0 or pos >= len(tape) - 1:
            return ('OUT', steps, None, maxpos - pad, None)
        if st == G and tape[pos] == 0 and not any(tape[lo:pos]):
            hi = len(tape) - 1
            while hi > pos and tape[hi] == 0: hi -= 1
            return ('G0', steps, ''.join(map(str, tape[pos + 1:hi + 1])), maxpos - pad, None)
        if steps > maxsteps:
            return ('LIMIT', steps, None, maxpos - pad, None)

if __name__ == '__main__':
    w = sys.argv[1]
    k, st, right, mp, x = run(w)
    print(k, st, compress(right) if right else right, 'maxpos', mp, 'len', len(w), x or '')
