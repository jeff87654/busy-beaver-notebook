"""run.py: resumable driver for the non-list pool scan (Idle priority, PIDs -> pids.txt).

  python run.py split            # pool.txt -> pchunks/p####.txt (25k machines each)
  python run.py pilot W          # stage P: nlp7 --pilotonly on every chunk -> pil_out/p####.tsv
  python run.py full W [TH]      # stage F: nlp7 1M macro --k2 on pilot P2 (300k macro steps, col 4) >= TH (default 8.0) -> full_out/p####.tsv
  python run.py run W [TH]       # both stages chunk by chunk
  python run.py stop             # kill PIDs from pids.txt that still run nlp7/python
  python run.py status
A file is done when it ends with a '#summary' line; temp files are renamed on success.
"""
import idle  # noqa: F401
import os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = HERE / 'nlp7.exe'          # stage P binary (pilot mode)
EXEF = HERE / 'nlp7f.exe'        # stage F binary (same source, final version with FR)
PCH, PIL, SUR, FUL = HERE / 'pchunks', HERE / 'pil_out', HERE / 'full_in', HERE / 'full_out'
PIDS = HERE / 'pids.txt'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
_lock = threading.Lock()
CH = 25000


def done(p):
    if not p.exists(): return False
    with open(p, 'rb') as f:
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 300))
        return b'#summary' in f.read()


def launch(cmd):
    p = subprocess.Popen([str(c) for c in cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=LOW)
    with _lock, open(PIDS, 'a') as f: f.write(f'{p.pid}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\t{Path(cmd[0]).name} {Path(cmd[1]).name}\n')
    return p.wait()


def split():
    PCH.mkdir(exist_ok=True)
    ms = open(HERE / 'pool.txt').read().split()
    for i in range(0, len(ms), CH):
        (PCH / f'p{i // CH:04d}.txt').write_text('\n'.join(ms[i:i + CH]) + '\n')
    print(len(ms), 'machines', (len(ms) + CH - 1) // CH, 'chunks')


def one(src, dst, args, exe=None):
    if done(dst): return
    tmp = dst.with_suffix('.tmp')
    launch([exe or EXE, src, tmp] + args)
    if done(tmp): os.replace(tmp, dst); print(dst.name, flush=True)
    else: print(dst.name, 'FAILED', flush=True)


def stage(mode, workers, th):
    for d in (PIL, SUR, FUL): d.mkdir(exist_ok=True)
    with _lock, open(PIDS, 'a') as f: f.write(f'{os.getpid()}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\tpython.exe (driver {mode})\n')
    chunks = sorted(PCH.glob('p*.txt'))
    def job(c):
        if mode in ('pilot', 'run'):
            one(c, PIL / (c.stem + '.tsv'), ['--pilotonly'])
        if mode in ('full', 'run'):
            pf = PIL / (c.stem + '.tsv')
            if not done(pf): return
            s = SUR / (c.stem + '.txt')
            if not s.exists():
                rows = [l.split('\t')[0] for l in open(pf) if not l.startswith(('#', 'machine'))
                        and float(l.split('\t')[3]) >= th]
                s.write_text('\n'.join(rows) + '\n')
            one(s, FUL / (c.stem + '.tsv'), ['1000000', '--k2'], EXEF)
    with ThreadPoolExecutor(workers) as ex: list(ex.map(job, chunks))


def status():
    n = len(list(PCH.glob('p*.txt')))
    pd = [p for p in PIL.glob('p*.tsv') if done(p)] if PIL.exists() else []
    fd = [p for p in FUL.glob('p*.tsv') if done(p)] if FUL.exists() else []
    print(f'pilot {len(pd)}/{n}  full {len(fd)}/{n}')


def stop():
    for line in open(PIDS):
        f = line.rstrip('\n').split('\t')
        if len(f) < 3: continue
        pid, exe = f[0], f[2].split()[0]
        r = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'], capture_output=True, text=True)
        if exe.lower() in r.stdout.lower():
            subprocess.run(['taskkill', '/PID', pid, '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); print('killed', pid, exe)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'split': split()
    elif cmd in ('pilot', 'full', 'run'): stage(cmd, int(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 8.0)
    elif cmd == 'stop': stop()
    else: status()
