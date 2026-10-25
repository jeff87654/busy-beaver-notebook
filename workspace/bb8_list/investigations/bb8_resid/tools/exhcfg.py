"""exhcfg.py: run a machine from K(0^n;0;b) (template word) until it reads an undefined slot; print the tape around the head."""
import sys
def parse(m):
    T = {}
    for q, r in enumerate(m.split('_')):
        for c in (0, 1):
            x = r[3*c:3*c+3]
            T[(q, c)] = None if ('-' in x or x[2] == 'Z') else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
def run(m, word, Q, maxs=10**8):
    T = parse(m); tape = {i: int(ch) for i, ch in enumerate(word)}; pos = len(word); q = Q
    for s in range(maxs):
        c = tape.get(pos, 0); t = T[(q, c)]
        if t is None: return s, q, c, pos, tape
        tape[pos] = t[0]; pos += t[1]; q = t[2]
    return None
def show(tape, pos, w=30):
    lo = min(k for k, v in tape.items() if v) if any(tape.values()) else pos
    return ''.join(str(tape.get(i, 0)) for i in range(min(lo, pos - w), pos)) + '[' + str(tape.get(pos, 0)) + ']' + ''.join(str(tape.get(i, 0)) for i in range(pos + 1, pos + 12))
rec = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'
ch = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF'
for n, b in [(0, 0), (1, 0), (2, 1), (3, 2)]:
    wr = '1' + '011' * (n + 1) + '01' * (3 * b + 1) + '10101'
    wc = '11' + '10' * 1 * (n + 1) + '1' * 0
    wc = '11' + ''.join('10' + '1' for _ in range(n + 1)) + '10' * (3 * b + 2) + '111001'
    for name, m, w, Q in [('rec', rec, wr, 6), ('champ', ch, wc, 1)]:
        r = run(m, w, Q)
        if r: s, q, c, pos, tape = r; print(name, n, b, 'steps', s, 'state', chr(65 + q), c, show(tape, pos))
        else: print(name, n, b, 'no halt')
