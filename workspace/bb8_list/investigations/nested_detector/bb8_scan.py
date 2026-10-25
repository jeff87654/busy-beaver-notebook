"""Incremental dlscan3 (nested digit-list / f_{omega+1}) scan of every enumerated BB(8) holdout chunk.

  python bb8_scan.py [--workers 2] [--census 1000000] [--max-files N]   scan the chunk files not scanned yet, then exit
  python bb8_scan.py --status                                           print the totals only

Companion of neighbors/dlscan2_all.py. It uses the same chunk files: jobs8/<job>/results/<chunk>_holdouts.txt,
taken once their _stats.json exists, plus the seed holdouts.
- Output per chunk: jobs8/<job>/dlscan3/<chunk>.tsv. A chunk counts as scanned when its file ends with the
  "#summary" line, so an interrupted run is simply resumed.
- Rows graded W1-HALTER, W1-HALT?, W1-LOOPER or MULTI are appended to nested_detector/dl3_hits.tsv.
- Runs at Idle priority. Only one instance runs at a time (bb8_scan.lock).
- Cost: about 0.4-1.0 s per holdout. The full 1.55M set is 170-430 CPU-hours; see ../nested_detector.md.
- Census: 1e6 (default) catches every structure seen at 1e6. --census 20000000 also catches BB(13)-like late starts
  (its nested phase begins at step 1.18e7), at about 1.5-2x the cost.
"""
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                       # bb8_list
sys.path.insert(0, str(ROOT / 'neighbors'))
import dlscan_all  # noqa: E402  (jobs, sources, pid_alive)

EXE = HERE / 'dlscan3.exe'
HITS = HERE / 'dl3_hits.tsv'
LOCK = HERE / 'bb8_scan.lock'
HEADER = 'time\tjob\tchunk\tmachine\tgrade\ttemplate\tw1\n'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
INTERESTING = ('W1-HALTER', 'W1-HALT?', 'W1-LOOPER', 'MULTI')


def finished(out):
    if not out.exists():
        return False
    lines = out.read_text().splitlines()
    return bool(lines) and lines[-1].startswith('#summary')


def todo_files():
    out = []
    for j in dlscan_all.jobs():
        for name, src in dlscan_all.sources(j):
            dst = j / 'dlscan3' / f'{name}.tsv'
            if not finished(dst):
                out.append((j, name, src, dst))
    return out


def totals():
    files = machines = todo = 0
    for j in dlscan_all.jobs():
        for name, _ in dlscan_all.sources(j):
            dst = j / 'dlscan3' / f'{name}.tsv'
            if finished(dst):
                files += 1
                last = dst.read_text().splitlines()[-1]
                machines += int(dict(x.split('=') for x in last.split('\t')[1:]).get('machines', 0))
            else:
                todo += 1
    hits = max(0, len(HITS.read_text().splitlines()) - 1) if HITS.exists() else 0
    return files, todo, machines, hits


def scan_file(job, name, src, dst, census, lock):
    dst.parent.mkdir(exist_ok=True)
    tmp = dst.with_suffix('.part')
    with open(dst.with_suffix('.err'), 'w') as err:
        subprocess.run([str(EXE), str(src), str(tmp), census, '20000'], stdout=err, stderr=err, creationflags=LOW)
    lines = tmp.read_text().splitlines() if tmp.exists() else []
    if not lines or not lines[-1].startswith('#summary'):
        return 0                                  # killed or failed: left for the next run
    os.replace(tmp, dst)
    rows = [l.split('\t') for l in lines[1:-1]]
    hits = [r for r in rows if len(r) > 5 and r[3] in INTERESTING]
    if hits:
        with lock:
            new = not HITS.exists()
            with open(HITS, 'a') as fh:
                if new:
                    fh.write(HEADER)
                for r in hits:
                    fh.write(f'{time.strftime("%Y-%m-%d %H:%M")}\t{job.name}\t{name}\t{r[0]}\t{r[3]}\t{r[4]}\t{r[5]}\n')
    return int(dict(x.split('=') for x in lines[-1].split('\t')[1:]).get('machines', 0))


def main():
    args = sys.argv[1:]
    if '--status' in args:
        f, t, m, h = totals()
        print(f'dlscan3 BB(8) scan: {m} holdouts in {f} chunk files scanned, {t} files to do; {h} rows in {HITS.name}')
        return
    workers = int(args[args.index('--workers') + 1]) if '--workers' in args else 2
    census = args[args.index('--census') + 1] if '--census' in args else '1000000'
    maxf = int(args[args.index('--max-files') + 1]) if '--max-files' in args else None
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip() or 0)
        except ValueError:
            pid = 0
        if pid > 0 and dlscan_all.pid_alive(pid):
            print(f'another bb8_scan.py is running (pid {pid})')
            return
    LOCK.write_text(str(os.getpid()))
    try:
        todo = todo_files()
        if maxf is not None:
            todo = todo[:maxf]
        print(f'{len(todo)} chunk files to scan with {workers} workers, census {census}', flush=True)
        lock = threading.Lock()
        done = [0, 0]
        t0 = time.time()

        def one(item):
            n = scan_file(*item, census, lock)
            with lock:
                done[0] += 1
                done[1] += n
                print(f'{time.time() - t0:8.0f}s {item[0].name}/{item[1]}: {n} machines ({done[0]}/{len(todo)} files, '
                      f'{done[1]} machines)', flush=True)

        with ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(one, todo))
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
