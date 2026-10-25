import sys
from canon import word_P, word_Q
from lit import parse, MAIN, compress
T = parse(MAIN)
kind, a, n, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
w = word_P(a, n) if kind == 'P' else word_Q(a, n)
pad = 1 << 20
tape = bytearray(pad) + bytearray(int(c) for c in w) + bytearray(pad)
pos = pad + len(w); st = 1; steps = 0; lo = pad; hi = pos
def show():
    i = lo
    while tape[i] == 0 and i < pos: i += 1
    j = hi
    while tape[j] == 0 and j > pos: j -= 1
    return compress(''.join(map(str, tape[i:pos]))) + ' [%s%d] ' % ('ABCDEFGH'[st], tape[pos]) + compress(''.join(map(str, tape[pos+1:j+1])))
while steps < N:
    e = T[st][tape[pos]]
    if e is None:
        print('HALT', steps, show()); break
    wr, d, q = e
    tape[pos] = wr; pos += d; st = q; steps += 1
    if pos < lo:
        lo = pos; print('L', steps, show())
    if pos > hi:
        hi = pos
        if st == 1: print('R', steps, show())
