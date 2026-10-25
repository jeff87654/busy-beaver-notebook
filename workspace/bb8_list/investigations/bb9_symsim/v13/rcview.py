import sys, re
m = sys.argv[1]; start = sys.argv[2]; steps = int(sys.argv[3]); every = int(sys.argv[4])
T = {}
for q, r in enumerate(m.split('_')):
    for c in (0, 1):
        x = r[3*c:3*c+3]; T[(q, c)] = None if '-' in x else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
st, L, R = start.split('|'); q = ord(st[0]) - 65; f = st[1]
L = L.replace('[S]', '0110' * 3); R = R.replace('[S]', '0110' * 3)
cells = L + R; head = len(L) - 1 if f == '<' else len(L)
N = 1 << 14; off = N // 2
tape = bytearray(N); tape[off:off+len(cells)] = bytes(int(ch) for ch in cells); pos = off + head
def comp(x): return re.sub(r'((\d+?)\2{3,})', lambda g: '(' + g.group(2) + ')^' + str(len(g.group(1)) // len(g.group(2))), x)
for step in range(steps):
    if step % every == 0:
        a = off - 4; b = max(i for i in range(N) if tape[i]) + 3
        s = ''.join(map(str, tape[a:pos])) + '[' + chr(65+q) + ']' + ''.join(map(str, tape[pos:b]))
        print(step, s)
    sym = tape[pos]; tr = T[(q, sym)]
    if tr is None: print('HALT', step); break
    w, d, nq = tr; tape[pos] = w; pos += d; q = nq
