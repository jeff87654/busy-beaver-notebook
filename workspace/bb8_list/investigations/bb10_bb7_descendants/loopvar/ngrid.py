"""n-grid for clean rebuilders: K(0^n;0;b) for n in NS (b = 6), hyb10 budget; prints H/J/T per n.
  python ngrid.py SCREEN.tsv OUT.tsv [WORKERS]   (SCREEN rows whose first rebuild is a clean list 0*2 4*L 1 ...)"""
import re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent
LOW = subprocess.IDLE_PRIORITY_CLASS
NS = [12, 13, 14, 15, 16, 17, 18, 19]
def D(m): return '10' * m + '1'
words = {}
for n in NS:
    w = '11' + D(1) * n + D(1) + '10' * 20 + '111001'
    wf = H / 'tmpw' / f'ng_{n}.txt'; wf.write_text(w); words[n] = (wf, len(w))
dst = Path(sys.argv[2])
done = {l.split('\t')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
ms = []
for l in open(sys.argv[1]):
    m, o = l.rstrip('\n').split('\t', 1)
    if m in done: continue
    if o.startswith('J') and re.search(r'\| 0\*2 4\*\d+ 1 37 20 ', o):
        ms.append(m)
def job(m):
    r = []
    for n in NS:
        wf, L = words[n]
        o = subprocess.run([str(H.parent / 'hyb10r.exe'), m, str(wf), str(L), 'B', '20000000', '-q', 'B'],
                           capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
        r.append((o[-1] if o else '?')[0])
    return m, ''.join(r)
with ThreadPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 3) as ex, dst.open('a') as out:
    for m, g in ex.map(job, ms):
        out.write(f'{m}\t{g}\n'); out.flush()
