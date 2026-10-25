"""BB(8) list pipeline: enumerate each job in jobs_order.txt, then growth-rank its holdouts.

Restartable: completed jobs (job.json complete) and completed rankings (ranking.tsv)
are skipped. Stop at any time; rerun the same command to continue.

  python pipeline.py [--max-jobs N] [--workers 14]

Ranking: unmodified Ligocki Quick_Sim (third_party/ligocki @ 1b31c66) via ../ligocki_runner.py,
--recursive, 2 s in-process time budget (--sim-time 2), then sort by decimal digits of the ones count.
On BB(7) job 243308 this ranks the known champion #1 of 157 holdouts (655 digits; next 48).
The score measures growth within a fixed simulator budget. It is not a halting verdict.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
VENV_PY = PROJECT / 'third_party' / 'venv311' / 'Scripts' / 'python.exe'
sys.path.insert(0, str(ROOT))
import run_job  # noqa: E402

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)  # share spare CPU equally with other idle-priority jobs


def digits(r):
    o = r.get('ones') or {}
    k = o.get('kind')
    if k == 'integer':
        return len(o['decimal'])
    if k == 'large_integer':
        return round(o['bit_length'] * 0.30103)
    if k == 'symbolic_expression':
        return 10**9
    return -1


def rank(jobdir, workers):
    if (jobdir / 'ranking.tsv').exists():
        return
    holdouts = jobdir / 'holdouts.txt'
    if not holdouts.read_text().strip():
        (jobdir / 'ranking.tsv').write_text('digits\tstatus\treason\trules\tmachine\n')
        return
    out = jobdir / 'growth.json'
    subprocess.run([str(VENV_PY), str(PROJECT / 'ligocki_runner.py'), '--input', str(holdouts),
                    '--recursive', '--workers', str(workers), '--timeout', '60',
                    '--max-loops', '1000000', '--sim-time', '2', '--output', str(out)],
                   stdout=open(jobdir / 'rank.log', 'w'), stderr=subprocess.STDOUT,
                   creationflags=LOW, check=True)
    rows = json.loads(out.read_text())['results']
    rows.sort(key=lambda r: -digits(r))
    lines = ['digits\tstatus\treason\trules\tmachine']
    for r in rows:
        lines.append(f"{digits(r)}\t{r['status']}\t{r.get('reason')}\t{r.get('rules_proven')}\t{r['machine']}")
    (jobdir / 'ranking.tsv').write_text('\n'.join(lines) + '\n')
    top = rows[0] if rows else None
    run_job.log(jobdir, f'RANKED {len(rows)} holdouts; top {digits(top)} digits: {top["machine"]}' if top else 'RANKED 0')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--states', type=int, default=8, choices=(7, 8))
    ap.add_argument('--jobs-file', default=str(ROOT / 'jobs_order.txt'))
    ap.add_argument('--max-jobs', type=int, default=0)
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument('--slice', type=float, default=3600)
    ap.add_argument('--no-rank', action='store_true', help='leave ranking to rank_incremental.py')
    a = ap.parse_args()
    jobs = [int(x) for x in Path(a.jobs_file).read_text().split()]
    if a.max_jobs:
        jobs = jobs[:a.max_jobs]
    for job in jobs:
        run_job.run_job(job, a.states, a.workers, a.slice, seed_seconds=60, initial_chunks=256)
        if not a.no_rank:
            rank(ROOT / f'jobs{a.states}' / f'{job:06d}', a.workers)


if __name__ == '__main__':
    main()
