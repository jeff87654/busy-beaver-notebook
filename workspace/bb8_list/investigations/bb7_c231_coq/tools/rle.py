import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
from kcheck import parse, ktape, M1
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
def rle(cells):
    out = []; i = 0
    while i < len(cells):
        j = i
        while j < len(cells) and cells[j] == cells[i]: j += 1
        out.append(f"{cells[i]}^{j-i}" if j - i > 1 else str(cells[i])); i = j
    return ' '.join(out)
def go(ds, a, b, m=M1, events=('F0',), maxn=10**6):
    T = parse(m); r = ktape(ds, a, b)
    tape = {i: v for i, v in enumerate(r)}; pos = 0; q = 4; n = 0
    while n < maxn:
        s = tape.get(pos, 0); tr = T[(q, s)]
        lo = min(min(tape), pos); hi = max(max(tape), pos)
        while hi > pos and tape.get(hi, 0) == 0: hi -= 1
        while lo < pos and tape.get(lo, 0) == 0: lo += 1
        L = [tape.get(i, 0) for i in range(lo, pos)]; R = [tape.get(i, 0) for i in range(pos + 1, hi + 1)]
        ev = 'ABCDEFG'[q] + str(s)
        if ev in events or tr is None:
            print(f"{n:6d} {rle(L)} [{'ABCDEFG'[q]}{s}] {rle(R)}")
        if tr is None: return
        w, d, q2 = tr
        tape[pos] = w; pos += d; q = q2; n += 1
        if q == 4 and tape.get(pos,0) == 0 and all(tape.get(i,0)==0 for i in range(min(tape), pos)) and n > 2:
            print('K', n); return
if __name__ == '__main__':
    m = M2 if '232' in sys.argv else M1
    ev = tuple(sys.argv[4].split(',')) if len(sys.argv) > 4 else ('F0',)
    go(eval(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), m, ev)
