"""Targeted radius-3 start prefilter (Idle): triples of event/handler slots containing a root slot (G0 or H1).
  python run_r3.py NAME MACHINE"""
import os, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
name, m = sys.argv[1], sys.argv[2]
env = dict(os.environ, REQ='G0,H1')
with open(H / f'r3_{name}_start.txt', 'w') as out, open(H / f'r3_{name}.err', 'w') as err:
    subprocess.run([str(H / 'nbrstart3.exe'), m, '3', 'E0,G0,H0,H1,I0,I1,J0,J1', str(H / 'target_rec.txt'), 'B', '20000'],
                   stdout=out, stderr=err, env=env, creationflags=subprocess.IDLE_PRIORITY_CLASS)
