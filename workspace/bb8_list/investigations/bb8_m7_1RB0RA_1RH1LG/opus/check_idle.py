"""Run proofs/check.py on one file at Idle priority (children inherit the priority class)."""
import subprocess, sys
from pathlib import Path
PROOFS = Path(__file__).resolve().parents[3] / 'proofs'
p = subprocess.run([sys.executable, 'check.py', sys.argv[1]], cwd=PROOFS, capture_output=True, text=True,
                   creationflags=subprocess.IDLE_PRIORITY_CLASS)
print('exit', p.returncode)
print((p.stdout + p.stderr)[-3000:])
