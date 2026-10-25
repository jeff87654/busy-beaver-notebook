"""D2-stage probe over many machines: python d2probe.py MACHFILE OUT.tsv WORKERS
For X in XS, k in KS, r in RS: run d2map word (left 4,21,2) to the first champion phase / halt / 3e7 steps.
Output per run: machine X k r kind steps nleft leftitems  (nleft = token count of the list left of the 0*6 tail)."""
import subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import d2map
ZS, KS, RS = [2, 3, 0], list(range(0, 13)), [8, 14, 20]
def ntok(items):
    n = 0
    for t in items:
        g = re.fullmatch(r'(\d+)\*(\d+)', t)
        n += int(g.group(2)) if g else 1
    return n
def left_part(body):
    its = body.split()
    out = []
    for i, t in enumerate(its):
        if i > 0 and re.fullmatch(r'0\*([5-9]|\d\d+)', t): break
        if t.startswith('<'): break
        out.append(t)
    return out
def job(m, Z, k, r):
    line = d2map.run(m, d2map.word([4, 21, 2], 38, k, r, 7, Z), 30000000)
    head, _, body = line.partition(' | ')
    f = head.split()
    lp = left_part(body)
    return f'{m}\t{X}\t{k}\t{r}\t{f[0]}\t{f[1]}\t{ntok(lp)}\t{" ".join(lp)[:300]}'
ms = [l.split()[0] for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
out = Path(sys.argv[2]); W = int(sys.argv[3])
with ThreadPoolExecutor(W) as ex, out.open('w') as f:
    futs = [ex.submit(job, m, Z, k, r) for m in ms for Z in ZS for k in KS for r in RS]
    for fu in as_completed(futs):
        f.write(fu.result() + '\n'); f.flush()
print('done', len(futs))
