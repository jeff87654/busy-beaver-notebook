"""j0big.py: n1 from far_K + [P 2 5 1^c 0^3 9 1^z | 1 | R] under a policy; print the stage and absolute position of the
first undefined read (J0) using fgstage's gadget-read list.  usage: python j0big.py c K z policy [P]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, far_of, N1, SUF
import mf35
def go():
    c, K, z, pol = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    P = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else []
    R = 19 if pol == 'std' else 2539
    word = far_of(K) + mf35.word_of_tokens(P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, R]) + SUF
    for st in range(2000):
        kind, d = stage(N1, word, 10**11, pol)
        if kind != 'K': break
        word = d['newword']
    g = d.get('G')
    print(f'c={c} c%14={c%14} K={K} pol={pol} P={P}: st={st} {kind} {d.get("slot")} reads={g[1][-3:] if g else None} '
          f'(old tail starts at {5*K}; J0 site idx = pos-{5*K}) steps={d.get("steps")}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
