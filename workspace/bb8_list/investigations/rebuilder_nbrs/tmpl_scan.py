"""Fit machines against a FIXED template with `dlscan2 --tmpl` (no template inference, so no slow cases).

  python tmpl_scan.py singles OUT.tsv [WORKERS=2]      # all radius-1 changes of the four parents
  python tmpl_scan.py pairs SINGLES.tsv OUT.tsv [WORKERS=2]
                                                        # pairs of rule-preserving singles of the same parent

A change is rule-preserving if the fit is ok and R1-R3 have exactly the parent's parameters
(R1 2b+2 | R2 a=2b+2 b=0 | R3 2b+2+0k tail=0 a=0 b=0); only R4 may differ.  Output columns:
machine, parent, changed, grade, params, rules_same (1/0), r4 (the R4 letters for b = 1..5).
"""
from __future__ import annotations

import itertools
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gen_nbrs import PARENTS, VALUES, cells, join, name

HERE = Path(__file__).resolve().parent
EXE = (HERE / '..' / '..' / 'neighbors' / 'dlscan2.exe').resolve()
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
TEMPLATES = [
    ['R', 'G', '11', '01', '1', '3', '1', '3', '1', '101'],
    ['R', 'G', '11', '01', '1', '3', '1', '3', '1', '101'],
    ['R', 'B', '11', '10', '1', '3', '1', '3', '2', '111001'],
    ['R', 'B', '11', '10', '1', '3', '1', '3', '2', '111001'],
]
RULES = 'R1 2b+2 | R2 a=2b+2 b=0 | R3 2b+2+0k tail=0 a=0 b=0'


def fit(m, pi):
    try:
        r = subprocess.run([str(EXE), '--tmpl', m, *TEMPLATES[pi], '100000'], creationflags=LOW, timeout=60,
                           capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', '-'
    last = [l for l in r.stdout.splitlines() if l.startswith('fit ')]
    mm = re.match(r'fit ok=(\d) grade=(\S+) ?(.*)', last[0]) if last else None
    if not mm or mm.group(1) != '1':
        return '-', '-'
    return mm.group(2), mm.group(3)


def run(jobs, out, workers):
    lock = threading.Lock()
    with open(out, 'w') as f, ThreadPoolExecutor(workers) as ex:
        f.write('machine\tparent\tchanged\tgrade\tparams\trules_same\tr4\n')

        def job(j):
            m, pi, changed = j
            g, p = fit(m, pi)
            same = int(p.startswith(RULES))
            r4 = re.search(r'R4 (\w+)', p).group(1) if 'R4 ' in p else '-'
            with lock:
                f.write(f'{m}\t{pi}\t{changed}\t{g}\t{p}\t{same}\t{r4}\n')
                f.flush()
        list(ex.map(job, jobs))


def main():
    mode = sys.argv[1]
    if mode == 'singles':
        out, workers = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2
        jobs = []
        for pi, p in enumerate(PARENTS):
            base = cells(p)
            for k in range(16):
                for v in VALUES:
                    if v != base[k]:
                        c = list(base)
                        c[k] = v
                        jobs.append((join(c), pi, f'{name(k)}={v}'))
        run(jobs, out, workers)
    else:
        singles, out = sys.argv[2], sys.argv[3]
        workers = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        keep = {}
        for line in open(singles).read().splitlines()[1:]:
            m, pi, changed, g, p, same, r4 = line.split('\t')
            if same == '1':
                keep.setdefault(int(pi), []).append(changed)
        jobs = []
        for pi, chs in keep.items():
            base = cells(PARENTS[pi])
            for a, b in itertools.combinations(chs, 2):
                ka, va = a.split('=')
                kb, vb = b.split('=')
                if ka == kb:
                    continue
                c = list(base)
                for kk, vv in ((ka, va), (kb, vb)):
                    c[2 * 'ABCDEFGH'.index(kk[0]) + int(kk[1])] = vv
                jobs.append((join(c), pi, f'{a},{b}'))
        print(f'{len(jobs)} pairs')
        run(jobs, out, workers)


if __name__ == '__main__':
    main()
