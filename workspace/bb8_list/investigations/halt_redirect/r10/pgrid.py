"""parallel grid.exe at Idle: python pgrid.py MACHINES STARTS BUDGET OUT W"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
LOW = subprocess.IDLE_PRIORITY_CLASS
src, st, bud, out, W = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]), int(sys.argv[5])
ms = [l.split('\t')[0] for l in Path(src).read_text().splitlines() if l.strip()]
tmp = out.parent / (out.stem + '_parts'); tmp.mkdir(exist_ok=True)
EXE = str(Path(__file__).resolve().parent.parent / 'grid.exe')
def job(i):
    f = tmp / f'm{i}.txt'; f.write_text('\n'.join(ms[i::W]) + '\n')
    r = subprocess.run([EXE, str(f), st, bud, '200000000'], capture_output=True, text=True, creationflags=LOW)
    if r.returncode: raise SystemExit(f'grid failed {r.returncode} {r.stderr[:300]}')
    return r.stdout
with ThreadPoolExecutor(W) as ex: res = list(ex.map(job, range(W)))
out.write_text(''.join(res)); print('rows', sum(len(x.splitlines()) for x in res))
