"""ctl8.py: positive/negative control. C8 = old BB(7) champion with E0 -> 1LH and H = ------ (two undefined slots).
The first undefined slot reached is H0 (H is entered on a 0). Its 32 completions H0 = w d X (X in A..H; H1 stays the halt)
are followed with pkf8t (champion-engine faithful follower) in the r6 world and the W2 world. M8 = H0:1RG must show the
r6 signature 11 97 12 4374 2617 and halt in W2."""
import idle  # noqa
import subprocess, sys, os, time, re
from concurrent.futures import ThreadPoolExecutor
PK = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_topmap_all\tools\pkf8t.exe'
BASE = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_'
WORLDS = {'r6': ['--B', '6', '--rk', '1', '--rc', '20', '--cls', '6', '--mod', '360', '--maxt', '3000000000'],
          'W2': ['--B', '66', '--cls', '66', '--mod', '150', '--jumps', '1000', '--maxt', '3000000000']}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctl8')
def job(a):
    m, w = a
    f = os.path.join(OUT, f'{w}_{m}.txt')
    if os.path.exists(f) and ('HALT' in open(f).read() or 'STOP' in open(f).read()): return
    with open(f, 'w') as lf:
        p = subprocess.Popen([PK, m] + WORLDS[w], stdout=lf, stderr=subprocess.STDOUT)
        with open(os.path.join(os.path.dirname(OUT), 'pids.txt'), 'a') as pf: pf.write(f'{time.strftime("%F %T")} ctl8 child={p.pid} {m} {w}\n')
        p.wait()
ms = [BASE + f'{w}{d}{x}---' for w in '01' for d in 'LR' for x in 'ABCDEFGH']
with ThreadPoolExecutor(2) as ex: list(ex.map(job, [(m, w) for w in ('r6', 'W2') for m in ms]))
