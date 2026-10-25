"""Incremental digit-list scan of every enumerated holdout, straight from the enumerator's chunk files.

  python dlscan_all.py [--workers 2] [--max-files N]     scan the holdout files not scanned yet, then exit
  python dlscan_all.py --status                          print the totals only

Unlike the old scan (doubling rows of followup/promising.tsv), this does not wait for the ranker or the
follow-up: each accepted chunk `jobs8/<job>/results/<chunk>_holdouts.txt` (and the seed holdouts) is screened by
dlscan.exe as soon as it exists, and the screen output is kept in `jobs8/<job>/dlscan/<chunk>.tsv`. A chunk is
never scanned twice. Jobs the ranker has not finished are scanned first.

Screen hits are confirmed and graded by dlscan.judge (kfit.py) and appended to `neighbors/dl_hits.tsv`:
  time, job, chunk, machine, verdict (DIGIT-LIST / unconfirmed / partial), grade (SAFE / NOBOUNDARY / CHECK /
  HALT?), known (the machine is already in investigations/dispatched.txt), details.
Runs at Idle priority. Only one instance runs at a time (dlscan_all.lock).
"""
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import dlscan  # noqa: E402

HITS = HERE / 'dl_hits.tsv'
LOCK = HERE / 'dlscan_all.lock'
HEADER = 'time\tjob\tchunk\tmachine\tverdict\tgrade\tknown\tdetails\n'


def sources(jobdir):
    """(name, holdout file) pairs that are final: the seed holdouts and every accepted chunk."""
    out = []
    if (jobdir / 'seed' / 'accepted').exists():
        out += [('seed', f) for f in (jobdir / 'seed').glob('holdouts_*.txt')]
    res = jobdir / 'results'
    if res.exists():
        for f in sorted(res.glob('*_holdouts.txt')):
            name = f.name[:-len('_holdouts.txt')]
            if (res / f'{name}_stats.json').exists():     # written after the holdout file is complete
                out.append((name, f))
    return out


def jobs():
    js = [j for j in sorted((ROOT / 'jobs8').glob('*')) if j.is_dir()]
    return sorted(js, key=lambda j: ((j / 'ranking.tsv').exists(), j.name))   # unranked jobs first


def known_machines():
    disp = ROOT / 'investigations' / 'dispatched.txt'
    return {l.split('\t')[0] for l in disp.read_text().splitlines() if l.strip()} if disp.exists() else set()


def pid_alive(pid):
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        return True


def totals():
    files = machines = 0
    todo = 0
    for j in jobs():
        srcs = sources(j)
        for name, _ in srcs:
            out = j / 'dlscan' / f'{name}.tsv'
            if not out.exists():
                todo += 1
                continue
            files += 1
            last = out.read_text().rstrip().rsplit('\n', 1)[-1].split('\t')
            machines += int(dict(x.split('=') for x in last[1:])['machines'])
    hits = [l.split('\t') for l in HITS.read_text().splitlines()[1:]] if HITS.exists() else []
    return files, todo, machines, hits


def status_line():
    files, todo, machines, hits = totals()
    dl = [h for h in hits if h[4] == 'DIGIT-LIST']
    new = [h for h in dl if h[6] != 'known']
    hot = [h for h in dl if h[5] in ('HALT?', 'R4-SOME', 'HALT-SOME', 'CHECK')]
    return (f'digit-list scan: {machines} holdouts in {files} chunk files scanned, {todo} files to do; '
            f'{len(dl)} digit-list machines ({len(new)} not known before, {len(hot)} graded HALT?/R4-SOME/HALT-SOME/CHECK), '
            f'{sum(h[4] == "unconfirmed" for h in hits)} unconfirmed, {sum(h[4] == "partial" for h in hits)} partial')


def scan_file(job, name, path, known, lock):
    out = job / 'dlscan' / f'{name}.tsv'
    tmp = job / 'dlscan' / f'{name}.partial'
    rows, summary = dlscan.screen(path, tmp)
    found = []
    for tm, full, partial in rows:
        verdict, grade, details = dlscan.judge(tm, full, partial)
        found.append((tm, verdict, grade, details))
    with lock:
        if found:
            if not HITS.exists():
                HITS.write_text(HEADER, newline='\n')
            with open(HITS, 'a', newline='\n') as f:
                for tm, verdict, grade, details in found:
                    f.write(f"{time.strftime('%Y-%m-%d_%H:%M')}\t{job.name}\t{name}\t{tm}\t{verdict}\t{grade}\t"
                            f"{'known' if tm in known else 'new'}\t{details}\n")
                    if verdict == 'DIGIT-LIST':
                        print(f"DIGIT-LIST [{grade}] {'(known) ' if tm in known else 'NEW '}{job.name}/{name} {tm}",
                              flush=True)
        tmp.replace(out)        # only now is the chunk marked as scanned
    return int(summary['machines'])


def main():
    if '--status' in sys.argv:
        print(status_line())
        return
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 2
    max_files = int(sys.argv[sys.argv.index('--max-files') + 1]) if '--max-files' in sys.argv else 0
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().split()[0])
        except (ValueError, IndexError):
            pid = -1
        if pid > 0 and pid_alive(pid):
            print(f'dlscan_all is already running (pid {pid}); ' + status_line())
            return
    LOCK.write_text(f'{os.getpid()}\n')
    try:
        known = known_machines()
        todo = []
        for j in jobs():
            (j / 'dlscan').mkdir(exist_ok=True)
            todo += [(j, name, path) for name, path in sources(j) if not (j / 'dlscan' / f'{name}.tsv').exists()]
        if max_files:
            todo = todo[:max_files]
        print(time.strftime('%H:%M:%S'), f'{len(todo)} chunk files to scan with {workers} workers', flush=True)
        lock = threading.Lock()
        done = machines = 0
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for n in pool.map(lambda t: scan_file(*t, known, lock), todo):
                done += 1
                machines += n
                if done % 100 == 0:
                    print(time.strftime('%H:%M:%S'), f'{done}/{len(todo)} files, {machines} holdouts, '
                          f'{(time.time() - t0) / max(machines, 1) * 1000 * workers:.0f} ms each', flush=True)
        print(time.strftime('%H:%M:%S'), f'scanned {machines} holdouts in {done} files this run', flush=True)
        print(status_line(), flush=True)
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
