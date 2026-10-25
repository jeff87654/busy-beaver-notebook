"""Grade neighbours with dlscan2 one machine at a time, with a per-machine timeout, at Idle priority.

  python grade_timeout.py NBRS.tsv OUT.tsv [WORKERS=4] [TIMEOUT=30] [STEPS=5000000] [N=100000]

Genuine champion-structure machines grade in under 1 s (the BB(7) champion, the 35-digit machine and
the four rebuilders: 0.5-0.9 s).  Machines for which dlscan2 infers hundreds of non-champion templates
(u = 1, s = 0 binary-counter shapes) can take minutes; they are recorded as TIMEOUT for a second pass.
Resumable: machines already in OUT.tsv are skipped.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = (HERE / '..' / '..' / 'neighbors' / 'dlscan2.exe').resolve()
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
HEAD = 'machine\tparents\tchanged\tin_m8\tseconds\thalted_step\tgrade\ttemplate\tparams\n'


def grade(m, td, timeout, steps, n):
    i, o = Path(td) / f'{threading.get_ident()}.txt', Path(td) / f'{threading.get_ident()}.tsv'
    i.write_text(m + '\n')
    t = time.time()
    try:
        subprocess.run([str(EXE), str(i), str(o), steps, n], creationflags=LOW, timeout=timeout,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return f'{time.time() - t:.2f}', '-', 'TIMEOUT', '-', '-'
    rows = [l.split('\t') for l in o.read_text().splitlines()[1:] if not l.startswith('#')]
    if not rows:
        return f'{time.time() - t:.2f}', '-', '-', '-', '-'
    r = rows[0]
    return f'{time.time() - t:.2f}', r[1], r[3], r[4], r[5]


def main():
    nbrs, out = Path(sys.argv[1]), Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 30
    steps = sys.argv[5] if len(sys.argv) > 5 else '5000000'
    n = sys.argv[6] if len(sys.argv) > 6 else '100000'
    meta = [l.split('\t') for l in nbrs.read_text().splitlines()]
    seen = set()
    if out.exists():
        seen = {l.split('\t')[0] for l in out.read_text().splitlines()[1:]}
    else:
        out.write_text(HEAD)
    todo = [r for r in meta if r[0] not in seen]
    lock = threading.Lock()
    count = [0]
    with tempfile.TemporaryDirectory() as td, out.open('a') as f, ThreadPoolExecutor(workers) as ex:
        def job(r):
            res = grade(r[0], td, timeout, steps, n)
            with lock:
                f.write('\t'.join(r + list(res)) + '\n')
                f.flush()
                count[0] += 1
                if count[0] % 100 == 0:
                    print(f'{count[0]}/{len(todo)}', flush=True)
        list(ex.map(job, todo))
    print(f'done: {len(todo)} graded -> {out}')


if __name__ == '__main__':
    main()
