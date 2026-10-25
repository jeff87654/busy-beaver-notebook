"""ttrace.py: n1/M stage-by-stage token trace from [far_K] [P 2 5 1^c 0^3 9 1^z | 1 | R].  usage: ttrace.py c P K z pol S [M]"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from fl import stage, far_of, N1, SUF, rle, rsig
import mf35
def go():
    c = int(sys.argv[1]); P = [int(x) for x in sys.argv[2].split(',')] if sys.argv[2] != '-' else []
    K = int(sys.argv[3]); z = int(sys.argv[4]); pol = sys.argv[5]; S = int(sys.argv[6]); M = sys.argv[7] if len(sys.argv) > 7 else N1
    R = 19 if pol == 'std' else 2539
    word = (far_of(K) if K else '') + mf35.word_of_tokens(P + [2, 5] + [1] * c + [0, 0, 0, 9] + [1] * z + [1, R]) + SUF
    A = 0
    for st in range(S):
        kind, d = stage(M, word, 10**10, pol)
        g = d.get('G'); gs = ''
        if g and g[0]: gs = f' G{g[0]}:' + ' '.join(x for x in g[1][:6]) + (' .. ' + ' '.join(x for x in g[1][-4:]) if len(g[1]) > 6 else '')
        if kind != 'K': print(st, kind, d.get('slot'), 'LO', d.get('LO'), gs); return
        r = rsig(d['toks'])
        print(f'{st}: far={len(d["far"])}b LO={d["LO"]} {rle(d["toks"][:-2])[:110]} | {d["toks"][-2]} {d["toks"][-1]} ev={d.get("ev")}' + (f' RSIG c={r[1]}/{r[1]%14}' if r else '') + gs, flush=True)
        word = d['newword']
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
