"""Compile one .v against busycoq + bb8_list/proofs (+ this folder as Dev) at Idle priority (house rule; BelowNormal was used once, when Idle starved
on the saturated machine: a trivial file did not finish in 15 min); print time and errors."""
import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[2] / "proofs"
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(HERE), 'Dev']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.run([COQC] + FLAGS + [v.name], cwd=v.parent, capture_output=True, text=True,
                   creationflags=subprocess.IDLE_PRIORITY_CLASS, timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 3600)
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (p.stdout + p.stderr).strip()
print(out[-4000:])
