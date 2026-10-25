"""Screen machines with the mini-follower, run A only (b = 6 representatives).
python mf_batch.py SET.txt OUT.tsv WORKERS [STAGES=10] [MAXS=3000000]
OUT: machine  kind  nstages  bigjumps  history"""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mf35
src, out, W = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
ST = int(sys.argv[4]) if len(sys.argv) > 4 else 10
MS = int(sys.argv[5]) if len(sys.argv) > 5 else 3_000_000
done = set(l.split('\t')[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
ms = [l.split()[0] for l in open(src) if l.strip() and l.split()[0] not in done]
print(len(ms), 'machines', flush=True)
def job(m):
    try:
        kind, hist = mf35.follow(m, 'A', ST, MS)
    except Exception as ex:
        kind, hist = 'CRASH', [repr(ex)[:200]]
    return m, kind, len(hist), mf35.big_jumps(hist), ' ; '.join(hist)
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for i, r in enumerate(ex.map(job, ms)):
        f.write('\t'.join(str(x) for x in r) + '\n')
        if i % 50 == 0:
            f.flush()
print('done', flush=True)
