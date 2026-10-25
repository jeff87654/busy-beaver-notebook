"""Parallel dlscan3 scan at Idle priority.

  python scan.py OUTDIR NPROC CENSUS FILE [FILE ...] [--chunk 1500] [--exe dlscan3.exe] [--extra "--span=32768"]
                 [--reset-claims]

Copies the machines of the input files (as they are now: files still being appended are read up to their current end)
into OUTDIR/chunks/c_NNNN.txt, runs dlscan3.exe on each chunk (NPROC at a time, Idle priority, probe budget 20000),
writes OUTDIR/out/c_NNNN.tsv, and finally OUTDIR/merged.tsv (all graded rows) and OUTDIR/summary.txt.
Chunks whose .tsv already ends with a #summary line are skipped, so a stopped scan can be resumed. A killed driver
leaves claim files (OUTDIR/claims/c_NNNN) for chunks it never finished; --reset-claims deletes the claims of all
unfinished chunks at start (use it only when no other driver works on OUTDIR). Note: the chunk list is fixed when
OUTDIR/chunks is first written; machines appended to the inputs later need a new OUTDIR (or rm -r OUTDIR/chunks
after a completed scan, which re-chunks and re-scans everything).
PIDs of running workers are kept in OUTDIR/pids.txt.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = HERE / 'dlscan3.exe'
IDLE = 0x00000040  # IDLE_PRIORITY_CLASS


def main():
    args = sys.argv[1:]
    chunk = 1500
    extra = []
    if '--chunk' in args:
        i = args.index('--chunk'); chunk = int(args[i + 1]); del args[i:i + 2]
    exe = EXE
    if '--exe' in args:
        i = args.index('--exe'); exe = HERE / args[i + 1]; del args[i:i + 2]
    reset = '--reset-claims' in args
    if reset:
        args.remove('--reset-claims')
    if '--extra' in args:
        i = args.index('--extra'); extra = args[i + 1].split(); del args[i:i + 2]
    outdir, nproc, census, files = Path(args[0]), int(args[1]), args[2], args[3:]
    (outdir / 'chunks').mkdir(parents=True, exist_ok=True)
    (outdir / 'out').mkdir(parents=True, exist_ok=True)
    chunks = sorted((outdir / 'chunks').glob('c_*.txt'))
    if not chunks:
        machines, seen = [], set()
        for f in files:
            with open(f) as fh:
                for line in fh:
                    m = line.split()[0] if line.strip() else ''
                    if '_' in m and m not in seen:
                        seen.add(m); machines.append(m)
        for k in range(0, len(machines), chunk):
            p = outdir / 'chunks' / f'c_{k // chunk:04d}.txt'
            p.write_text('\n'.join(machines[k:k + chunk]) + '\n')
        (outdir / 'inputs.txt').write_text(''.join(f'{f}\n' for f in files) + f'machines {len(machines)}\n')
        chunks = sorted((outdir / 'chunks').glob('c_*.txt'))

    def done(c):
        o = outdir / 'out' / (c.stem + '.tsv')
        if not o.exists():
            return False
        lines = o.read_text().splitlines()
        return bool(lines) and lines[-1].startswith('#summary')

    # Chunks are claimed with an exclusive claim file, so two drivers on the same OUTDIR share the work instead of
    # duplicating it (remove OUTDIR/claims to re-run unfinished chunks after a crash).
    (outdir / 'claims').mkdir(exist_ok=True)
    if reset:
        for c in chunks:
            if not done(c):
                (outdir / 'claims' / c.stem).unlink(missing_ok=True)

    def claim(c):
        try:
            fd = os.open(str(outdir / 'claims' / c.stem), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode()); os.close(fd)
            return True
        except FileExistsError:
            return False

    todo = [c for c in chunks if not done(c)]
    failed = set()
    running = {}
    t0 = time.time()
    while todo or running:
        while todo and len(running) < nproc:
            c = todo.pop(0)
            if not claim(c):
                continue
            o = outdir / 'out' / (c.stem + '.tsv')
            err = open(outdir / 'out' / (c.stem + '.err'), 'w')
            p = subprocess.Popen([str(exe), str(c), str(o), census, '20000'] + extra, stdout=err, stderr=err,
                                 creationflags=IDLE)
            running[p] = (c, err)
        (outdir / 'pids.txt').write_text(''.join(f'{p.pid}\n' for p in running))
        time.sleep(2)
        for p in list(running):
            if p.poll() is not None:
                c, err = running.pop(p)
                err.close()
                print(f'{time.time() - t0:8.0f}s done {c.name} rc={p.returncode}, {len(todo)} left', flush=True)
                if not done(c):                    # failed or killed: release the claim, do not wait for it
                    (outdir / 'claims' / c.stem).unlink(missing_ok=True)
                    failed.add(c)
    (outdir / 'pids.txt').write_text('')
    # chunks claimed by another driver may still be running: wait for them (at most 6 h) before merging
    t1 = time.time()
    while not all(done(c) or c in failed or not (outdir / 'claims' / c.stem).exists() for c in chunks)             and time.time() - t1 < 6 * 3600:
        time.sleep(10)
    # merge
    rows, summ = [], {}
    for c in chunks:
        o = outdir / 'out' / (c.stem + '.tsv')
        for line in o.read_text().splitlines():
            if line.startswith('machine\t'):
                continue
            if line.startswith('#summary'):
                for kv in line.split('\t')[1:]:
                    k, v = kv.split('=')
                    summ[k] = summ.get(k, 0) + int(v)
                continue
            rows.append(line)
    order = ['W1-HALTER', 'W1-LOOPER', 'MULTI', 'LOOPER', 'REBUILD', 'CHAMPION', 'R4-SOME', 'HALT?', 'HALT-SOME',
             'CHECK', 'NOBOUNDARY', 'SAFE']
    rows.sort(key=lambda r: order.index(r.split('\t')[3]) if r.split('\t')[3] in order else 99)
    with open(outdir / 'merged.tsv', 'w') as fh:
        fh.write('machine\thalted_step\tn_templates\tgrade\ttemplate\tw1\tparams\n')
        fh.write(''.join(r + '\n' for r in rows))
    (outdir / 'summary.txt').write_text(' '.join(f'{k}={v}' for k, v in summ.items()) + '\n')
    print('summary:', summ)


if __name__ == '__main__':
    main()
