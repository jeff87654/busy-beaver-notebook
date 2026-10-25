"""Enumerate whole mxdys subtasks (job ids 0..999999) across many cores, restartably.

Stage 1 (seed): run the unmodified enumerator (`mxdys_pilot{7,8}.exe enum ID`) with a
short deadline. It completes the 10 BFS rounds of the job partition, starts the final
DFS and checkpoints every unvisited final-DFS node to a frontier file.
Stage 2 (chunks): the frontier is split into chunk files. A pool of workers resumes
chunks (`mxdys_resume{7,8}.exe resume CHUNK`) with a per-run time slice. When a slice
expires, the unvisited remainder is re-split into new chunks. The job is complete when
no chunk is pending. Its holdouts are then the seed holdouts plus every chunk's holdouts.

Crash safety: a chunk's outputs are accepted only after a clean exit that wrote a
stats file. A chunk left in pending/ after an interruption is re-run from scratch.
Accepting a chunk is idempotent (fixed output names), so a restart never loses or
duplicates holdouts.

Usage:
  python run_job.py --states 8 --job 76450 [--workers 14] [--slice 1800]
  python run_job.py --states 8 --jobs-file jobs_order.txt --max-jobs 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
COMPILER_BIN = r'C:\msys64\ucrt64\bin'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)  # share spare CPU equally with other idle-priority jobs


MAX_POOL = 16


def worker_cap(default):
    """Concurrent chunk runs: the integer in workers.txt if present (0 pauses), else the default."""
    try:
        return max(0, min(MAX_POOL, int((ROOT / 'workers.txt').read_text().split()[0])))
    except (OSError, ValueError, IndexError):
        return min(MAX_POOL, default)


def binaries(states):
    return (PROJECT / f'mxdys_pilot{states}.exe', PROJECT / f'mxdys_resume{states}.exe')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def env_with(seconds, prefix):
    env = dict(os.environ)
    env['PATH'] = COMPILER_BIN + os.pathsep + env.get('PATH', '')
    env['BB_PILOT_SECONDS'] = str(seconds)
    env['BB_PILOT_PREFIX'] = prefix
    env.pop('BB_PILOT_HALTERS', None)
    return env


def machine_lines(path):
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text().splitlines() if '_' in l]


def split_lines(lines, parts):
    parts = max(1, min(parts, len(lines)))
    return [lines[i::parts] for i in range(parts)]


def log(jobdir, msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    print(line, flush=True)
    with open(jobdir / 'progress.log', 'a') as f:
        f.write(line + '\n')


def seed(job, jobdir, states, seed_seconds):
    sdir = jobdir / 'seed'
    if (sdir / 'accepted').exists():
        return
    shutil.rmtree(sdir, ignore_errors=True)
    sdir.mkdir(parents=True)
    pilot, _ = binaries(states)
    while True:
        t0 = time.time()
        rc = subprocess.run([str(pilot), 'enum', str(job)], cwd=sdir, env=env_with(seed_seconds, 'seed'),
                            stdout=open(sdir / 'out.log', 'w'), stderr=subprocess.STDOUT,
                            creationflags=LOW).returncode
        stats = sdir / 'seed_stats.json'
        frontier = sdir / 'seed_frontier.txt'
        assert rc == 0 and stats.exists(), f'seed run failed rc={rc}'
        rounds = {l.split()[1] for l in frontier.read_text().splitlines() if l.strip()}
        if rounds <= {'10'}:
            break
        # The deadline hit before the BFS partition finished; retry with more time.
        log(jobdir, f'seed deadline {seed_seconds}s hit during BFS (rounds {sorted(rounds)}); retrying')
        seed_seconds *= 2
    log(jobdir, f'seed done in {time.time()-t0:.0f}s: {json.loads(stats.read_text())}')
    (sdir / 'accepted').write_text('ok\n')


def run_chunk(chunk, jobdir, states, slice_seconds):
    """Resume one chunk in a scratch dir. Return (chunk, ok, info)."""
    _, resume = binaries(states)
    work = jobdir / 'work' / chunk.stem
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    rc = subprocess.run([str(resume), 'resume', str(chunk)], cwd=work, env=env_with(slice_seconds, 'out'),
                        stdout=open(work / 'out.log', 'w'), stderr=subprocess.STDOUT,
                        creationflags=LOW).returncode
    ok = rc == 0 and (work / 'out_stats.json').exists()
    return chunk, ok, rc


def accept(chunk, jobdir, fanout):
    work = jobdir / 'work' / chunk.stem
    res = jobdir / 'results'
    res.mkdir(exist_ok=True)
    stats = json.loads((work / 'out_stats.json').read_text())
    shutil.copyfile(work / 'out_holdouts.txt', res / f'{chunk.stem}_holdouts.txt')
    (res / f'{chunk.stem}_stats.json').write_text(json.dumps(stats))
    rest = [l for l in (work / 'out_frontier.txt').read_text().splitlines() if l.strip()]
    pending = jobdir / 'chunks' / 'pending'
    if rest:
        # Child names are a deterministic function of the parent, so re-accepting a chunk
        # after an interruption overwrites rather than duplicates its children.
        for i, part in enumerate(split_lines(rest, fanout)):
            child = 'r' + hashlib.sha1(f'{chunk.stem}/{i}'.encode()).hexdigest()[:12]
            (pending / f'{child}.txt').write_text('\n'.join(part) + '\n')
    done = jobdir / 'chunks' / 'done'
    done.mkdir(exist_ok=True)
    os.replace(chunk, done / chunk.name)
    shutil.rmtree(work, ignore_errors=True)
    return stats, len(rest)


def run_job(job, states, workers, slice_seconds, seed_seconds, initial_chunks):
    jobdir = ROOT / f'jobs{states}' / f'{job:06d}'
    jobdir.mkdir(parents=True, exist_ok=True)
    if (jobdir / 'job.json').exists() and json.loads((jobdir / 'job.json').read_text()).get('complete'):
        log(jobdir, 'already complete')
        return
    seed(job, jobdir, states, seed_seconds)
    pending = jobdir / 'chunks' / 'pending'
    if not (jobdir / 'chunks').exists():
        pending.mkdir(parents=True)
        lines = [l for l in (jobdir / 'seed' / 'seed_frontier.txt').read_text().splitlines() if l.strip()]
        for i, part in enumerate(split_lines(lines, initial_chunks)):
            (pending / f'c{i:04d}.txt').write_text('\n'.join(part) + '\n')
        log(jobdir, f'{len(lines)} frontier roots split into {min(initial_chunks, len(lines))} chunks')
    t_start = time.time()
    failures = {}
    running = {}
    with ThreadPoolExecutor(max_workers=MAX_POOL) as pool:
        while True:
            cap = worker_cap(workers)
            for chunk in sorted(pending.glob('*.txt')):
                if len(running) >= cap:
                    break
                if chunk.name not in running:
                    running[chunk.name] = pool.submit(run_chunk, chunk, jobdir, states, slice_seconds)
            if not running:
                if any(pending.glob('*.txt')):  # paused via workers.txt = 0
                    time.sleep(60)
                    continue
                break
            # The timeout re-reads workers.txt every minute; lowering it takes effect as chunks finish.
            finished, _ = wait(list(running.values()), timeout=60, return_when=FIRST_COMPLETED)
            for fut in finished:
                chunk, ok, rc = fut.result()
                del running[chunk.name]
                if ok:
                    # Re-split the unvisited remainder only when the queue is running low;
                    # otherwise keep it as one chunk (fewer process launches and file writes).
                    queued = sum(1 for _ in pending.glob('*.txt')) - len(running)
                    stats, rest = accept(chunk, jobdir, fanout=cap if queued < 2 * cap else 1)
                    log(jobdir, f'{chunk.stem}: {stats["nodes_started"]} nodes, '
                                f'{stats["elapsed_seconds"]:.0f}s, {rest} roots re-queued; '
                                f'{len(list(pending.glob("*.txt")))} chunks pending')
                else:
                    failures[chunk.name] = failures.get(chunk.name, 0) + 1
                    log(jobdir, f'{chunk.stem}: FAILED rc={rc} (attempt {failures[chunk.name]})')
                    if failures[chunk.name] >= 3:
                        raise SystemExit(f'chunk {chunk} failed 3 times; see work dir')
    # Complete: merge.
    seed_hold = machine_lines(next((jobdir / 'seed').glob('holdouts_*.txt')))
    holdouts = list(seed_hold)
    nodes = json.loads((jobdir / 'seed' / 'seed_stats.json').read_text())['nodes_started']
    cpu = json.loads((jobdir / 'seed' / 'seed_stats.json').read_text())['elapsed_seconds']
    for st in sorted((jobdir / 'results').glob('*_stats.json')):
        s = json.loads(st.read_text())
        nodes += s['nodes_started']
        cpu += s['elapsed_seconds']
        holdouts += machine_lines(st.with_name(st.name.replace('_stats.json', '_holdouts.txt')))
    assert not list(pending.glob('*.txt'))
    (jobdir / 'holdouts.txt').write_text('\n'.join(holdouts) + ('\n' if holdouts else ''))
    pilot, resume = binaries(states)
    info = {'job': job, 'states': states, 'complete': True, 'nodes': nodes, 'holdouts': len(holdouts),
            'distinct_holdouts': len(set(holdouts)), 'cpu_seconds': round(cpu, 1),
            'wall_seconds_this_run': round(time.time() - t_start, 1),
            'finished': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'enumerator': 'github.com/ccz181078/TM @ a41db6c (main.cpp sha256 22294ab2...) + deadline/checkpoint hooks',
            'binaries': {pilot.name: sha256(pilot), resume.name: sha256(resume)}}
    (jobdir / 'job.json').write_text(json.dumps(info, indent=1))
    log(jobdir, f'COMPLETE: {info}')
    shutil.rmtree(jobdir / 'work', ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--states', type=int, choices=(7, 8), default=8)
    ap.add_argument('--job', type=int, action='append', default=[])
    ap.add_argument('--jobs-file')
    ap.add_argument('--max-jobs', type=int, default=0)
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument('--slice', type=float, default=1800, help='seconds per chunk run before re-splitting')
    ap.add_argument('--seed-seconds', type=float, default=60)
    ap.add_argument('--initial-chunks', type=int, default=256)
    a = ap.parse_args()
    jobs = list(a.job)
    if a.jobs_file:
        jobs += [int(x) for x in Path(a.jobs_file).read_text().split()]
    if a.max_jobs:
        jobs = jobs[:a.max_jobs]
    for job in jobs:
        assert 0 <= job < 10**6
        run_job(job, a.states, a.workers, a.slice, a.seed_seconds, a.initial_chunks)


if __name__ == '__main__':
    main()
