"""j0view.py MACHINE c [z] [stages]: follow n1-world round start with counter c to the stage where an undefined slot is
read; print the literal tape around the head at that read (far part)."""
import sys, threading
from t1lib import run, start_word, rle, fark
from sim import Sim
M = sys.argv[1]; c = int(sys.argv[2]); z = int(sys.argv[3]) if len(sys.argv) > 3 else 32
def go():
    last = {}
    def cb(st, kind, d):
        last['w'] = cur[0]
        if kind == 'K': cur[0] = d[2]
    cur = [start_word([2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [1, 19])]
    kind, st, d, v = run(M, cur[0], 400, cb=cb)
    print('result', kind, st, d)
    if kind == 'H':
        w = last['w']; s = Sim(M, w, q='G'); r = s.run(10**8)
        t = ''.join(map(str, s.t)); a = t.find('1'); h = s.h
        print(r, s.q, 'head-off', h - a, 'steps', s.steps)
        print('left part :', t[a:h] + '[' + s.q + ']' + t[h:h + 60])
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
