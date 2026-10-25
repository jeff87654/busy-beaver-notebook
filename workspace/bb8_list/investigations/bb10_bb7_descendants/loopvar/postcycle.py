"""c35-looper variants: run from the configuration right after the first full cycle, [D2, 0^Z, a=D1 | r=R | D4]
(canonical G), Z = 12b+46 (D5 family) or 12b+44 (D8 family), for b in {6, 11} and R in {201, 606} (= 0 mod 3).
H = halts right after one full cycle from the 35-digit start: a route-(b) RECORD CANDIDATE.
python postcycle.py SCREEN.tsv OUT.tsv"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent
LOW = subprocess.IDLE_PRIORITY_CLASS
def D(m): return '10' * m + '1'
import os
BS = [int(x) for x in os.environ.get('PC_B', '6,11').split(',')]
RS = [int(x) for x in os.environ.get('PC_R', '201,606').split(',')]
rows = []
for l in open(sys.argv[1]):
    m, k, d = l.rstrip('\n').split('\t')
    first = d.split(' || ')[0]
    body = first.split(' | ', 1)[1] if ' | ' in first else ''
    if body.startswith('5 4*'): rows.append((m, 46))
    elif body.startswith('8 4*'): rows.append((m, 44))
def job(mz):
    m, c = mz
    res = []
    for b in BS:
        for R in RS:
          for kind in ('E1', 'E2'):
            w = (D(2) if kind == 'E1' else '') + D(1) * (12 * b + c) + D(1) + D(R) + D(4)
            wf = H / 'tmpw' / f'pc_{abs(hash(m))}_{b}_{R}_{kind}.txt'
            wf.write_text(w)
            o = subprocess.run([str(H.parent / 'hyb10r.exe'), m, str(wf), str(len(w)), 'G', '300000000', '-q', 'G'],
                               capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()[-1]
            f = o.split()
            res.append(kind + ':' + f'{f[0]}@{f[1]}' + (f'/{f[2]}{f[3]}/ones{f[4]}' if f[0] == 'H' else ''))
    return m, ' '.join(res)
with ThreadPoolExecutor(3) as ex, open(sys.argv[2], 'w') as out:
    for m, r in ex.map(job, rows):
        out.write(f'{m}\t{r}\n'); out.flush()
