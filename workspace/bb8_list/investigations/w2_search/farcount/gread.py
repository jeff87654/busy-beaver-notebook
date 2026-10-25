"""gread.py: follow M from far_k + [0 1^n|1|R] and print per stage: kD2, tail length, tokens, RSIG, and the gadget reads
(states >= J) with ABSOLUTE positions (abs 0 = far's left end).  usage: python gread.py M k n stages [policy] [R]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, rsig, far_of, word_of, rle, SUF
from farfol import fark
def go():
    M = sys.argv[1]; k = int(sys.argv[2]); n = int(sys.argv[3]); S = int(sys.argv[4])
    pol = sys.argv[5] if len(sys.argv) > 5 else 'std'; R = int(sys.argv[6]) if len(sys.argv) > 6 else 19
    word = far_of(k) + word_of([0] + [1] * n + [1, R]) + SUF; A = 0
    for st in range(S):
        kind, d = stage(M, word, 10**9, pol)
        g = d.get('G')
        gs = '' if not g or g[0] == 0 else f' G[{g[0]}]: ' + ' '.join(f'{x.split("@")[0]}@{A + int(x.split("@")[1])}' for x in g[1][:24] if '@' in x)
        if kind != 'K':
            print(st, kind, d.get('slot'), gs); return
        kd, rest = fark(d['far'])
        r = rsig(d['toks'])
        tag = f' RSIG c={r[1]}/{r[1]%14} z={r[2]} P={rle(list(r[0]))[:40]}' if r else ''
        print(f'{st}: kD2={kd} tail={len(rest)} {rle(d["toks"][:-2])[:100]} | {d["toks"][-2]} {d["toks"][-1]}{tag}{gs}', flush=True)
        A += d['shift']; word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
