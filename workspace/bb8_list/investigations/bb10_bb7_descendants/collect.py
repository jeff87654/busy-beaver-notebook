"""Collect RESULT lines from logs/ for the machines of a set file into a results file (only HALT and full results
from follow2 logs; logs without RESULT are skipped).  python collect.py SET.tsv RESULTS.tsv"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = [l.split('\t') for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
dst = Path(sys.argv[2])
done = {l.split('\t')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
n = 0
with dst.open('a') as f:
    for r in rows:
        m = r[0]
        lg = HERE / 'logs' / f'{m}.log'
        if m in done or not lg.exists():
            continue
        res = [l for l in lg.read_text().splitlines() if l.startswith('RESULT')]
        if res and 'template' not in lg.read_text().splitlines()[0] or (res and len(r) > 2):
            f.write(f'{m}\t{r[1]}\t{res[-1]}\n'); n += 1
print(n, 'collected')
