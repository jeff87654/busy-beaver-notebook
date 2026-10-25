import sys
m = sys.argv[1]; start, claimed = sys.argv[2], sys.argv[3]
T = {}
for q, r in enumerate(m.split('_')):
    for c in (0, 1):
        x = r[3*c:3*c+3]; T[(q, c)] = None if '-' in x else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
def parse(s):
    st, L, R = s.split('|'); q = ord(st[0]) - 65; f = st[1]
    L = L.replace('[S]', '0110' * 1000); R = R.replace('[S]', '0110' * 1000)
    cells = L + R
    head = len(L) - 1 if f == '<' else len(L)
    return q, cells, head
q, cells, head = parse(start)
tq, tcells, thead = parse(claimed)
N = 1 << 16; off = N // 2
tape = bytearray(N); tape[off:off+len(cells)] = bytes(int(ch) for ch in cells); pos = off + head
# the target as cells relative to the left end of the start's left part (left parts share the sentinel start)
tt = bytearray(N); tt[off:off+len(tcells)] = bytes(int(ch) for ch in tcells); tpos = off + thead
for step in range(5000000):
    if q == tq and pos == tpos and tape == tt: print('MATCH at step', step); break
    sym = tape[pos]; tr = T[(q, sym)]
    if tr is None: print('HALT', step); break
    w, d, nq = tr; tape[pos] = w; pos += d; q = nq
else:
    print('no match')
