"""Growth-rank holdouts as soon as each chunk is accepted, instead of after a whole job.

For every jobs8/<id>/ it ranks the seed holdouts and each results/<chunk>_holdouts.txt
exactly once, using persistent Quick_Sim workers (fast_rank.py): --recursive and a budget of
2 CPU-seconds of simulation per machine. The output is growth/<name>.json.
It maintains:
  top_candidates_bb8.tsv        best 300 machines across all jobs (by digits of sigma reached)
  jobs8/<id>/ranking.tsv        full ranking, written once the job is complete and fully ranked
Restartable; run alongside pipeline.py --no-rank, under the venv interpreter:
  ../third_party/venv311/Scripts/python.exe rank_incremental.py --workers 2
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import fast_rank

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
VENV_PY = PROJECT / 'third_party' / 'venv311' / 'Scripts' / 'python.exe'
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


def sources(jobdir):
    """(name, holdout file) pairs that are final (their chunk was accepted)."""
    out = []
    if (jobdir / 'seed' / 'accepted').exists():
        out += [('seed', f) for f in (jobdir / 'seed').glob('holdouts_*.txt')]
    if (jobdir / 'results').exists():
        for f in sorted((jobdir / 'results').glob('*_holdouts.txt')):
            out.append((f.name[:-len('_holdouts.txt')], f))
    return out


def rank_file(name, path, jobdir, pool):
    gdir = jobdir / 'growth'
    gdir.mkdir(exist_ok=True)
    machines = [l.strip() for l in path.read_text().splitlines() if '_' in l]
    results = pool.rank(machines) if machines else []
    tmp = gdir / f'{name}.partial.json'
    tmp.write_text(json.dumps({'results': results}))
    tmp.replace(gdir / f'{name}.json')
    return len(machines)


def all_rows(jobdir):
    rows = []
    for g in (jobdir / 'growth').glob('*.json') if (jobdir / 'growth').exists() else []:
        if g.name.endswith('.partial.json'):
            continue
        for r in json.loads(g.read_text())['results']:
            r['_job'] = jobdir.name
            rows.append(r)
    return rows


def fmt(r):
    return f"{digits(r)}\t{r['status']}\t{r.get('reason')}\t{r.get('rules_proven')}\t{r['_job']}\t{r['machine']}"


def refresh(jobs_root, states):
    everything = []
    for jobdir in sorted(jobs_root.glob('*')):
        rows = all_rows(jobdir)
        everything += rows
        complete = (jobdir / 'job.json').exists()
        if complete and not (jobdir / 'ranking.tsv').exists():
            srcs = sources(jobdir)
            if all((jobdir / 'growth' / f'{n}.json').exists() for n, _ in srcs):
                rows.sort(key=lambda r: -digits(r))
                (jobdir / 'ranking.tsv').write_text(
                    'digits\tstatus\treason\trules\tjob\tmachine\n' + '\n'.join(map(fmt, rows)) + '\n')
    everything.sort(key=lambda r: -digits(r))
    (ROOT / f'top_candidates_bb{states}.tsv').write_text(
        'digits\tstatus\treason\trules\tjob\tmachine\n' + '\n'.join(map(fmt, everything[:300])) + '\n')
    return len(everything)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--states', type=int, default=8)
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--once', action='store_true')
    a = ap.parse_args()
    jobs_root = ROOT / f'jobs{a.states}'
    pool = fast_rank.Pool(workers=a.workers, sim_time=2.0)
    try:
        loop(a, jobs_root, pool)
    finally:
        pool.close()


def loop(a, jobs_root, pool):
    while True:
        did = 0
        for jobdir in sorted(jobs_root.glob('*')):
            for name, path in sources(jobdir):
                if not (jobdir / 'growth' / f'{name}.json').exists():
                    did += 1 + rank_file(name, path, jobdir, pool)
        total = refresh(jobs_root, a.states)
        if did:
            print(time.strftime('%H:%M:%S'), f'ranked through {total} holdouts', flush=True)
        if a.once:
            break
        if not did:
            time.sleep(60)


if __name__ == '__main__':
    main()
