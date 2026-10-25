"""leftend.py MACHINE WORDFILE STATE MAXSTEPS [WIN=14] [MAXPRINT=120]: print the run while the head is near the left end
of the initial word (positions < WIN), with the tape window."""
import sys
from prof import parse
m, w, q0 = sys.argv[1], open(sys.argv[2]).read().strip(), sys.argv[3]
N = int(sys.argv[4]); WIN = int(sys.argv[5]) if len(sys.argv) > 5 else 14; MP = int(sys.argv[6]) if len(sys.argv) > 6 else 120
t = parse(m)
off = 1000; tape = bytearray(off) + bytearray(int(c) for c in w) + bytearray(3_000_000)
pos = off + len(w); q = ord(q0) - 65; printed = 0; last = -10
for st in range(N):
    c = tape[pos]
    if pos - off < WIN:
        if st != last + 1: print('---')
        seg = ''.join(str(x) for x in tape[off - 8: off + WIN + 6])
        print(f'{st:9d} {chr(65+q)}{c} pos={pos-off:4d} {seg[:pos-off+8]}[{seg[pos-off+8]}]{seg[pos-off+9:]}')
        printed += 1; last = st
        if printed >= MP: break
    if (q, c) not in t: print('HALT', st, chr(65+q), c); break
    wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
