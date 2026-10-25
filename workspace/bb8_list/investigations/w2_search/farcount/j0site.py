"""j0site.py: from a round start [far_K + P 2 5 1^c 0^3 9 1^z | 1 | R], follow n1 (or M) to the first undefined read;
report the class c mod 14, the stage, and the literal head position of the read relative to the far region
(abs 0 = far's left end; far = D2^K (5K bits) + 44-bit tail).  usage: python j0site.py C0 C1 [K] [z] [M]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from ilib import stage, far_of, word_of, rle, N1, SUF
import mf35
from sim import Sim
def go():
    c0, c1 = int(sys.argv[1]), int(sys.argv[2])
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    z = int(sys.argv[4]) if len(sys.argv) > 4 else 41
    M = sys.argv[5] if len(sys.argv) > 5 else N1
    P = [int(x) for x in sys.argv[6].split(',')] if len(sys.argv) > 6 and sys.argv[6] else []
    for c in range(c0, c1 + 1):
        word = far_of(K) + mf35.word_of_tokens(P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, 19]) + SUF
        A = 0; res = None
        for st in range(60 + c):
            kind, d = stage(M, word, 4 * 10**8)
            if kind != 'K':
                res = (st, kind, d); break
            A += d['shift']; lastw = word; word = d['newword']
        if res is None:
            print(f'c={c} c%14={c%14}: MAX'); continue
        st, kind, d = res
        if kind == 'H':
            s = Sim(M, word, q='G'); r = s.run(4 * 10**8)
            wd, hpos, a = s.word()
            # absolute: word's first cell is at abs A (if far nonempty, far starts at word start)
            habs = A + (s.h - s.pad - 0)
            # locate: compute head index within current word string
            hidx = s.h - (s.pad - 0)
            print(f'c={c} c%14={c%14}: st={st} H {d["slot"]} head_abs={A + hidx} (far D2 run = [0,{5*K}), tail [{5*K},{5*K+44}))'
                  f' word_start_abs={A} curfar_len={len(word) - len(mf35.word_of_tokens([0]))}', flush=True)
        else:
            print(f'c={c} c%14={c%14}: st={st} {kind} LO={d.get("LO")}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
