"""bigend.py MACHINE k p c z policy bigk maxs stages: crafted round-2 start [2^(k-4) 1 5 p 2 5 1^c 0^3 3 1^z | 1 | U]
(U = 19 std, 2539+2520*(bigk-1) big); per-stage K summary to the end."""
import sys, threading
from t1lib import start_word, rle
from fstep import stage
M = sys.argv[1]; k, p, c, z = map(int, sys.argv[2:6]); pol = sys.argv[6]; bigk = int(sys.argv[7]); maxs = int(float(sys.argv[8])); S = int(sys.argv[9])
U = 19 if pol == 'std' else 2539 + 2520 * (bigk - 1)
def go():
    w = start_word([2] * (k - 4) + [1, 5, p, 2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [1, U])
    for st in range(S):
        kind, d = stage(M, w, maxs, pol, bigk)
        if kind != 'K': print(st, 'END', kind, d[:2] if kind == 'H' else d, flush=True); return
        t = rle(d[0]); t = t if isinstance(t, str) else ' '.join(map(str, t))
        print(st, f'ev={d[3]} far={len(d[1])} |', t[:200], '| ->', str(d[5][-1]), flush=True)
        w = d[2]
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(400000)
t = threading.Thread(target=go); t.start(); t.join()
