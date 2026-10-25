"""cfgat.py N: config after N steps from blank: prints 'word headpos state' (word from leftmost 1 or head)"""
import sys
from tailvisit import T
N = int(sys.argv[1]); tape = {}; p = 0; q = 'A'
for _ in range(N):
    c = tape.get(p, 0); t = T[(q, c)]; tape[p] = t[0]; p += t[1]; q = t[2]
ks = [k for k, v in tape.items() if v] + [p]
lo, hi = min(ks), max(ks)
print(''.join(str(tape.get(k, 0)) for k in range(lo, hi + 1)), p - lo, q)
