"""Compile a .v at Idle priority with -time, streaming coqc output to <file>.log (so progress can be watched)."""
import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1] / "proofs"
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(HERE / 'dev'), 'Dev', '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8']
v = Path(sys.argv[1]).resolve()
extra = sys.argv[2:]
log = open(str(v) + '.log', 'w')
t0 = time.time()
p = subprocess.run([COQC] + FLAGS + extra + [v.name], cwd=v.parent, stdout=log, stderr=subprocess.STDOUT,
                   creationflags=subprocess.IDLE_PRIORITY_CLASS)
log.write('\nEXIT %d %.1fs\n' % (p.returncode, time.time() - t0))
log.close()
