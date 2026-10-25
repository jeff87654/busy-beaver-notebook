import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
from kcheck import parse
from rle import rle
M = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
T = parse(M); tape = {}; pos = 0; q = 0
lo = int(sys.argv[1]); hi_ = int(sys.argv[2]); ev = sys.argv[3].split(',')
for n in range(hi_):
    s = tape.get(pos, 0)
    if n >= lo and ('ABCDEFG'[q] + str(s)) in ev:
        a = min(min(tape), pos); b = max(max(tape), pos)
        L = [tape.get(i,0) for i in range(a, pos)]; R = [tape.get(i,0) for i in range(pos+1, b+1)]
        print(n, rle(L), '[' + 'ABCDEFG'[q] + str(s) + ']', rle(R))
    w, d, q2 = T[(q, s)]; tape[pos] = w; pos += d; q = q2
