"""prefix_table.py: n1 base from a no-far list [P 1^N | 1 | 19] (P = small digit prefix left by an eater):
which round start (counter c) follows?  delta = c - 79.  usage: python prefix_table.py MAXLEN MAXDIGIT [N] [policy]"""
import sys, threading, itertools
from t1lib import N1, run, start_word, rsig, rle
L, D = int(sys.argv[1]), int(sys.argv[2]); N = int(sys.argv[3]) if len(sys.argv) > 3 else 329
pol = sys.argv[4] if len(sys.argv) > 4 else 'std'
def go():
    for l in range(1, L + 1):
        for P in itertools.product(range(D + 1), repeat=l):
            def cb(st, kind, d):
                if kind == 'K':
                    s = rsig(d[0][:-2])
                    if s and not d[1]:
                        return s
            kind, st, d, v = run(N1, start_word(list(P) + [1] * N + [1, 19]), 40, policy=pol, cb=cb)
            if v:
                Pq, c, z = v
                print(f'P={" ".join(map(str, P))}\tRESTART\tc={c}\tc%42={c % 42}\tdelta={c - 79}\tP2={" ".join(map(str, Pq))}\tz={z}\tst={st}', flush=True)
            else:
                print(f'P={" ".join(map(str, P))}\t{kind}\tst={st}\t{str(d[:2]) if kind == "H" else ""}', flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
