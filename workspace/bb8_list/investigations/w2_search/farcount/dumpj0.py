"""dumpj0.py: like j0site but prints the literal tape around the undefined read (abs coords; far left end = 0).
usage: python dumpj0.py c K z [M] [P]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from ilib import stage, far_of, N1, SUF
import mf35
from sim import Sim
def go():
    c, K, z = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    M = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else N1
    P = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else []
    word = far_of(K) + mf35.word_of_tokens(P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, 19]) + SUF
    for st in range(200):
        kind, d = stage(M, word, 4 * 10**8)
        if kind != 'K': break
        word = d['newword']
    s = Sim(M, word, q='G'); r = s.run(4 * 10**8)
    t = ''.join(map(str, s.t)); base = s.pad
    a = t.find('1')
    print('stage', st, kind, d.get('slot'), 'head', s.h - base, 'state', s.q, 'leftmost1', a - base)
    lo = min(a, s.h) ; hi = t.rfind('1')
    seg = t[lo:s.h] + '[' + s.q + ']' + t[s.h:min(hi + 1, s.h + 400)]
    print('from abs', lo - base); print(seg)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
