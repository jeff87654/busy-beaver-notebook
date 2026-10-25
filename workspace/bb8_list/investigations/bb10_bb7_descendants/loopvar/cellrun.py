"""Run cellscan.exe over a machine list in N chunks (Idle).  python cellrun.py MACHINES OUT FAMILY [CHUNKS]
FAMILY C28: cells cs_e0r (E0 real: n=11, R=20 = rho mod 120), cs_c12..19.  FAMILY C2932: cells from tmpw/cs4_list.txt."""
import subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
ms = Path(sys.argv[1]).read_text().split(); out = Path(sys.argv[2]); fam = sys.argv[3]
k = int(sys.argv[4]) if len(sys.argv) > 4 else 4
cells = (['tmpw/cs_e0r.txt'] + [f'tmpw/cs_c{n}.txt' for n in range(12, 20)]) if fam == 'C28' else \
        (H / 'tmpw' / 'cs4r_list.txt').read_text().split()
ps = []
for i in range(k):
    part = H / 'tmpw' / f'{out.stem}_in{i}.txt'; part.write_text('\n'.join(ms[i::k]) + '\n')
    ps.append(subprocess.Popen([str(H / 'cellscan.exe'), str(part), 'B', *cells], cwd=H,
                               stdout=open(H / 'tmpw' / f'{out.stem}_out{i}.txt', 'w'), creationflags=subprocess.IDLE_PRIORITY_CLASS))
for p in ps: p.wait()
with out.open('w') as f:
    for i in range(k): f.write((H / 'tmpw' / f'{out.stem}_out{i}.txt').read_text())
