import sys
from tm import parse
from probe_e import craft3, CORE

gap = int(sys.argv[1]); p, a, c, d, e = map(int, sys.argv[2:7]); N = int(sys.argv[7])
T = parse(CORE)
tape, pos = craft3(p, a, c, d, e, gap=gap)
q = 'A'
lo = min(tape); hi = max(tape)
for s in range(1, N + 1):
    sym = tape.get(pos, 0)
    t = T[ord(q) - 65][sym]
    if s <= 120 or s % 200 == 0:
        lo = min([lo, pos]); hi = max([hi, pos])
        w = ''.join(str(tape.get(k, 0)) for k in range(lo - 2, hi + 3))
        print(f"{s:5d} q={q} sym={sym} pos={pos-lo+2:3d} {w}")
    if t is None or t[2] == 'Z':
        print('HALT', s); break
    w, mv, nq = t
    tape[pos] = w; pos += mv; q = nq
else:
    print('after', N, 'steps tape:')
    lo = min([min(tape), pos]); hi = max([max(tape), pos])
    print(''.join(str(tape.get(k, 0)) for k in range(lo - 2, hi + 3)))
