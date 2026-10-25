"""Tail-context probes: token list V + the real tail, run machine TM9, report A-events with ctx 1x / halts / WHOLE.
  python tprobe.py MAXSTEPS WORKERS "V1;V2;..." """
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
TAIL = '0*6 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00 1 00> 0'
mx, wk = int(sys.argv[1]), int(sys.argv[2])
vs = sys.argv[3].split(';')


def one(v):
    w = tok2word(v + ' ' + TAIL)
    out = subprocess.run([str(HERE / 'tr9run3.exe'), M, w, str(len(w)), 'B', str(mx), 'aevents', '100000'],
                         capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    ev = [x for x in out if x.startswith('AE ')]
    bad = [x for x in ev if ' ctx 1' in x]
    whole = [x for x in ev if ' WHOLE ' in x]
    end = [x for x in out if x.startswith('HALT') or x.startswith('END')]
    s = f'[{v}]: {end[0][:40] if end else "?"} | A {len(ev)} WHOLE {len(whole)} ctx1x {len(bad)}'
    for x in (bad[:1] + whole[:1]):
        s += '\n    ' + x[:170]
    return s


with ThreadPoolExecutor(wk) as ex:
    for r in ex.map(one, vs):
        print(r, flush=True)
