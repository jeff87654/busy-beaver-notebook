"""triage7.py: resumable two-stage triage of the BB(7) holdout list (16,949,557 machines in chunks/c#####.txt).

Stage 1, pf7 (prefilter/src/pf7.exe, 300k steps, ~3 ms/machine quiet, 6-9 ms under the shared load): clean-transfer
         pre-filter (passes ~12-18% of holdouts), writes pf7_out/c#####.tsv.
Stage 2, dlscan2 with --skipdl (bb8_list/neighbors/dlscan2_skipdl.exe) on the pf7 survivors of each chunk:
         survivors/c#####.txt -> dl2_out/c#####.tsv.
A file is done when its last line starts with '#summary'. Everything runs at Idle priority.

  python triage7.py run W          # both stages, chunk by chunk, W workers (each worker: pf7 then dlscan2)
  python triage7.py pf W           # stage 1 only
  python triage7.py dl W           # stage 2 only, for chunks whose stage 1 is done
  python triage7.py status         # progress, pass rate, grades; writes hits_triage7.tsv (dlscan2 rows with a grade)
  python triage7.py stop           # kill the worker processes this driver started (PIDs in triage7.pids)

Settings: see PF_ARGS / DL_ARGS below (calibration in prefilter/REPORT.txt).
"""
import idle  # noqa: F401  (Idle priority for this process and its children)
import os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('TRIAGE7_ROOT', HERE))      # override only for tests
CH = ROOT / 'chunks'
PF_EXE = HERE / 'prefilter' / 'src' / 'pf7.exe'
DL_EXE = HERE.parent / 'bb8_list' / 'neighbors' / 'dlscan2_skipdl.exe'
PF_OUT, SURV, DL_OUT = ROOT / 'pf7_out', ROOT / 'survivors', ROOT / 'dl2_out'
PIDS = ROOT / 'triage7.pids'
PF_ARGS = ['300000']                                   # pf7 defaults: --ct=60 --csmin=20 --frac=0.7 --smallspan=60 --ctsmall=3
DL_ARGS = ['1000000', '20000', '--skipdl']             # dlscan2 census 1M, probes 20k (as bb7scan.py), skip dlscan's templates
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
_lock = threading.Lock()


def done(p):
    if not p.exists(): return False
    with open(p, 'rb') as f:
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 400))
        return b'#summary' in f.read()


def launch(cmd):
    p = subprocess.Popen([str(c) for c in cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=LOW)
    with _lock, open(PIDS, 'a') as f: f.write(f'{p.pid}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\t{cmd[0].name}\n')
    return p.wait()


def stage1(c):
    o = PF_OUT / (c.stem + '.tsv')
    if not done(o):
        tmp = o.with_suffix('.tmp')
        launch([PF_EXE, c, tmp] + PF_ARGS)
        if done(tmp): os.replace(tmp, o)
        else: print(c.stem, 'pf7 FAILED', flush=True); return False
    s = SURV / (c.stem + '.txt')
    if not s.exists():
        rows = [l.split('\t')[0] + '\n' for l in open(o) if '\tPASS\t' in l]
        tmp = s.with_suffix('.tmp'); tmp.write_text(''.join(rows)); os.replace(tmp, s)
    return True


def stage2(c):
    s, o = SURV / (c.stem + '.txt'), DL_OUT / (c.stem + '.tsv')
    if done(o) or not s.exists(): return
    tmp = o.with_suffix('.tmp')
    launch([DL_EXE, s, tmp] + DL_ARGS)
    if done(tmp): os.replace(tmp, o)
    else: print(c.stem, 'dlscan2 FAILED', flush=True)


def run(mode, workers):
    for d in (PF_OUT, SURV, DL_OUT): d.mkdir(exist_ok=True)
    with _lock, open(PIDS, 'a') as f: f.write(f'{os.getpid()}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\tpython.exe (driver {mode})\n')
    chunks = sorted(CH.glob('c*.txt'))
    def one(c):
        if mode in ('run', 'pf'):
            if not stage1(c): return
        if mode in ('run', 'dl'): stage2(c)
        print(c.stem, flush=True)
    todo = [c for c in chunks if not (done(DL_OUT / (c.stem + '.tsv')) if mode != 'pf' else done(PF_OUT / (c.stem + '.tsv')))]
    print(len(todo), 'chunks to do', flush=True)
    with ThreadPoolExecutor(workers) as ex: list(ex.map(one, todo))


def status():
    nch = len(list(CH.glob('c*.txt')))
    pf = [p for p in sorted(PF_OUT.glob('c*.tsv')) if done(p)] if PF_OUT.exists() else []
    n = npass = 0
    for p in pf:
        for line in open(p):
            if line.startswith('#summary'):
                f = dict(x.split('=') for x in line.split('\t')[1:])
                n += int(f['machines']); npass += int(f['pass'])
    dl = [p for p in sorted(DL_OUT.glob('c*.tsv')) if done(p)] if DL_OUT.exists() else []
    hits, grades = [], {}
    for p in dl:
        for line in open(p):
            f = line.rstrip('\n').split('\t')
            if line.startswith(('#', 'machine')) or len(f) < 4 or f[3] == '-': continue
            hits.append(line); grades[f[3]] = grades.get(f[3], 0) + 1
    (ROOT / 'hits_triage7.tsv').write_text(''.join(hits))
    print(f'pf7: {len(pf)}/{nch} chunks, {n} machines, {npass} PASS ({100 * npass / max(n, 1):.2f}%)')
    print(f'dlscan2_skipdl: {len(dl)}/{nch} chunks, {len(hits)} graded rows -> hits_triage7.tsv', grades)


def stop():
    if not PIDS.exists(): print('no pids file'); return
    # only PIDs this driver recorded, and only if that PID still runs one of our two executables (PIDs get reused)
    for line in open(PIDS):
        f = line.rstrip('\n').split('\t')
        if len(f) < 3: continue
        pid, exe = f[0], f[2].split()[0]       # the driver's own line first, so it spawns nothing new
        r = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'], capture_output=True, text=True)
        if exe.lower() in r.stdout.lower():
            subprocess.run(['taskkill', '/PID', pid, '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print('killed', pid, exe)
    print('done')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd in ('run', 'pf', 'dl'): run(cmd, int(sys.argv[2]))
    elif cmd == 'stop': stop()
    else: status()
