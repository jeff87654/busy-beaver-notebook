"""First outer conversion of the c35 exception: event from  P X D3 D1^(Z-2) D0 D0 D2 D1 | 0 | r  (the state after
the inner hydra dies, from c35ev runs, event 21) for a grid of Z, X and r.  python conv_scan.py"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('EVTEXE', 'evt2.exe'); os.environ.setdefault('JSTOP', '1')
import c35ev
P = [2, 1, 1, 0, 2, 1, 0, 1]
for r in (6, 18, 42, 90):
    for X in (147,):
        for Z in range(6, 61, 2):
            ts = P + [X, 3] + [1] * (Z - 2) + [0, 0, 2, 1]
            kind, line, _ = c35ev.event(c35ev.M2, ts, r, 'G', 200_000_000)
            out = c35ev.fmt(c35ev.lock_list(line)[len(P):]) if kind == 'J' else line[:120]
            print(f'r={r:<3} X={X} Z={Z:<3} {kind} {out}', flush=True)
