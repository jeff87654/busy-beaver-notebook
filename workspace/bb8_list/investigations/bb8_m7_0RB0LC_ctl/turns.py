"""turns.py WORD NSTEPS [from]: print tape with head marker at each direction change"""
import sys
from tailvisit import T
def show(tape, p, q, lo, hi):
    s = ''
    for k in range(lo, hi+1):
        c = str(tape.get(k, 0))
        s += f'[{q}{c}]' if k == p else c
    return s
w = sys.argv[1]; N = int(sys.argv[2]); fr = int(sys.argv[3]) if len(sys.argv) > 3 else 0
tape = {i: int(c) for i, c in enumerate(w)}; p = len(w); q = 'B'; lastd = 0
for st in range(N):
    c = tape.get(p, 0); t = T[(q, c)]
    if t is None: print('HALT', st); break
    d = t[1]
    if d != lastd and st >= fr:
        ks = [k for k, v in tape.items() if v]; lo = min(ks + [p]); hi = max(ks + [p])
        print(f'{st:7d} {"R" if d>0 else "L"} ' + show(tape, p, q, lo, hi))
    lastd = d
    tape[p] = t[0]; p += d; q = t[2]
