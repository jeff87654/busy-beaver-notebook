"""chk_eat.py: re-follow EAT/NOEND leaves of an enum12 tsv from the class-12 start far_K + [2 5 1^40 0^3 9 1^29|1|19]
at several K: kD2 and class at each round start (does the far run keep shrinking, and is the eat K-independent?).
usage: python chk_eat.py TSV K1,K2,..  (undefined slots read -> reported as HALT)"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading
from farfol import track
from fl import far_of, SUF
import mf35
def go():
    rows = [l.split('\t') for l in open(sys.argv[1]) if l.split('\t')[1] in ('EAT', 'NOEND', 'RS')]
    Ks = [int(x) for x in sys.argv[2].split(',')]
    seen = set()
    for r in rows:
        M = r[0]
        if M in seen: continue
        seen.add(M)
        out = []
        for K in Ks:
            w = far_of(K) + mf35.word_of_tokens([2, 5] + [1] * 40 + [0, 0, 0, 9] + [1] * 29 + [1, 19]) + SUF
            o = track(M, nrs=6, maxst=200, maxs=10**8, start=w)
            out.append(f'K={K}: {o["end"]} {o["slot"] or ""} ' + ' '.join(f'{kd}/{c%14}' for st, kd, rl, P, c, z, _ in o['rs']))
        print(M.split('_', 9)[-1], ' | '.join(out), flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
