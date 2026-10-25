"""g-type conveyor machines: run from g's REAL end-of-list configuration (9-state study, endtoks_B6.txt: digit D(6139)
exhausted to D1, accumulator X) and report halt / no halt.  python endtest.py OUT.tsv"""
import re, subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent
G2 = HERE.parent / 'bb9_c7m12_1RB0RA_0RI0LC'
sys.path.insert(0, str(G2))
from tok2word import tok2word
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
s = (G2 / 'g2' / 'endtoks_B6.txt').read_text().strip()
ms = sorted({p.stem for p in (HERE / 'logs').glob('*.log') if '(D(4) D(2) D(7))' in p.read_text()})
ms.append('1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---')   # g itself (9 states)
def job(m):
    res = []
    for X in (2, 5, 8):
        t = re.sub(r' 4 2\*2 (\d+) 1 2 ', f' 4 2*2 1 1 {X} ', s, count=1)
        w = tok2word(t)
        Path(HERE / 'tmp_end').mkdir(exist_ok=True)
        wf = HERE / 'tmp_end' / f'{m[-20:]}_{X}.txt'
        wf.write_text(w)
        o = subprocess.run([str(HERE / 'hyb10r.exe'), m, str(wf), str(len(w)), 'B', '2000000000', '-q', 'Z'],
                           capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()[-1]
        f = o.split()
        res.append(f'X={X}:' + (f'H@{f[1]}/{f[2]}{f[3]}/ones{f[4]}' if f[0] == 'H' else f'{f[0]}@{f[1]}'))
    return m, ' '.join(res)
with ThreadPoolExecutor(3) as ex, open(sys.argv[1], 'w') as out:
    for m, r in ex.map(job, ms):
        out.write(f'{m}\t{r}\n'); out.flush()
