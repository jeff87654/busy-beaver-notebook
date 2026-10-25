"""Exhaustion probes for dlscan2-template machines (thread 3).
  python kprobe.py MACHINE TEMPLATE "ds" a b MAXSTEPS [evt options]
TEMPLATE like R,A,P=101,u=10,s=1,d=2d+1,b=2b+0,S=-  (orientation R only).
K(ds; a; b) = P (u^(al*d+be) s) for each d in ds, then (u^(al*a+be) s), then u^(alB*b+beB), then S; the head is on
the blank right of the word in state Q.  Prints the evt.exe event view (canonical state Q)."""
import re
import subprocess
import sys
import tempfile
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRX = re.compile(r'([LR]),([A-P]),P=([01-]*),u=([01]+),s=([01]+),d=(\d+)d\+(\d+),b=(\d+)b\+(\d+),S=([01-]*)$')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


def kword(tpl, ds, a, b):
    g = TRX.match(tpl)
    if not g or g.group(1) != 'R':
        raise SystemExit(f'unsupported template {tpl}')
    _, q, P, u, s, al, be, alB, beB, S = g.groups()
    P = '' if P == '-' else P
    S = '' if S == '-' else S
    al, be, alB, beB = int(al), int(be), int(alB), int(beB)
    w = P
    for d in list(ds) + [a]:
        w += u * (al * d + be) + s
    w += u * (alB * b + beB) + S
    return w, q


def run(m, tpl, ds, a, b, maxsteps, opts):
    w, q = kword(tpl, ds, a, b)
    fd, path = tempfile.mkstemp(suffix='.txt')
    with os.fdopen(fd, 'w') as f:
        f.write(w)
    try:
        r = subprocess.run([str(HERE.parent / 'evt.exe'), m, path, str(len(w)), q, str(maxsteps), '-q', q, *opts],
                           capture_output=True, text=True, creationflags=LOW)
    finally:
        os.unlink(path)
    return r.stdout


if __name__ == '__main__':
    m, tpl, ds, a, b, ms = sys.argv[1:7]
    ds = [int(x) for x in ds.split(',') if x != '']
    print(run(m, tpl, ds, int(a), int(b), int(ms), sys.argv[7:]))
