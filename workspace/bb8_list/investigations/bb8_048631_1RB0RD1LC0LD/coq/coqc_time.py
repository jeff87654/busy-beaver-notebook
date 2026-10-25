import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PROOFS = (HERE / '..' / '..' / '..' / 'proofs').resolve()
BUSY = (HERE / '..' / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
f = sys.argv[1]
t = time.time()
r = subprocess.run([COQC, '-time', '-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', f], cwd=HERE, capture_output=True, text=True)
lines = r.stdout.splitlines()
import re
rows = []
for ln in lines:
    m = re.match(r'Chars (\d+) - (\d+) \[(.*)\] ([\d.]+) secs', ln)
    if m:
        rows.append((float(m.group(4)), m.group(3)[:100]))
rows.sort(reverse=True)
for sec, cmd in rows[:25]:
    print('%7.2f  %s' % (sec, cmd))
print('total listed %.1f' % sum(r[0] for r in rows))
print(r.stderr[-3000:])
print('rc', r.returncode, 'time %.1f' % (time.time() - t))
