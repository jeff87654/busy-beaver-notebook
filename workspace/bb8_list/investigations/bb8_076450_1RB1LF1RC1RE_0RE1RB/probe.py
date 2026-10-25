"""Probe: from 0^inf F>0 <word> 0^inf run until the next config in state F reading 0 with blank tape to its left."""
import sys
from lit import parse, rle
TM = "1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC"
T = parse(TM)
def run(word, st=5, maxsteps=10**7, stopstate=5):
    n = len(word); pad = 4*n + 256
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1; steps = 0; lo = pos; maxpos = pos
    while True:
        e = T[st][tape[pos]]
        if e is None:
            hi = len(tape)-1
            while hi > lo and tape[hi] == 0: hi -= 1
            return ('HALT %s' % 'ABCDEFGH'[st], steps, ''.join(map(str, tape[lo:hi+1])), maxpos - pad)
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        lo = min(lo, pos); maxpos = max(maxpos, pos)
        if st == stopstate and tape[pos] == 0 and not any(tape[lo:pos]):
            hi = len(tape) - 1
            while hi > pos and tape[hi] == 0: hi -= 1
            return ('F0', steps, ''.join(map(str, tape[pos+1:hi+1])), maxpos - pad)
        if steps > maxsteps: return ('LIMIT', steps, None, None)
if __name__ == '__main__':
    for suffix in ('00', '01'):
        for n in range(0, 30):
            k, s, w, mp = run('1'*n + suffix + '1011')
            print(suffix, n, n % 6, k, s, rle(w) if w else w, 'maxpos', mp, 'len', n+2)
