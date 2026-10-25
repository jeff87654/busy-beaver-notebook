"""survey.py: for every RS leaf of the given ienum/t12enum tsv files, follow from far_29 + [0 1^29|1|19] (std) for up
to 6 round starts and record the far D2 count kD2 at each restart.  Output: survey.tsv rows
machine  end  slot  st  minlo  seq(st:kD2:taillen:Plen:c:z)  flag  (flag EAT = kD2 strictly decreasing over >=3 restarts)"""
# self-Idle (lead 2026-10-10)
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)

import sys, threading, os, time, ctypes
from farfol import track
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
def go():
    out = sys.argv[1]; files = sys.argv[2:]
    done = set()
    if os.path.exists(out):
        for l in open(out): done.add(l.split('\t')[0])
    ms = []
    for f in files:
        for l in open(f):
            p = l.rstrip('\n').split('\t')
            if len(p) > 1 and (p[1].startswith('RS') or p[1].startswith('RESTART') or p[1].startswith('MAX2')) and p[0] not in done and p[0] not in ms: ms.append(p[0])
    print('machines', len(ms), flush=True)
    fo = open(out, 'a'); t0 = time.time()
    for i, M in enumerate(ms):
        try:
            o = track(M, 29, 29, nrs=6, maxst=300, maxs=10**8)
        except Exception as ex:
            fo.write(f'{M}\tERR\t{str(ex)[:50]}\n'); fo.flush(); continue
        ks = [r[1] for r in o['rs']]
        flag = 'EAT' if len(ks) >= 3 and all(ks[j+1] < ks[j] for j in range(len(ks)-1)) else ('DEC' if len(ks) >= 2 and ks[-1] < ks[0] else '')
        seq = ' '.join(f'{st}:{kd}:{rl}:{len(P)}:{c}:{z}' for st, kd, rl, P, c, z, _ in o['rs'])
        fo.write(f'{M}\t{o["end"]}\t{o["slot"] or ""}\t{o["st"]}\t{o["minlo"]}\t{seq}\t{flag}\n'); fo.flush()
        if i % 20 == 0: print(i, '%.0fs' % (time.time() - t0), flush=True)
    print('DONE', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
