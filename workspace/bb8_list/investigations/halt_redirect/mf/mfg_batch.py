"""Mini-follower screen of a sibling family's completion tree (mf35g, run A only).
python mfg_batch.py FAMILY SET.txt OUT.tsv WORKERS [STAGES=12] [MAXS=3000000]
OUT: machine  kind  nstages  bigjumps  history"""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mf35, mf35g
fam, src, out, W = sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4])
ST = int(sys.argv[5]) if len(sys.argv) > 5 else 12
MS = int(sys.argv[6]) if len(sys.argv) > 6 else 3_000_000
done = set(l.split('\t')[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
ms = [l.split()[0] for l in open(src) if l.strip() and l.split()[0] not in done]
print(len(ms), 'machines', flush=True)
def job(m):
    try:
        kind, hist = mf35g.follow(fam, m, ST, MS)
    except Exception as ex:
        kind, hist = 'CRASH', [repr(ex)[:200]]
    return m, kind, len(hist), mf35.big_jumps(hist), ' ; '.join(hist)
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for i, r in enumerate(ex.map(job, ms)):
        f.write('\t'.join(str(x) for x in r) + '\n')
        if i % 20 == 0:
            f.flush()
print('done', flush=True)
