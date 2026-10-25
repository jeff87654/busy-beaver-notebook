"""Compile a scratch .v file with the same logical paths as build.py (BusyCoq, BB8)."""
import subprocess, sys, time
from pathlib import Path
PROOFS = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs')
BUSY = Path(r'C:\Users\jeffr\Downloads\bb8\third_party\busycoq\verify')
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
f = Path(sys.argv[1]).resolve()
t = time.time()
r = subprocess.run([COQC, '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(f.parent), 'Scratch', str(f)],
                   cwd=f.parent, capture_output=True, text=True)
print(r.stdout[-6000:])
print(r.stderr[-6000:])
print('exit', r.returncode, 'time %.1fs' % (time.time() - t))
