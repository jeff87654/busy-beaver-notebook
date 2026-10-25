import idle  # noqa
import sys
M = sys.argv[1]; n = int(sys.argv[2]); b = int(sys.argv[3]); steps = int(sys.argv[4]); every = int(sys.argv[5])
tr = {}
for q, blk in enumerate(M.split('_')):
    for c in range(2):
        t = blk[3*c:3*c+3]
        tr[(q, c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
w = '110' + '0' * n + '0' + '1' * b
tape = {i: int(ch) for i, ch in enumerate(w)}
p = len(w); q = 0  # state A on blank right of S (S empty)
def rle(s):
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append(s[i] + ('^%d' % (j - i) if j - i > 3 else s[i] * (j - i - 1))); i = j
    return ' '.join(out)
for st in range(steps):
    c = tape.get(p, 0)
    t = tr[(q, c)]
    if t is None:
        print('HALT', st); break
    tape[p] = t[0]; p += t[1]; q = t[2]
    if st % every == 0:
        ks = [k for k, v in tape.items() if v]
        lo, hi = min(ks), max(ks)
        s = ''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1))
        print(st, 'ABCDEFG'[q], p - lo, rle(s)[:300])
