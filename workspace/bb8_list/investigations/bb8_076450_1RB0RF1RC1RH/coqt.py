"""Compile a scratch .v with a time limit (kills only its own coqc child on timeout)."""
import subprocess, sys, time
from pathlib import Path
PROOFS = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs')
BUSY = Path(r'C:\Users\jeffr\Downloads\bb8\third_party\busycoq\verify')
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
lim = float(sys.argv[2]) if len(sys.argv) > 2 else 300
f = Path(sys.argv[1]).resolve()
t = time.time()
p = subprocess.Popen([COQC, '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(f.parent), 'Scratch', str(f)],
                     cwd=f.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    out, err = p.communicate(timeout=lim)
    print(out[-3000:]); print(err[-3000:])
    print(f.name, 'exit', p.returncode, 'time %.1fs' % (time.time() - t))
except subprocess.TimeoutExpired:
    p.kill(); p.communicate()
    print(f.name, 'TIMEOUT after %.0fs' % lim)
