"""Halting check from the real end-of-list configuration: digit D(6139) exhausted (-> D1), accumulator D(X).
  python endhalt.py ENDTOKS_FILE X1,X2,... [MACHINE]"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from tok2word import tok2word  # noqa: E402

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
s = open(sys.argv[1]).read().strip()
xs = [int(x) for x in sys.argv[2].split(',')]
M = sys.argv[3] if len(sys.argv) > 3 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---'
for X in xs:
    t = re.sub(r' 4 2\*2 (\d+) 1 2 ', f' 4 2*2 1 1 {X} ', s, count=1)
    w = tok2word(t)
    out = subprocess.run([str(HERE / 'tr9run3.exe'), M, w, str(len(w)), 'B', '3000000000', 'aevents', '100'],
                         capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    ev = [x for x in out if x.startswith('AE ')]
    end = [x for x in out if x.startswith('HALT') or x.startswith('END')][0]
    ones = int(end.split('ones ')[1].split(',')[0])
    print(f'X={X}: {end[:60]} | A-events {len(ev)} first {ev[0][:60] if ev else ""} | ones {ones}', flush=True)
