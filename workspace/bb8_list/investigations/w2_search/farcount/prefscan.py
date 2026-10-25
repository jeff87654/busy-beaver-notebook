"""prefscan.py: n1 (or M) from [far_K] + [D 2 5 1^c 0^3 9 1^z | 1 | R]: does the round end borrow from the prefix digit D?
prints per c: stage of the first change of the leftmost token, its new value, and the end (H slot / MAX) with tokens.
usage: python prefscan.py c0 c1 D [K] [z] [M] [policy]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, far_of, N1, SUF, rle
import mf35
def go():
    c0, c1, D = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 0; z = int(sys.argv[5]) if len(sys.argv) > 5 else 29
    M = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '-' else N1; pol = sys.argv[7] if len(sys.argv) > 7 else 'std'
    for c in range(c0, c1 + 1):
        far = far_of(K) if K else ''
        word = far + mf35.word_of_tokens([D, 2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, 19 if pol == 'std' else 2539]) + SUF
        ch = None; last = None
        for st in range(80 + c):
            kind, d = stage(M, word, 10**9, pol)
            if kind != 'K': break
            toks = d['toks']
            if ch is None and toks and toks[0] != D:
                ch = (st, rle(toks[:-2])[:80])
            last = toks; word = d['newword']
        print(f'c={c} c%14={c%14}: end={kind} {d.get("slot","")} st={st} firstchange={ch} last={rle(last[:-2])[:90] if last else None}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
