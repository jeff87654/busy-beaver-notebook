"""survey2.py: like survey.py but records the prefix P (last 4 tokens) at each restart and flags DIG when the token
adjacent to '2 5' (P[-1]) strictly decreases over >= 3 consecutive restarts (a prefix-digit outer counter).
usage: python survey2.py OUT.tsv TREE.tsv..."""
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
            if len(p) > 1 and (p[1].startswith('RS') or p[1].startswith('RESTART') or p[1].startswith('MAX2') or p[1] == 'NOEND') and p[0] not in done and p[0] not in ms:
                ms.append(p[0])
    print('machines', len(ms), flush=True)
    fo = open(out, 'a'); t0 = time.time()
    for i, M in enumerate(ms):
        try:
            o = track(M, 29, 29, nrs=6, maxst=300, maxs=10**8)
        except Exception as ex:
            fo.write(f'{M}\tERR\t{str(ex)[:50]}\n'); fo.flush(); continue
        adj = [r[3][-1] if r[3] else -1 for r in o['rs']]
        dec = sum(1 for j in range(1, len(adj)) if 0 <= adj[j] < adj[j - 1])
        flag = 'DIG' if dec >= 2 else ''
        seq = ' '.join(f'{st}:{kd}:{".".join(map(str, P[-4:]))}:{c}:{z}' for st, kd, rl, P, c, z, _ in o['rs'])
        fo.write(f'{M}\t{o["end"]}\t{o["slot"] or ""}\t{o["st"]}\t{seq}\t{flag}\n'); fo.flush()
        if i % 50 == 0: print(i, '%.0fs' % (time.time() - t0), flush=True)
    print('DONE', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
