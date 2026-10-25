"""Dead-end E0 events (context other than the G0-emulation context 01) for K(0^n;0;b), any machine.
  TM9=MACHINE python degrid.py N0 N1 B0 B1 MAXSTEPS
Prints per (n,b): outcome (HALT step / END), number of dead-end events by context, first events' steps."""
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kword import kword  # noqa: E402

M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
n0, n1, b0, b1, mx = (int(x) for x in sys.argv[1:6])
for n in range(n0, n1 + 1):
    for b in range(b0, b1 + 1):
        w = kword([0] * n, 0, b)
        out = subprocess.run([str(HERE / 'tr9run.exe'), M, w, str(len(w)), 'B', str(mx), 'deadend', '1000000'],
                             capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
        de = [x for x in out if x.startswith('DE ')]
        cnt = Counter(x.split()[3] for x in de)
        end = [x for x in out if x.startswith('HALT') or x.startswith('END')]
        e = end[0].split(':')[0] if end else '?'
        firsts = ' '.join(f'{x.split()[1]}:{x.split()[3]}' for x in de[:6])
        print(f'{n}\t{b}\t{e}\t{dict(cnt)}\t{firsts}', flush=True)
