import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
from kcheck import parse, ktape, M1
def trace(ds, a, b, m=M1, maxn=100000, every=False):
    T = parse(m); r = ktape(ds, a, b)
    tape = {i: v for i, v in enumerate(r)}; pos = 0; q = 4; n = 0; lastd = None
    def fmt():
        lo = min(min(tape), pos); hi = max(max(tape), pos)
        while hi > pos and tape.get(hi, 0) == 0: hi -= 1
        while lo < pos and tape.get(lo, 0) == 0: lo += 1
        s = ''
        for i in range(lo, hi + 1):
            if i == pos: s += '[' + 'ABCDEFG'[q] + ']'
            s += str(tape.get(i, 0))
        return s
    print(n, fmt())
    while n < maxn:
        s = tape.get(pos, 0); tr = T[(q, s)]
        if tr is None: print('HALT', n, fmt()); return
        w, d, q2 = tr
        if every or d != lastd: print(n, fmt())
        lastd = d
        tape[pos] = w; pos += d; q = q2; n += 1
        if q == 4 and tape.get(pos,0) == 0 and all(tape.get(i,0)==0 for i in range(min(tape), pos)) and n > 2:
            print("K?", n, fmt())
trace(eval(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), every=len(sys.argv) > 4)
