"""Fit one C7 cascade sub-step D0f t L P s y l -> next D0 moment, cell-exact.
D0f far-first: l 1 (10)^s 101 (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001 <B>.
python fitsub.py r  : L = 5J + c (c = 60 + r), P = 6p + 12 + E, several s, y; prints the next D0 parsed with the
old l (='11') stripped, i.e. new = PRE + l."""
import idle, subprocess, sys, re, itertools
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7_coq\tools\c7md.exe'
L0 = '1101'   # far frame stand-in ending in 1 (so the old l is recognisable)
def word(t, L, P, s, y, l=L0):
    return l + '1' + '10' * s + '101' + '10' * y + '011' + '100' * P + '1' * L + '11' + '11111100' * t + '1001'
D0 = re.compile(r'1((?:10)*)101((?:10)*)011((?:100)*)(1*)11((?:11111100)*)1001')
def nextd0(t, L, P, s, y):
    open('tmp_f.txt', 'w').write(word(t, L, P, s, y))
    out = subprocess.run([EXE, C7, 'f:tmp_f.txt', '5e8', 'noh', 'dump1'], capture_output=True, text=True, creationflags=0x40).stdout
    return out
def parse_dump(w):
    # w far-first cells, must start with L0
    assert w.startswith(L0), w[:20]
    rest = w[len(L0):]
    out = []
    for k in range(0, len(rest)):   # PRE = rest[:k], then D0 body
        m = D0.fullmatch(rest[k:])
        if m:
            out.append((rest[:k], len(m.group(1)) // 2, len(m.group(2)) // 2, len(m.group(3)) // 3, len(m.group(4)), len(m.group(5)) // 8))
    return out
def one(t, L, P, s, y):
    out = nextd0(t, L, P, s, y)
    m = re.search(r'^DUMP (\d+)$', out, re.M)
    if not m: return None
    return parse_dump(m.group(1))
if __name__ == '__main__':
    r = int(sys.argv[1]); c = int(sys.argv[2]) if len(sys.argv) > 2 else 60 + r
    for J, p, s, y in [(8, 20, 3, 9), (9, 20, 3, 9), (8, 21, 3, 9), (8, 20, 4, 9), (8, 20, 3, 10), (10, 22, 5, 12)]:
        for E in [0, 1, 2, 3, 4, 5]:
            L = 5 * J + c; P = 6 * p + 12 + E
            res = one(5, L, P, s, y)
            if res is None: print(J, p, s, y, E, 'NONE'); continue
            print('J=%d p=%d s=%d y=%d E=%d L=%d P=%d ->' % (J, p, s, y, E, L, P),
                  ' | '.join('pre=%s s=%d y=%d P=%d L=%d t=%d' % x for x in res[:3]))
