import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROOFS = (HERE / '..' / '..' / '..' / 'proofs').resolve()
BUSY = (HERE / '..' / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
t = time.time()
for f in sys.argv[1:]:
    r = subprocess.run([COQC, '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(HERE), 'BB8dev', f], cwd=HERE, capture_output=True, text=True)
    print(f, r.stdout[-3000:], r.stderr[-3000:], 'rc', r.returncode, 'time %.1f' % (time.time() - t))
    if r.returncode: break
