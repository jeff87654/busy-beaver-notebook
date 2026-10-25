"""Y(M) = 0^inf A>0 (01)^M 0^inf : run literally to the first canonical config (lenient prefix)."""
import re, sys
from lit import parse, MAIN
T = parse(MAIN)
R = re.compile(r'^(.*?)((?:010)*)(01110111|0)(1+)01010$')
def run_Y(M, maxsteps=10**7):
    w = '01' * M
    pad = 4 * len(w) + 4096
    tape = bytearray(pad) + bytearray(int(c) for c in w) + bytearray(4 * len(w) + 4096)
    pos = pad - 1; st = 0; steps = 0; lo = pos; hi = pad + len(w) - 1
    while steps < maxsteps:
        e = T[st][tape[pos]]
        if e is None:
            return ('HALT', steps)
        wr, d, q = e
        tape[pos] = wr; pos += d; st = q; steps += 1
        if pos < lo: lo = pos
        if pos > hi:
            hi = pos
            if st == 1:
                i = lo
                while tape[i] == 0: i += 1
                s = ''.join('1' if c else '0' for c in tape[i:pos])
                m = R.match(s)
                if m and len(m.group(1)) <= 4 and len(m.group(4)) >= 2:
                    return (m.group(1), len(m.group(2)) // 3, 'P' if m.group(3) == '01110111' else 'Q', len(m.group(4)), steps, i - (pad - 1))
    return ('LIMIT', steps)
if __name__ == '__main__':
    for M in range(int(sys.argv[1]), int(sys.argv[2])):
        print(M, M % 3, run_Y(M))
