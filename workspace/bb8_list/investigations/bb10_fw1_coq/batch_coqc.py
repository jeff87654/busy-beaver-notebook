"""Compile several .v files with at most 2 concurrent coqc processes at Idle priority; one log line per file.
  python batch_coqc.py LOG f1.v f2.v ..."""
import subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
PROOFS = Path(__file__).resolve().parents[2] / "proofs"
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8']
log = open(sys.argv[1], 'a')
def one(f):
    v = Path(f).resolve(); t0 = time.time()
    p = subprocess.run([COQC] + FLAGS + [v.name], cwd=v.parent, capture_output=True, text=True,
                       creationflags=subprocess.IDLE_PRIORITY_CLASS)
    out = (p.stdout + p.stderr).strip().replace('\n', ' | ')
    line = '%s exit=%d %.0fs %s' % (v.name, p.returncode, time.time() - t0, out[-700:])
    log.write(line + '\n'); log.flush()
    return line
with ThreadPoolExecutor(2) as ex:
    for r in ex.map(one, sys.argv[2:]):
        print(r, flush=True)
