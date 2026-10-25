"""Exhaustion screen: hyb10 from K(0^n;0;b) (champion template, canonical B), one run per machine.
  python screen2.py MACHINES.txt OUT.tsv N B BUDGET [WORKERS]"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent
LOW = subprocess.IDLE_PRIORITY_CLASS
src, dst, n, b, bud = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
W = int(sys.argv[6]) if len(sys.argv) > 6 else 4
def D(m): return '10' * m + '1'
w = '11' + D(1) * n + D(1) + '10' * (3 * b + 2) + '111001'
wf = H / 'tmpw' / f'k_{n}_{b}.txt'; wf.parent.mkdir(exist_ok=True); wf.write_text(w)
done = {l.split('\t')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
ms = [m for m in Path(src).read_text().split() if m not in done]
def job(m):
    r = subprocess.run([str(H.parent / 'hyb10r.exe'), m, str(wf), str(len(w)), 'B', bud, '-q', 'B'], capture_output=True,
                       text=True, creationflags=LOW).stdout.strip().splitlines()
    return m, (r[-1] if r else '?')[:220]
with ThreadPoolExecutor(W) as ex, dst.open('a') as out:
    for m, o in ex.map(job, ms):
        out.write(f'{m}\t{o}\n'); out.flush()
