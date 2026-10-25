import re, sys
from lit import parse, MAIN
T = parse(MAIN)
R = re.compile(r'^(.*?)((?:010)*)(01110111|0)(1+)01010$')
N = int(sys.argv[1])
size = 1 << 16
tape = bytearray(size); pos = size // 2; st = 0; steps = 0; lo = hi = pos
while steps < N:
    e = T[st][tape[pos]]
    if e is None:
        print('HALT', steps); break
    w, d, q = e
    tape[pos] = w; pos += d; st = q; steps += 1
    if pos < lo: lo = pos
    if pos > hi:
        hi = pos
        if st == 1:
            i = lo
            while tape[i] == 0: i += 1
            s = ''.join('1' if c else '0' for c in tape[i:pos])
            m = R.match(s)
            if m and len(m.group(1)) <= 4 and len(m.group(4)) >= 2:
                print(steps, repr(m.group(1)), len(m.group(2)) // 3, 'P' if m.group(3) == '01110111' else 'Q', len(m.group(4)))
