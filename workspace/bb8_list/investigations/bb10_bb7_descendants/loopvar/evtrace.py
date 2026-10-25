"""evtrace.py MACHINE WORDFILE STATE MAXSTEPS TRANS[,TRANS..] [CTX=12] [MAX=40]: print each use of the given transitions
with the tape context around the head (positions relative to the word's left end)."""
import sys
from prof import parse
m, w, q0, N = sys.argv[1], open(sys.argv[2]).read().strip(), sys.argv[3], int(sys.argv[4])
watch = set(sys.argv[5].split(',')); CTX = int(sys.argv[6]) if len(sys.argv) > 6 else 12; MX = int(sys.argv[7]) if len(sys.argv) > 7 else 40
t = parse(m)
off = 3_000_000; tape = bytearray(off) + bytearray(int(c) for c in w) + bytearray(6_000_000)
pos = off + len(w); q = ord(q0) - 65; n = 0
lo = off
for st in range(N):
    c = tape[pos]
    k = chr(65+q)+str(c)
    if k in watch:
        seg = ''.join(str(x) for x in tape[pos-CTX:pos]) + '[' + str(c) + ']' + ''.join(str(x) for x in tape[pos+1:pos+CTX+1])
        print(f'{st:10d} {k} pos={pos-off:6d} {seg}'); n += 1
        if n >= MX: break
    if (q, c) not in t: print('HALT', st, k); break
    wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
