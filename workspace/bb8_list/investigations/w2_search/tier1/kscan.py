"""kscan.py MACHINE K0 K1 [n] [stages]: eater outcome from far_k + [0 1^n|1|19] for each k: first restart (c, delta) or
halt/junk within the stage cap (phase-1 only, plus the round-2 outcome if --two)."""
import sys, threading
from t1lib import run, start_word, far_of, rsig
M = sys.argv[1]; k0, k1 = int(sys.argv[2]), int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 41
S = int(sys.argv[5]) if len(sys.argv) > 5 else 30
import os; POL = os.environ.get("POL", "std"); R0 = 2539 if POL == "big" else 19
def go():
    for k in range(k0, k1 + 1):
        rs = []
        def cb(st, kind, d):
            if kind == 'K':
                s = rsig(d[0][:-2])
                if s and not d[1] and s[1] >= 40:
                    rs.append((s[1], st)); return 1
        kind, st, d, v = run(M, start_word([0] + [1] * n + [1, R0], far_of(k)), S, cb=cb, policy=POL, maxs=2*10**9)
        out = f'RESTART c={rs[0][0]} d={rs[0][0]-79} @{rs[0][1]}' if rs else f'{kind} st={st} {d[:2] if kind == "H" else ""}'
        print(f'k={k} k%3={k%3} k%4={k%4}: {out}', flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
