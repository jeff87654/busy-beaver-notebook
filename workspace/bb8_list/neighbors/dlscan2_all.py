"""Incremental scan of every enumerated holdout with the generalised digit-list screen (dlscan2.exe).

  python dlscan2_all.py [--workers 2] [--max-files N]     scan the chunk files not scanned yet, then exit
  python dlscan2_all.py --status                          print the totals only

Companion of dlscan_all.py (which runs dlscan.exe + kfit.py). dlscan2.exe infers more general templates
(prefix and suffix blocks, units starting with 0, digits written as alpha*d+beta repeats) and also grades
CHAMPION: the BB(7) champion's structure, a digit-list counter that halts when its list is used up.
Screen output per chunk: jobs8/<job>/dlscan2/<chunk>.tsv. Every graded machine is re-checked with 1,000,000-step
probes (dlscan2.exe on that machine alone) and appended to neighbors/dl2_hits.tsv:
  time, job, chunk, machine, grade (20,000-step screen), grade (1,000,000-step check), known, template, params.
Runs at Idle priority. Only one instance runs at a time (dlscan2_all.lock).
"""
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dlscan_all  # noqa: E402  (sources, jobs, known_machines, pid_alive)

EXE = HERE / 'dlscan2.exe'
HITS = HERE / 'dl2_hits.tsv'
LOCK = HERE / 'dlscan2_all.lock'
HEADER = 'time\tjob\tchunk\tmachine\tgrade\tcheck_grade\tknown\ttemplate\tparams\n'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
INTERESTING = ('CHAMPION', 'R4-SOME', 'HALT?', 'HALT-SOME', 'CHECK')


def screen(src, out, N=20000):
    subprocess.run([str(EXE), str(src), str(out), '5000000', str(N)], check=True, creationflags=LOW)
    rows, summary = [], None
    for l in Path(out).read_text().splitlines()[1:]:
        f = l.split('\t')
        if f[0] == '#summary':
            summary = dict(x.split('=') for x in f[1:])
        else:
            rows.append(f)
    return rows, summary


def recheck(tm, job):
    src = job / 'dlscan2' / 'recheck.txt'
    out = job / 'dlscan2' / 'recheck.tsv'
    src.write_text(tm + '\n')
    rows, _ = screen(src, out, N=1000000)
    return rows[0][3] if rows else '-'


def totals():
    files = machines = todo = 0
    for j in dlscan_all.jobs():
        for name, _ in dlscan_all.sources(j):
            out = j / 'dlscan2' / f'{name}.tsv'
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
    by = {}
    for h in hits:
        by[h[5]] = by.get(h[5], 0) + 1
    new_hot = [h for h in hits if h[5] in INTERESTING and h[6] != 'known']
    return (f'generalised digit-list scan: {machines} holdouts in {files} chunk files scanned, {todo} files to do; '
            f'graded {dict(sorted(by.items()))}; {len(new_hot)} new CHAMPION/R4-SOME/HALT?/HALT-SOME/CHECK')


def scan_file(job, name, path, known, lock):
    out = job / 'dlscan2' / f'{name}.tsv'
    tmp = job / 'dlscan2' / f'{name}.partial'
    rows, summary = screen(path, tmp)
    found = [(f[0], f[3], f[4], f[5]) for f in rows if f[3] != '-']
    with lock:
        if found:
            if not HITS.exists():
                HITS.write_text(HEADER, newline='\n')
            for tm, grade, tmpl, params in found:
                chk = recheck(tm, job)
                with open(HITS, 'a', newline='\n') as f:
                    f.write(f"{time.strftime('%Y-%m-%d_%H:%M')}\t{job.name}\t{name}\t{tm}\t{grade}\t{chk}\t"
                            f"{'known' if tm in known else 'new'}\t{tmpl}\t{params}\n")
                if chk in INTERESTING:
                    print(f"{chk} {'(known) ' if tm in known else 'NEW '}{job.name}/{name} {tm}", flush=True)
        tmp.replace(out)
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
        if pid > 0 and dlscan_all.pid_alive(pid):
            print(f'dlscan2_all is already running (pid {pid}); ' + status_line())
            return
    LOCK.write_text(f'{os.getpid()}\n')
    try:
        known = dlscan_all.known_machines()
        todo = []
        for j in dlscan_all.jobs():
            (j / 'dlscan2').mkdir(exist_ok=True)
            todo += [(j, n, p) for n, p in dlscan_all.sources(j) if not (j / 'dlscan2' / f'{n}.tsv').exists()]
        if max_files:
            todo = todo[:max_files]
        print(time.strftime('%H:%M:%S'), f'{len(todo)} chunk files to scan with {workers} workers', flush=True)
        lock = threading.Lock()
        done = machines = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for n in pool.map(lambda t: scan_file(*t, known, lock), todo):
                done += 1
                machines += n
                if done % 100 == 0:
                    print(time.strftime('%H:%M:%S'), f'{done}/{len(todo)} files (in submission order), {machines} holdouts',
                          flush=True)
        print(time.strftime('%H:%M:%S'), f'scanned {machines} holdouts in {done} files this run', flush=True)
        print(status_line(), flush=True)
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
