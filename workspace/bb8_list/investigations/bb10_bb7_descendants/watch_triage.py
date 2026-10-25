"""Triage the NOBOUNDARY / R4-SOME / HALT? rows of a watcher's watch_hits.tsv with follow2.py --blank.
  python watch_triage.py WATCH_HITS.tsv RESULTS.tsv [WORKERS=4] [STAGES=12] [BUDGET=150000000]
Re-runnable: machines already in RESULTS.tsv are skipped.  Prints a tally at the end; any 'HALT' line with level >= 2,
or with full_cycles >= 3 from a short start, is a record candidate (see bb10_bb7_descendants.md, section 9)."""
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
w = sys.argv[3] if len(sys.argv) > 3 else '4'
st = sys.argv[4] if len(sys.argv) > 4 else '12'
bud = sys.argv[5] if len(sys.argv) > 5 else '150000000'
rows = {}
for l in src.read_text().splitlines():
    f = l.split('\t')
    if len(f) > 1 and f[0] in ('NOBOUNDARY', 'R4-SOME', 'HALT?'):
        rows.setdefault(f[1], f[0])
setf = dst.with_suffix('.set.tsv')
setf.write_text(''.join(f'{m}\t{t}\t\t\t\tblank\n' for m, t in rows.items()))
subprocess.run([sys.executable, str(HERE / 'batch.py'), str(setf), str(dst), w, st, bud])
import tally
from collections import Counter
c = Counter()
for l in dst.read_text().splitlines():
    f = l.split('\t')
    c[tally.category(f[2])] += 1
    if 'RESULT HALT' in f[2] and ('level=2' in f[2] or 'level=3' in f[2] or 'level=4' in f[2]):
        print('!!! RECORD CANDIDATE:', l)
for k, v in c.most_common():
    print(f'{v:5d}  {k}')
