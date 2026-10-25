"""Compile one .v (anywhere) against busycoq + bb8_list/proofs at Idle priority; print time and errors."""
import subprocess, sys, time
from pathlib import Path
PROOFS = Path(__file__).resolve().parents[3] / 'proofs'
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.run([COQC] + FLAGS + [v.name], cwd=v.parent, capture_output=True, text=True,
                   creationflags=subprocess.IDLE_PRIORITY_CLASS, timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 1800)
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (p.stdout + p.stderr).strip()
print(out[-4000:])
