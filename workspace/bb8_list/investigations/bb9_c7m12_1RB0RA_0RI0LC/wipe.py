"""Runs of machine TM9 from K-template token lists (e.g. 'L=4 2 1 1' + b), quiet + A-event summary.
  python wipe.py MAXSTEPS WORKERS "list1;list2;..." b1,b2,..."""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from tok2word import tok2word  # noqa: E402

M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
mx, wk = int(sys.argv[1]), int(sys.argv[2])
lists = sys.argv[3].split(';')
bs = [int(x) for x in sys.argv[4].split(',')]


def one(lb):
    L, b = lb
    w = tok2word(f'0*2 {L} <(10)^{3 * b + 2} 111001>')
    out = subprocess.run([str(HERE / 'tr9run3.exe'), M, w, str(len(w)), 'B', str(mx), 'aevents', '100000'],
                         capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    ev = [x for x in out if x.startswith('AE ')]
    whole = [x for x in ev if ' WHOLE ' in x]
    bad = [x for x in ev if ' ctx 1' in x]
    end = [x for x in out if x.startswith('HALT') or x.startswith('END')]
    s = f'[{L}] b={b}: {end[0][:45] if end else "?"} | A {len(ev)} WHOLE {len(whole)} ctx1x {len(bad)}'
    for x in whole[:3]:
        s += '\n    ' + x[:150]
    return s


with ThreadPoolExecutor(wk) as ex:
    for r in ex.map(one, [(L, b) for L in lists for b in bs]):
        print(r, flush=True)
