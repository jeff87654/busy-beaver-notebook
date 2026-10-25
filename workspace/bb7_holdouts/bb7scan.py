"""Resumable digit-list scan of the BB(7) holdout list (June 2026, 16,949,557 machines).

  python bb7scan.py split                       # cut the list into chunks/c#####.txt (50,000 machines each)
  python bb7scan.py run dlscan|dlscan2 WORKERS  # scan every chunk not yet done (Idle priority), resumable
  python bb7scan.py status

Outputs: out_<scanner>/c#####.tsv (a chunk is done when its last line starts with '#summary').
Settings: census 1,000,000 steps (calibration on the 24 known digit-list machines: identical detection at
5M / 1M / 300k), probes 100,000 (dlscan) / 20,000 (dlscan2).
Hits: dlscan rows with full keys, dlscan2 rows with a grade -> hits_<scanner>.tsv (python bb7scan.py status).
"""
import gzip, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
NB = HERE.parent / 'bb8_list' / 'neighbors'
SRC = HERE / 'june2026' / 'undecided_06.06.2026_16,949,557.txt.gz'
CH = HERE / 'chunks'
ARGS = {'dlscan': ['1000000', '100000'], 'dlscan2': ['1000000', '20000']}
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)

def split():
    CH.mkdir(exist_ok=True)
    buf, k = [], 0
    with gzip.open(SRC, 'rt') as f:
        for line in f:
            buf.append(line.split()[0] + '\n')
            if len(buf) == 50000:
                (CH / f'c{k:05d}.txt').write_text(''.join(buf)); buf, k = [], k + 1
    if buf:
        (CH / f'c{k:05d}.txt').write_text(''.join(buf)); k += 1
    print(k, 'chunks')

def done(p):
    if not p.exists(): return False
    with open(p, 'rb') as f:
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 400))
        return b'#summary' in f.read()

def run(scanner, workers):
    out = HERE / f'out_{scanner}'; out.mkdir(exist_ok=True)
    todo = [c for c in sorted(CH.glob('c*.txt')) if not done(out / (c.stem + '.tsv'))]
    print(len(todo), 'chunks to do', flush=True)
    def one(c):
        subprocess.run([str(NB / f'{scanner}.exe'), str(c), str(out / (c.stem + '.tsv'))] + ARGS[scanner],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=LOW)
        print(c.stem, flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, todo))

def status():
    nch = len(list(CH.glob('c*.txt')))
    for scanner in ARGS:
        out = HERE / f'out_{scanner}'
        files = [p for p in sorted(out.glob('c*.tsv')) if done(p)] if out.exists() else []
        hits = []
        for p in files:
            for line in open(p):
                f = line.rstrip('\n').split('\t')
                if line.startswith(('#', 'machine')) or len(f) < 4: continue
                if scanner == 'dlscan' and f[3] not in ('', '0', '-'): hits.append(line)
                if scanner == 'dlscan2' and f[3] != '-': hits.append(line)
        (HERE / f'hits_{scanner}.tsv').write_text(''.join(hits))
        print(f'{scanner}: {len(files)}/{nch} chunks done, {len(hits)} hits')

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'split': split()
    elif cmd == 'run': run(sys.argv[2], int(sys.argv[3]))
    else: status()
