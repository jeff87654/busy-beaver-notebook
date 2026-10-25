"""dctx.py: n1 from [far_K] [P.. 2 5 1^c 0^3 9 1^z | 1 | R]; at the first undefined read print the stage, the token
list (follower parse) of the stage word, and the literal neighbourhood of the read (60 cells left, 60 right).
usage: python dctx.py c P(comma) [K] [z] [policy] [M]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, far_of, N1, SUF, rle
import mf35
from sim import Sim
def go():
    c = int(sys.argv[1]); P = [int(x) for x in sys.argv[2].split(',')] if sys.argv[2] != '-' else []
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 0; z = int(sys.argv[4]) if len(sys.argv) > 4 else 29
    pol = sys.argv[5] if len(sys.argv) > 5 else 'std'; M = sys.argv[6] if len(sys.argv) > 6 else N1
    R = 19 if pol == 'std' else 2539
    word = (far_of(K) if K else '') + mf35.word_of_tokens(P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, R]) + SUF
    prev = None
    for st in range(400):
        kind, d = stage(M, word, 10**10, pol)
        if kind != 'K': break
        prev = d; word = d['newword']
    g = d.get('G'); last = [x for x in g[1] if '@' in x][-1] if g else None
    pos = int(last.split('@')[1]) if last else None
    print(f'c={c} P={P} K={K} {pol}: st={st} {kind} {d.get("slot")} at {pos}; stage-word toks: {rle(prev["toks"][:-2])[:120] if prev else ""} | far={len(prev["far"]) if prev else 0}b')
    if pos is not None and pol == 'std':
        s = Sim(M, word, q='G'); s.run(10**9)
        t = ''.join(map(str, s.t)); h = s.h
        print('   ', t[h-70:h] + '[' + s.q + ']' + t[h:h+int(__import__("os").environ.get("WIN","70"))])
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
