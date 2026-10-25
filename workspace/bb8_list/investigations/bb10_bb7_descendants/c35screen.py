"""Screen c35m14 holdouts for the 35-digit start: run 3e6 steps from blank (hyb10, no canonical states) and count
D-tokens in the final tape view (the BB(8) record has 35+ list tokens).  python c35screen.py OUT.tsv [WORKERS]"""
import re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
D = HERE.parent / 'bb10_from_bb7' / 'c35m14'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
out = Path(sys.argv[1]); W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
done = set(l.split('\t')[0] for l in out.read_text().splitlines()) if out.exists() else set()
ms = set()
for p in D.glob('part_*.txt'):
    ms |= set(x for x in p.read_text(errors='ignore').split() if '_' in x and len(x) == 69)
todo = sorted(ms - done)
def job(m):
    r = subprocess.run([str(HERE / 'hyb10.exe'), m, '-', '0', 'A', '3000000', '-q', 'P'], capture_output=True, text=True,
                       creationflags=LOW).stdout.strip().splitlines()
    last = r[-1] if r else ''
    body = last.partition(' | ')[2]
    ntok = 0; best = 0
    for t in body.split():
        if t.startswith('<') or t.startswith('['):
            best = max(best, ntok); ntok = 0; continue
        k = int(t.split('*')[1]) if '*' in t else 1
        ntok += k
    best = max(best, ntok)
    return m, last.split()[0] if last else '?', best, body[:150]
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for m, kind, best, body in ex.map(job, todo):
        f.write(f'{m}\t{kind}\t{best}\t{body}\n')
print(len(todo), 'screened')
