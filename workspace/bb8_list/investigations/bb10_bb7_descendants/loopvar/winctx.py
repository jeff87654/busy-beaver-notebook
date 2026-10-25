"""winctx.py MACHINE R WORD:STATE:STEPS[:SKIP] ... : (state, tape window of radius R) contexts of the LAST run never seen in
the other runs; prints the first few with their step numbers."""
import sys
from prof import parse
m, R = sys.argv[1], int(sys.argv[2])
t = parse(m)
sets = []
for spec in sys.argv[3:]:
    parts = spec.split(':'); wf, q0, N = parts[:3]; N = int(N); SKIP = int(parts[3]) if len(parts) > 3 else 0
    w = open(wf).read().strip() if wf != '-' else ''
    off = 3_000_000; tape = bytearray(off) + bytearray(int(c) for c in w) + bytearray(6_000_000)
    pos = off + len(w); q = ord(q0) - 65
    seen = {}
    for st in range(N):
        c = tape[pos]
        key = (q, bytes(tape[pos-R:pos+R+1]))
        if st >= SKIP and key not in seen: seen[key] = (st, pos - off)
        if (q, c) not in t: break
        wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
    sets.append(seen)
last = sets[-1]; other = set().union(*[set(s) for s in sets[:-1]])
new = sorted((v, k) for k, v in last.items() if k not in other)
print(f'R={R}: {len(new)} new contexts of {len(last)}')
for (st, p), (q, win) in new[:12]:
    print(f'  step {st} pos {p} {chr(65+q)} {win[:R].hex() if False else "".join(str(x) for x in win[:R])}[{win[R]}]{"".join(str(x) for x in win[R+1:])}')
