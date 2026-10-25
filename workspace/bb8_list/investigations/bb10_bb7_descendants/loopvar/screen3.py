"""Exhaustion-cell screen for looper variants (rec14 template, canonical B).
  python screen3.py MACHINES.txt OUT.tsv [WORKERS]
Cells K(0^n;0;b): E0 = (11,6) (the real first exhaustion: its accumulator 3b+2 has the universal residue rho,
and 20 = rho mod 120; an earlier version used b = 14, which is wrong), then (n,6) for n = 12..19 (3b+2 = 20 matches
the universal later-exhaustion residue rho mod 8,3,5,7,9,13; n covers all classes mod 8), then (14,46), (15,46) (rho mod 16).
Letters: J clean rebuild (0*2 4*L 1 37 20 ...), j other jump, H halt, T timeout.  A record needs E0 = J and an H later
in the real (n_k) sequence: n_1 = 6, n_2 = 1, n_3 = 4, n_4 = 7, ... mod 8."""
import re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent
LOW = subprocess.IDLE_PRIORITY_CLASS
CELLS = [(11, 6)] + [(n, 6) for n in range(12, 20)] + [(14, 46), (15, 46)]
def D(m): return '10' * m + '1'
words = {}
for n, b in CELLS:
    w = '11' + D(1) * n + D(1) + '10' * (3 * b + 2) + '111001'
    wf = H / 'tmpw' / f's3_{n}_{b}.txt'; wf.write_text(w); words[n, b] = (wf, len(w))
CLEAN = re.compile(r'\| 0\*2 4\*\d+ 1 37 20 ')
dst = Path(sys.argv[2])
done = {l.split('\t')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
ms = [m for m in Path(sys.argv[1]).read_text().split() if m not in done]
def job(m):
    let, odd = [], ''
    for c in CELLS:
        wf, L = words[c]
        o = subprocess.run([str(H.parent / 'hyb10r.exe'), m, str(wf), str(L), 'B', '30000000' if c[1] < 40 else '60000000',
                            '-q', 'B'], capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
        o = o[-1] if o else '?'
        k = o[0]
        if k == 'J' and not CLEAN.search(o): k = 'j'
        let.append(k)
        if k != 'J' and not odd: odd = f'{c}:{o[:160]}'
        if c == CELLS[0] and k not in 'Jj': break   # E0 must rebuild, else no record via this route
    return m, ''.join(let), odd
with ThreadPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 4) as ex, dst.open('a') as out:
    for m, g, odd in ex.map(job, ms):
        out.write(f'{m}\t{g}\t{odd}\n'); out.flush()
