"""Find the earliest configurations (from blank tape) of the form
   blank [A0] 0 (100)^x 1010 (100)^j 1010 (110)^k 10100 R      (beta, any R)
   blank [A0] 0 (100)^x 1010 (100)^j 10 (100)^m 00100 R        (gamma, any R)
Also report the first few configurations where head is at the left end in A reading 0 with blank left.
"""
import re, sys
TMS = "1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG"
T = []
for ch in TMS.split('_'):
    row = []
    for i in (0, 3):
        e = ch[i:i + 3]
        row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, 'ABCDEFG'.index(e[2])))
    T.append(row)

N = 1 << 16
tape = bytearray(N)
pos = N // 2
st = 0
minp = maxp = pos
beta = re.compile(r'^00((?:100)*)1010((?:100)*)1010((?:110)*)10100(.*)$')
gamma = re.compile(r'^00((?:100)*)1010((?:100)*)10((?:100)*)00100(.*)$')
maxsteps = int(sys.argv[1]) if len(sys.argv) > 1 else 3_000_000
found = 0
for n in range(1, maxsteps + 1):
    tr = T[st][tape[pos]]
    if tr is None:
        print('HALT', n); break
    w, d, st = tr
    tape[pos] = w
    pos += d
    if pos < minp: minp = pos
    if pos > maxp: maxp = pos
    if st == 0 and tape[pos] == 0 and not any(tape[minp:pos]):
        hi = maxp
        while hi > pos and tape[hi] == 0: hi -= 1
        s = ''.join('1' if c else '0' for c in tape[pos:hi + 1])
        m = beta.match(s)
        if m:
            x, j, k = len(m.group(1)) // 3, len(m.group(2)) // 3, len(m.group(3)) // 3
            print(f'step {n}: beta x={x} j={j} k={k} R={m.group(4)!r}')
            found += 1
        m = gamma.match(s)
        if m:
            x, j, mm = len(m.group(1)) // 3, len(m.group(2)) // 3, len(m.group(3)) // 3
            print(f'step {n}: gamma x={x} j={j} m={mm} R={m.group(4)!r}')
            found += 1
        if found >= 12: break
        if found == 0 and n < 20000:
            print(f'step {n}: leftA0 {s[:80]}')
print('done at', n)
