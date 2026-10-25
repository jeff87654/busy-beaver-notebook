"""Compile with -time at Idle, streaming output to FILE.log.  python coqc_time.py FILE.v"""
import subprocess, sys
from pathlib import Path
PROOFS = Path(__file__).resolve().parents[2] / "proofs"
BUSY = (PROOFS / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
v = Path(sys.argv[1]).resolve()
log = open(str(v) + '.timelog', 'w')
p = subprocess.Popen([COQC, '-time', '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', v.name], cwd=v.parent,
                     stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.IDLE_PRIORITY_CLASS)
print('pid', p.pid, 'exit', p.wait())
