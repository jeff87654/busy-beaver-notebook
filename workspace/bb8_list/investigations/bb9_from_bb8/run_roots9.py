"""Enumerate every root of roots9.tsv with knuth9.exe exactfrom, in parallel at Idle priority, with a time limit.

  python run_roots9.py roots9.tsv OUTDIR [WORKERS=4] [LIMIT_SECONDS=7200]

Each root writes OUTDIR/rNNNN.txt (holdouts) and OUTDIR/rNNNN.json (node counts); a root whose .json exists is
skipped, so the run can be restarted.  A root that hits the time limit is recorded as {"timeout": true} and keeps
the holdouts found so far.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = HERE / 'knuth9.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


def main():
    roots, out = Path(sys.argv[1]), Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    limit = float(sys.argv[4]) if len(sys.argv) > 4 else 7200
    out.mkdir(exist_ok=True)
    rows = [l.split('\t') for l in roots.read_text().splitlines() if l.strip()]
    lock = threading.Lock()

    def job(i_row):
        i, (root, free, lab, tr) = i_row
        stem = out / f'r{i:04d}'
        js = stem.with_suffix('.json')
        if js.exists():
            return
        t0 = time.time()
        try:
            r = subprocess.run([str(EXE), 'exactfrom', root, '8', '2', free, str(stem.with_suffix('.txt'))],
                               creationflags=LOW, timeout=limit, capture_output=True, text=True)
            line = [l for l in r.stdout.splitlines() if l.startswith('{')]
            res = json.loads(line[-1]) if line else {'error': r.stderr[-300:]}
        except subprocess.TimeoutExpired:
            res = {'root': root, 'timeout': True}
        res.update({'parent': lab, 'freed': tr, 'wall': round(time.time() - t0, 1)})
        js.write_text(json.dumps(res))
        with lock:
            print(f"r{i:04d} {lab} {tr}: {res.get('nodes', '?')} nodes, {res.get('holdouts', '?')} holdouts, "
                  f"{res['wall']} s{' TIMEOUT' if res.get('timeout') else ''}", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, enumerate(rows, 1)))
    print('done')


if __name__ == '__main__':
    main()
