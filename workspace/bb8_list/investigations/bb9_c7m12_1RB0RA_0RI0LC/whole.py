"""Whole-tape exhaustion events (A-events with only blanks to the left) in runs from K(0^n;0;b).
  TM9=... python whole.py N0 N1 B0 B1 MAXSTEPS WORKERS > out.txt"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kword import kword  # noqa: E402

M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
n0, n1, b0, b1, mx, wk = (int(x) for x in sys.argv[1:7])


def one(nb):
    n, b = nb
    w = kword([0] * n, 0, b)
    out = subprocess.run([str(HERE / 'tr9run3.exe'), M, w, str(len(w)), 'B', str(mx), 'aevents', '100000'],
                         capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    ev = [x for x in out if x.startswith('AE ')]
    whole = [x for x in ev if ' WHOLE ' in x]
    end = [x for x in out if x.startswith('HALT') or x.startswith('END')]
    s = f'n={n} b={b}: {end[0][:40] if end else "?"} | A-events {len(ev)}, WHOLE {len(whole)}'
    for x in whole[:4]:
        s += '\n    ' + x[:230]
    halts = [x for x in ev if ' ctx 1' in x]
    for x in halts[:2]:
        s += '\n    HALTCTX ' + x[:230]
    return s


with ThreadPoolExecutor(wk) as ex:
    for r in ex.map(one, [(n, b) for n in range(n0, n1 + 1) for b in range(b0, b1 + 1)]):
        print(r, flush=True)
