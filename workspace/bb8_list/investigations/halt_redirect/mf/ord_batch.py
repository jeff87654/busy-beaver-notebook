"""Size-ordering check of candidate halters: each machine under policies std / big / shrink.
python ord_batch.py IN.tsv OUT.tsv WORKERS   (IN: family <TAB> machine)"""
import sys, io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ord_run
src, out, W = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
rows = [l.rstrip('\n').split('\t')[:2] for l in open(src) if l.strip()]
done = set(l.split('\t')[1] for l in out.read_text().splitlines()) if out.exists() else set()
rows = [r for r in rows if r[1] not in done]
def job(r):
    fam, m = r
    res = []
    for pol, bk in (('std', 1), ('big', 1), ('shrink', 1)):
        lines = []
        try:
            k = ord_run.follow(6, pol, 80, 1_000_000_000, bigk=bk, log=lines.append, FAM=fam, M=m)
        except Exception as ex:
            k = 'CRASH ' + repr(ex)[:80]
        nj = sum(1 for l in lines if ' J: ' in l)
        last = lines[-1][:90] if lines else ''
        res.append(f'{pol}:{k}:{nj}:{last}')
    return fam, m, res
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for fam, m, res in ex.map(job, rows):
        f.write('\t'.join([fam, m] + res) + '\n'); f.flush()
print('done', flush=True)
