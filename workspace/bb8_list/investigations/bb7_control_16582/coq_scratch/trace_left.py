"""Print compressed tapes whenever head is at the left end in A reading 0 (blank left), up to step N."""
import re, sys
TMS = "1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG"
T = []
for ch in TMS.split('_'):
    row = []
    for i in (0, 3):
        e = ch[i:i + 3]
        row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, 'ABCDEFG'.index(e[2])))
    T.append(row)

def compress(s):
    out = []
    i = 0
    while i < len(s):
        best = None
        for blk in ('100', '110', '001', '011', '101', '010', '10', '01'):
            n = 0
            while s.startswith(blk, i + n * len(blk)):
                n += 1
            if n >= 3 and (best is None or n * len(blk) > best[1] * len(best[0])):
                best = (blk, n)
        if best:
            out.append(f'({best[0]})^{best[1]} ')
            i += best[1] * len(best[0])
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)

N = 1 << 16
tape = bytearray(N)
pos = N // 2
st = 0
minp = maxp = pos
maxsteps = int(sys.argv[1])
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
        print(f'{n}: [A0]{s[0]} {compress(s[1:])}')
