"""stagelog.py MACHINE k n [stages] [policy]: per-stage K-moment summary (event, far bits, rle tokens) from
far_k + [0 1^n|1|R] (R = 19 std, 2539 big); ends at the halt."""
import sys, threading
from t1lib import run, start_word, far_of, rle
M, k, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); S = int(sys.argv[4]) if len(sys.argv) > 4 else 60
pol = sys.argv[5] if len(sys.argv) > 5 else 'std'; R0 = 2539 if pol == 'big' else 19
def go():
    def cb(st, kind, d):
        if kind == 'K':
            t = rle(d[0]) if not isinstance(rle(d[0]), list) else ' '.join(map(str, rle(d[0])))
            print(f'{st:3d} ev={d[3]} far={len(d[1])} | {str(t)[:170]}', flush=True)
    kind, st, d, v = run(M, start_word([0] + [1] * n + [1, R0], far_of(k)), S, cb=cb, policy=pol, maxs=4 * 10**9)
    print('END', kind, st, d[:2] if kind == 'H' else '')
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(400000)
t = threading.Thread(target=go); t.start(); t.join()
