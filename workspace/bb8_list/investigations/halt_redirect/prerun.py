"""Run grid.exe over a machine list in parallel chunks at Idle priority.
  python prerun.py MACHINES.tsv STARTS.txt BUDGET OUT.tsv [WORKERS=6]"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
src, starts, budget, out = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
W = int(sys.argv[5]) if len(sys.argv) > 5 else 6
ms = [l.split('\t')[0] for l in Path(src).read_text().splitlines() if l.strip()]
tmp = out.parent / (out.stem + '_parts'); tmp.mkdir(exist_ok=True)
def job(i):
    f = tmp / f'm{i}.txt'; f.write_text('\n'.join(ms[i::W]) + '\n')
    r = subprocess.run(['./grid.exe', str(f), starts, budget], capture_output=True, text=True, creationflags=LOW)
    return r.stdout
with ThreadPoolExecutor(W) as ex:
    res = list(ex.map(job, range(W)))
out.write_text(''.join(res))
print('done', sum(len(r.splitlines()) for r in res), 'rows')
