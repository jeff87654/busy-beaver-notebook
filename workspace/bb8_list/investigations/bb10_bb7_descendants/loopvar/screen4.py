"""Event-cell screen for variants of the C29/C32 loopers, whose cycle has three event types (rec14 canonical B):
  X0 = [11 0^n | R]  (store R as a left digit D(2R-1)),  X1 = [D3 0^n | R]  (store again),  X2 = [D0 0^n | R]  (expand
  the list by 4R-5).  Cells: E0 = X0(11, R = 20) (the real first exhaustion; its accumulator has the universal residue rho = 20 mod 120), then X0, X1, X2 for n = 12..19 at
  R = 20 (the later-event residue rho mod 8,3,5,7,9,13).  In the real run n is 3 or 7 mod 8, alternating per cycle.
  python screen4.py MACHINES.txt OUT.tsv [WORKERS]
Letters per cell: J = parent-like jump, j = other jump, H = halt, T = timeout.  Any H after an E0 jump is a lead."""
import re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent
LOW = subprocess.IDLE_PRIORITY_CLASS
def D(m): return '10' * m + '1'
LEFT = {'X0': '11', 'X1': D(3), 'X2': '1'}
PAT = {'X0': re.compile(r'\| \d+ 4\*\d+ 1 37 20 '), 'X1': re.compile(r'\| 0 \d+ 4\*\d+ 1 37 20 '),
       'X2': re.compile(r'\| 0\*2 4\*\d+ 1 37 20 ')}
CELLS = [('X0', 11, 20)] + [(t, n, 20) for n in range(12, 20) for t in ('X0', 'X1', 'X2')]
words = {}
for t, n, R in CELLS:
    w = LEFT[t] + D(1) * n + D(1) + D(R) + '11001'
    wf = H / 'tmpw' / f's4_{t}_{n}_{R}.txt'; wf.write_text(w); words[t, n, R] = (wf, len(w))
dst = Path(sys.argv[2])
done = {l.split('\t')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
ms = [m for m in Path(sys.argv[1]).read_text().split() if m not in done]
def job(m):
    let, odd = [], ''
    for c in CELLS:
        wf, L = words[c]
        o = subprocess.run([str(H.parent / 'hyb10r.exe'), m, str(wf), str(L), 'B', '30000000', '-q', 'B'],
                           capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
        o = o[-1] if o else '?'
        k = o[0]
        if k == 'J' and not PAT[c[0]].search(o): k = 'j'
        let.append(k)
        if k != 'J' and not odd: odd = f'{c}:{o[:160]}'
        if c == CELLS[0] and k not in 'Jj': break
    return m, ''.join(let), odd
with ThreadPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 4) as ex, dst.open('a') as out:
    for m, g, odd in ex.map(job, ms):
        out.write(f'{m}\t{g}\t{odd}\n'); out.flush()
