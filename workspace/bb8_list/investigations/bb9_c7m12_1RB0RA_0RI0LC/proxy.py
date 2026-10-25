"""Long proxy runs of a machine from the inner exhaustion J_B(0*,0,0,0;0;c) (and other starts), quiet mode.
  TM9=... python proxy.py MAXSTEPS WORKERS B1,B2,.. c1,c2,..  -> one line per (B,c): HALT step/ones or END."""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from exh_check import J  # noqa: E402

M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
mx, workers = int(sys.argv[1]), int(sys.argv[2])
Bs = [int(x) for x in sys.argv[3].split(',')]
cs = [int(x) for x in sys.argv[4].split(',')]


def one(Bc):
    B, c = Bc
    w = J(B, 0, [0, 0, 0], 0, c)
    out = subprocess.run([str(HERE / 'tr9run2.exe'), M, w, str(len(w)), 'B', str(mx), 'quiet'], capture_output=True,
                         text=True, creationflags=LOW).stdout.splitlines()
    return f'B={B} c={c}: {out[0][:110]}'


with ThreadPoolExecutor(workers) as ex:
    for r in ex.map(one, [(B, c) for B in Bs for c in cs]):
        print(r, flush=True)
