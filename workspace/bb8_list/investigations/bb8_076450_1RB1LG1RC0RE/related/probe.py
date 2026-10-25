"""Run from 0^inf A>0 <word> 0^inf to the next left-edge A0 (or halt); report result word, offset, steps,
and the max cell index visited (0-based within word).  usage: python probe.py TM word [word...]"""
import sys
from lit import parse, ST, compress

def run(T, word, maxsteps=10**7):
    n = len(word); pad = 4 * n + 64
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1; st = 0; steps = 0; maxpos = pos
    while steps < maxsteps:
        e = T[st][tape[pos]]
        if e is None:
            hi = len(tape) - 1
            while hi > pos and tape[hi] == 0: hi -= 1
            return ('HALT', steps, pos - (pad - 1), ST[st] + str(tape[pos]), ''.join(map(str, tape[pos+1:hi+1])), maxpos - pad)
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos > maxpos: maxpos = pos
        if st == 0 and tape[pos] == 0 and not any(tape[:pos]):
            hi = len(tape) - 1
            while hi > pos and tape[hi] == 0: hi -= 1
            return ('A0', steps, pos - (pad - 1), 'A0', ''.join(map(str, tape[pos+1:hi+1])), maxpos - pad)
    return ('LIMIT', steps, None, None, None, maxpos - pad)

if __name__ == '__main__':
    T = parse(sys.argv[1])
    for w in sys.argv[2:]:
        k, st, off, hs, right, mx = run(T, w)
        print(k, 'steps', st, 'off', off, hs, 'maxidx', mx, '/', len(w), '|', w, '->', right, '|', compress(right) if right else '')
