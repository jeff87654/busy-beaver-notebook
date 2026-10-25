import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
from kcheck import parse, ktape
M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
want = ktape([1]*20, 1, 2)
for m in (M1, M2):
    T = parse(m); tape = {}; pos = 0; q = 0; n = 0
    while n < 20000:
        if q == 4 and tape.get(pos,0) == 0 and all(v == 0 for i, v in tape.items() if i < pos):
            hi = max(tape); cells = [tape.get(i, 0) for i in range(pos, hi + 1)]
            while cells and cells[-1] == 0: cells.pop()
            if cells == want: print(m, 'Kc(1^20;1;2) at step', n); break
        s = tape.get(pos, 0); w, d, q2 = T[(q, s)]; tape[pos] = w; pos += d; q = q2; n += 1
