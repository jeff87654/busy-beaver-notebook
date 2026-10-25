"""ptest.py POLICY N 'P1' 'P2' ...: restart counter after no-far list [P 1^N | 1 | 19] in n1 (policy std|big)."""
import sys, threading
from t1lib import N1, run, start_word, rsig, rle
pol = sys.argv[1]; N = int(sys.argv[2])
def go():
    for ps in sys.argv[3:]:
        P = [int(x) for x in ps.split()]
        R = 19 if pol == 'std' else 2539
        def cb(st, kind, d):
            if kind == 'K':
                s = rsig(d[0][:-2])
                if s and not d[1]: return s
        kind, st, d, v = run(N1, start_word(P + [1] * N + [1, R]), 40, policy=pol, cb=cb, maxs=10**9)
        print(ps, '->', (f'c={v[1]} P2={v[0]} z={v[2]} st={st}' if v else f'{kind} st={st}'), flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
