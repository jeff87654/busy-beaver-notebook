"""Mini-follower screen (family C7) of a completion tree.
python mfc7_batch.py SET.txt OUT.tsv WORKERS [STAGES=12] [MAXS=3000000] [B0=6]
OUT: machine  kind  nstages  bigjumps  history"""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import c7fam, mf35, mf35g
src, out, W = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
ST = int(sys.argv[4]) if len(sys.argv) > 4 else 12
MS = int(sys.argv[5]) if len(sys.argv) > 5 else 3_000_000
B0 = int(sys.argv[6]) if len(sys.argv) > 6 else 6
done = set(l.split('\t')[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
ms = [l.split()[0] for l in open(src) if l.strip() and not l.startswith('#') and l.split()[0] not in done]
print(len(ms), 'machines', flush=True)
def job(m):
    m10 = m if m.count('_') == 9 else m + '_------' * (9 - m.count('_'))
    try:
        kind, hist = mf35g.follow('C7', m10, ST, MS, b0=B0)
    except Exception as ex:
        kind, hist = 'CRASH', [repr(ex)[:200]]
    return m, kind, len(hist), mf35.big_jumps(hist), ' ; '.join(hist)
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for i, r in enumerate(ex.map(job, ms)):
        f.write('\t'.join(str(x) for x in r) + '\n')
        if i % 20 == 0:
            f.flush()
print('done', flush=True)
