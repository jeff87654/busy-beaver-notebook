"""Radius-2 start prefilter for looper parents (Idle).  python run_r2.py"""
import subprocess
from pathlib import Path
H = Path(__file__).resolve().parent
LOW = subprocess.IDLE_PRIORITY_CLASS
jobs = [('c35a', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LB0LC_1RG1LD_0RI0RH_1RG1LF_0LB0RJ_0LE---', 'target_c35.txt', 'G', '30000'),
        ('c35b', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_1RG1LD_0LI0RH_1RG1LF_0RC1RE_---1LI', 'target_c35.txt', 'G', '30000'),
        ('C28', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---0RJ_0LB0RJ', 'target_rec.txt', 'B', '20000'),
        ('C29', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---1RJ_0LD1RJ', 'target_rec.txt', 'B', '20000'),
        ('C32', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_1RI0RE_0LJ0RI_1LD---', 'target_rec.txt', 'B', '20000')]
procs = []
for name, m, t, q, st in jobs:
    out = open(H / f'r2_{name}_start.txt', 'w')
    procs.append(subprocess.Popen([str(H / 'nbrstart.exe'), m, '2', 'all', str(H / t), q, st], stdout=out,
                                  stderr=open(H / f'r2_{name}.err', 'w'), creationflags=LOW))
for p in procs:
    p.wait()
