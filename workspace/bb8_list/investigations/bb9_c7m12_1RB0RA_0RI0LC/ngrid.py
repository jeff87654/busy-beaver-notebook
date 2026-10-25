"""Literal outcome of the list-exhausted configuration K(0^n; 0; b) for a range of n and b.
  python ngrid.py N0 N1 B0 B1 MAXSTEPS > out.tsv
Prints n, b, HALT step / ones, or the token view (dtok) of the tape at MAXSTEPS."""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kword import kword  # noqa: E402

M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0RE0LG_---1LF')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
n0, n1, b0, b1, mx = (int(x) for x in sys.argv[1:6])
for n in range(n0, n1 + 1):
    for b in range(b0, b1 + 1):
        w = kword([0] * n, 0, b)
        out = subprocess.run([str(HERE / 'tr9run.exe'), M, w, str(len(w)), 'B', str(mx), 'quiet'], capture_output=True,
                             text=True, creationflags=LOW).stdout.strip().splitlines()
        hdr = out[0]
        if hdr.startswith('HALT'):
            print(f'{n}\t{b}\tHALT\t{hdr.split(":")[0][10:]}\t{hdr.split("ones ")[1].split(",")[0]}', flush=True)
        else:
            tok = subprocess.run([sys.executable, str(HERE / 'dtok.py'), '11111111001001', '160'], input='\n'.join(out),
                                 capture_output=True, text=True).stdout.strip()
            print(f'{n}\t{b}\tRUNNING\t{mx}\t{tok[-160:]}', flush=True)
