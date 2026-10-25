"""Grade enumeration leaves (non-HALT, non-WIDE) with grade35.exe at b = 3,4,5 (n = 35), in parallel Idle workers.
python grade_batch.py OUT.tsv WORKERS e_*.txt   (machines already in OUT.tsv are skipped)"""
import subprocess, sys, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
out = Path(sys.argv[1]); W = int(sys.argv[2]); files = sys.argv[3:]
done = set()
if out.exists():
    done = set(l.split()[0] for l in out.read_text().splitlines() if l.strip())
ms = []
seen = set()
for fn in files:
    for l in open(fn):
        f = l.split()
        if len(f) < 2 or f[0] in ('HALT', 'WIDE'):
            continue
        m = f[1]
        if m in seen or m in done:
            continue
        seen.add(m); ms.append(m)
print(len(ms), 'machines to grade', flush=True)
CH = 200
chunks = [ms[i:i + CH] for i in range(0, len(ms), CH)]
def job(ch):
    r = subprocess.run([str(HERE / 'grade35.exe'), '35', '1000000', '30000', '3,4,5'], input='\n'.join(ch) + '\n',
                       capture_output=True, text=True, creationflags=LOW)
    return r.stdout
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for i, s in enumerate(ex.map(job, chunks)):
        f.write(s); f.flush()
        if i % 20 == 0:
            print(i * CH, 'graded', flush=True)
print('done', flush=True)
