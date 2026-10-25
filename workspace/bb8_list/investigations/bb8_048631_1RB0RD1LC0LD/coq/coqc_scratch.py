import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROOFS = (HERE / '..' / '..' / '..' / 'proofs').resolve()
BUSY = (HERE / '..' / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
f = sys.argv[1]
t = time.time()
r = subprocess.run([COQC, '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', f], cwd=HERE, capture_output=True, text=True)
print(r.stdout[-6000:], r.stderr[-6000:])
print('rc', r.returncode, 'time %.1f' % (time.time() - t))
