"""Early-halt scan of the outer exhaustion K(0^n;0;b) for machine TM9 (quiet runs, parallel, Idle).
  python hgrid.py N0 N1 B MAXSTEPS WORKERS > out.tsv   -> n, b, HALT step / RUNNING"""
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
n0, n1, b, mx, wk = (int(x) for x in sys.argv[1:6])


def one(n):
    w = kword([0] * n, 0, b)
    out = subprocess.run([str(HERE / 'tr9run3.exe'), M, w, str(len(w)), 'B', str(mx), 'quiet'], capture_output=True,
                         text=True, creationflags=LOW).stdout.splitlines()
    h = out[0]
    return f'{n}\t{b}\t' + (('HALT\t' + h.split(':')[0][10:]) if h.startswith('HALT') else 'RUNNING')


with ThreadPoolExecutor(wk) as ex:
    for r in ex.map(one, range(n0, n1 + 1)):
        print(r, flush=True)
