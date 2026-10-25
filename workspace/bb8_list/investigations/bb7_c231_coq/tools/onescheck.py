import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
from kcheck import parse, ktape
M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
def U0(x): return 3*x+9
def halt_ones(m, ds, a, b):
    T = parse(m); r = ktape(ds, a, b); tape = {i: v for i, v in enumerate(r)}; pos = 0; q = 4; n = 0
    while True:
        s = tape.get(pos, 0); tr = T[(q, s)]
        if tr is None: return n, sum(tape.values()), 'ABCDEFG'[q], s
        w, d, q2 = tr; tape[pos] = w; pos += d; q = q2; n += 1
for m in (M1, M2):
    for ds, a, b, B in [([1], 0, 2, U0(2)), ([2], 0, 1, U0(U0(1))), ([3], 0, 0, U0(U0(U0(0)))), ([0,0,0], 0, 5, 5), ([1], 2, 0, U0(6))]:
        n, o, q, s = halt_ones(m, ds, a, b)
        print(m[-6:], ds, a, b, 'halt', q, s, 'steps', n, 'ones', o, 'pred 2B+7 =', 2*B+7, 'OK' if o == 2*B+7 else 'MISMATCH')
