"""btable.py: borrow table.  n1 from [D 2 5 1^c 0^3 9 1^z|1|19] (no far): at the J0 stage report the stage-start tokens,
whether a token D-d (1<=d<=12) is present (the borrow), and the J0 position relative to the digit's cells.
usage: python btable.py c0 c1 D [z]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, N1, SUF, rle
import mf35
def go():
    c0, c1, D = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); z = int(sys.argv[4]) if len(sys.argv) > 4 else 29
    for c in range(c0, c1 + 1):
        word = mf35.word_of_tokens([D, 2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, 19]) + SUF
        prev = None; kind = 'MAX'
        for st in range(30 + c):
            kind, d = stage(N1, word, 10**9)
            if kind != 'K': break
            prev = d; word = d['newword']
        if kind != 'H':
            print(f'c={c} c%14={c%14} c%42={c%42}: {kind} st={st}', flush=True); continue
        toks = prev['toks'][:-2] if prev else []
        bor = [D - t for t in toks if 1 <= D - t <= 12]
        g = d.get('G'); last = [x for x in g[1] if '@' in x][-1] if g else ''
        pos = int(last.split('@')[1]) if last else None
        print(f'c={c} c%14={c%14} c%42={c%42}: J0 st={st} at {pos} (digit cells [0,{2*D+1})) borrow={bor} far={len(prev["far"]) if prev else 0} toks={rle(toks)[:70]}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
