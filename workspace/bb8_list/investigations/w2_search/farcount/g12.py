"""g12.py: trace M from the class-12 end start (far_K + [P 2 5 1^c 0^3 9 1^z|1|R]) stage by stage (kD2, tokens, RSIG,
gadget reads).  usage: python g12.py M K c z S [P] [policy]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, rsig, far_of, rle, SUF, N1
from farfol import fark
import mf35
def go():
    M = sys.argv[1]; K, c, z, S = map(int, sys.argv[2:6])
    P = [int(x) for x in sys.argv[6].split(',')] if len(sys.argv) > 6 and sys.argv[6] != '-' else []
    pol = sys.argv[7] if len(sys.argv) > 7 else 'std'; R = 19 if pol == 'std' else 2539
    word = (far_of(K) if K else '') + mf35.word_of_tokens(P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, R]) + SUF
    for st in range(S):
        kind, d = stage(M, word, 10**10, pol)
        g = d.get('G'); gs = ''
        if g and g[0]:
            xs = [x for x in g[1] if '@' in x]
            gs = f' G{g[0]}:' + ' '.join(xs[:8]) + (' .. ' + ' '.join(xs[-4:]) if len(xs) > 8 else '')
        if kind != 'K': print(st, kind, d.get('slot'), gs); return
        kd, rest = fark(d['far']); r = rsig(d['toks'])
        print(f'{st}: kD2={kd} rest={len(rest)} LO={d["LO"]} {rle(d["toks"][:-2])[:110]} | {d["toks"][-2]} {d["toks"][-1]}' + (f' RSIG c={r[1]}/{r[1]%14} P={rle(list(r[0]))[:50]}' if r else '') + gs, flush=True)
        word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
