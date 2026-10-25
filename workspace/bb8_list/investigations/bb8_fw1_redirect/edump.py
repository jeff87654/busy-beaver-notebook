"""edump.py TAG MACHINE A STEPS...: run MACHINE from K(;A;B0) (template frame) and print run-length tapes at the given steps."""
import idle, sys
from bcfg import *
tag, M, A = sys.argv[1], sys.argv[2], int(sys.argv[3]); stops = [int(x) for x in sys.argv[4:]]
t = T(tag); B0 = BASES[tag][2]; mir = t['o'] == 'L'
tr = {}
for q, row in enumerate(M.split('_')):
    for c in range(2):
        x = row[3*c:3*c+3]
        if x[0] != '-': d = 1 if x[1] == 'R' else -1; tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
w = word(tag, [], A, B0); tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}; pos = len(w); q = ord(t['q']) - 65
def rl():
    ks = [k for k, v in tape.items() if v]
    if not ks: return '(blank)'
    lo, hi = min(ks + [pos]), max(ks + [pos]); s = ''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1))
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append(f"{s[i]}^{j-i}" if j - i > 3 else s[i:j]); i = j
    return f"head@{pos-lo} " + ' '.join(out)
st = 0
for S in stops:
    while st < S:
        c = tape.get(pos, 0)
        if (q, c) not in tr: print('HALT', st, chr(65+q), c); sys.exit()
        W, d, nq = tr[(q, c)]; tape[pos] = W; pos += d; q = nq; st += 1
    r = rl(); print(st, chr(65+q), r[:200], " ... ", r[-150:])
