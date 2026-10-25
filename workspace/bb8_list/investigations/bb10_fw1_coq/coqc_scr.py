"""Compile a scratch .v with scratch/ bound to logical path Scr (plus busycoq and proofs/ as BB8), at Idle priority."""
import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1] / "proofs"
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(HERE / 'scratch'), 'Scr']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.run([COQC] + FLAGS + [v.name], cwd=v.parent, capture_output=True, text=True,
                   creationflags=subprocess.IDLE_PRIORITY_CLASS)
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
print((p.stdout + p.stderr).strip()[-3000:])
