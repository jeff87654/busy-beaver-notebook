"""run2.py: second pass over the pf7 REJECTS (13,994,313 machines in rchunks/r####.txt, 100k each).
Stage A (nlp7r.exe --pilotonly): K pilot 6 x 30k macro + 300k macro at the best K -> P2, slot resets (nsr), first
         slot-reset base step (sr0), max run count.  -> rpil/r####.tsv
Gate     P2 >= 8.0 (fast growth, same gate as the first pass)  OR  nsr >= 2 (>= 2 slot resets at the macro level).
Stage B (nlp7r.exe 1M macro --k2, i.e. the first pass's stage F: FAST, D, FR, ...) on gate passers -> rfull/r####.tsv
Resumable (a file is done when it ends with '#summary'), Idle priority, PIDs appended to pids.txt.
  python run2.py run W | status | stop
"""
import idle  # noqa: F401
import os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = HERE / 'nlp7r.exe'
CH, PIL, FIN, FUL = HERE / 'rchunks', HERE / 'rpil', HERE / 'rfull_in', HERE / 'rfull'
PIDS = HERE / 'pids.txt'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
_lock = threading.Lock()


def done(p):
    if not p.exists(): return False
    with open(p, 'rb') as f:
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 300))
        return b'#summary' in f.read()


def launch(cmd):
    p = subprocess.Popen([str(c) for c in cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=LOW)
    with _lock, open(PIDS, 'a') as f: f.write(f'{p.pid}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\tnlp7r.exe {Path(cmd[1]).name}\n')
    return p.wait()


def one(src, dst, args):
    if done(dst): return
    tmp = dst.with_suffix('.tmp')
    launch([EXE, src, tmp] + args)
    if done(tmp): os.replace(tmp, dst); print(dst.name, flush=True)
    else: print(dst.name, 'FAILED', flush=True)


def gate(l):
    x = l.rstrip('\n').split('\t')
    return len(x) >= 11 and (float(x[3]) >= 8.0 or int(x[9]) >= 2)


def job(c):
    pf = PIL / (c.stem + '.tsv')
    one(c, pf, ['--pilotonly'])
    if not done(pf): return
    s = FIN / (c.stem + '.txt')
    if not s.exists():
        rows = [l.split('\t')[0] for l in open(pf) if not l.startswith(('#', 'machine')) and gate(l)]
        s.write_text('\n'.join(rows) + '\n')
    one(s, FUL / (c.stem + '.tsv'), ['1000000', '--k2'])


def run(w):
    for d in (PIL, FIN, FUL): d.mkdir(exist_ok=True)
    with _lock, open(PIDS, 'a') as f: f.write(f'{os.getpid()}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\tpython.exe (run2 driver)\n')
    with ThreadPoolExecutor(w) as ex: list(ex.map(job, sorted(CH.glob('r*.txt'))))


def status():
    n = len(list(CH.glob('r*.txt')))
    a = sum(done(p) for p in PIL.glob('r*.tsv')) if PIL.exists() else 0
    b = sum(done(p) for p in FUL.glob('r*.tsv')) if FUL.exists() else 0
    print(f'stage A {a}/{n}  stage B {b}/{n}')


def stop():
    for line in open(PIDS):
        f = line.rstrip('\n').split('\t')
        if len(f) < 3 or not ('nlp7r' in f[2] or 'run2' in f[2]): continue
        pid, exe = f[0], f[2].split()[0]
        r = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'], capture_output=True, text=True)
        if exe.lower() in r.stdout.lower():
            subprocess.run(['taskkill', '/PID', pid, '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); print('killed', pid, exe)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'run': run(int(sys.argv[2]))
    elif cmd == 'stop': stop()
    else: status()
