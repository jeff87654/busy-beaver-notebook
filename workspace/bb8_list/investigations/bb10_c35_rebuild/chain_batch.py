"""Run chain35.exe on a machine list in chunks with W Idle workers.  python chain_batch.py SET.txt OUT.txt W [MAXS] [MAXV]"""
import subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
src, out, W = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
MAXS = sys.argv[4] if len(sys.argv) > 4 else '300000'
MAXV = sys.argv[5] if len(sys.argv) > 5 else '300'
done = set(l.split()[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
ms = [l.split()[0] for l in open(src) if l.strip() and l.split()[0] not in done]
CH = 100
chunks = [ms[i:i + CH] for i in range(0, len(ms), CH)]
def job(ch):
    r = subprocess.run([str(HERE / 'chain35.exe'), MAXS, '200000', MAXV, '30'], input='\n'.join(ch) + '\n',
                       capture_output=True, text=True, creationflags=LOW)
    return r.stdout
print(len(ms), 'machines', flush=True)
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for i, s in enumerate(ex.map(job, chunks)):
        f.write(s); f.flush()
print('done', flush=True)
