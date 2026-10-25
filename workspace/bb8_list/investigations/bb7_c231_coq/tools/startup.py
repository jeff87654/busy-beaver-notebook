import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
from kcheck import parse
from rle import rle
M = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
T = parse(M); tape = {}; pos = 0; q = 0
for n in range(3716):
    s = tape.get(pos, 0)
    if q == 4 and s == 0 and all(v == 0 for i, v in tape.items() if i < pos):
        hi = max(tape); cells = [tape.get(i,0) for i in range(pos, hi+1)]
        print(n, '[E]', rle(cells))
    w, d, q2 = T[(q, s)]; tape[pos] = w; pos += d; q = q2
