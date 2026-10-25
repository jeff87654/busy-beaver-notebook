"""Report the steps where the tape is  blank [A0] 0 (100)^j 1010 (110)^k R  (bounce phase, L0 pattern)."""
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
pat = re.compile(r'^00((?:100)*)1010((?:110)*)(.*)$')
maxsteps = int(sys.argv[1])
for n in range(1, maxsteps + 1):
    tr = T[st][tape[pos]]
    w, d, st = tr
    tape[pos] = w
    pos += d
    if pos < minp: minp = pos
    if pos > maxp: maxp = pos
    if st == 0 and tape[pos] == 0 and not any(tape[minp:pos]):
        hi = maxp
        while hi > pos and tape[hi] == 0: hi -= 1
        s = ''.join('1' if c else '0' for c in tape[pos:hi + 1])
        m = pat.match(s)
        if m:
            print(f'{n}: j={len(m.group(1))//3} k={len(m.group(2))//3} R={m.group(3)}  (left used cells: {pos-minp})')
