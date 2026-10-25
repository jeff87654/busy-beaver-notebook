"""Compile one .v against busycoq + bb8_list/proofs at Idle priority; print time and the tail of the output.
  python coqc_idle.py FILE.v [timeout_s]"""
import subprocess, sys, time
from pathlib import Path
PROOFS = Path(__file__).resolve().parents[2] / "proofs"
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                     creationflags=subprocess.IDLE_PRIORITY_CLASS)
print('pid', p.pid, flush=True)
try:
    out, _ = p.communicate(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 7200)
except subprocess.TimeoutExpired:
    p.kill(); out = 'TIMEOUT'
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
print(out.strip()[-5000:])
