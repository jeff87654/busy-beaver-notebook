"""Time dlscan2 per machine at Idle priority: python time_one.py LIST.txt [TIMEOUT=60] [STEPS] [N]"""
import subprocess, sys, time, tempfile, os
from pathlib import Path
EXE = Path(__file__).resolve().parent.parent.parent / 'neighbors' / 'dlscan2.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
lst = Path(sys.argv[1]).read_text().split()
to = float(sys.argv[2]) if len(sys.argv) > 2 else 60
extra = sys.argv[3:5]
with tempfile.TemporaryDirectory() as td:
    for m in lst:
        i, o = Path(td) / 'i.txt', Path(td) / 'o.tsv'
        i.write_text(m + '\n')
        t = time.time()
        try:
            subprocess.run([str(EXE), str(i), str(o), *extra], creationflags=LOW, timeout=to)
            rows = [l for l in o.read_text().splitlines()[1:] if not l.startswith('#')]
            g = rows[0].split('\t')[3] if rows else '-'
        except subprocess.TimeoutExpired:
            g = 'TIMEOUT'
        print(f'{time.time() - t:7.2f}s  {g:<11} {m}', flush=True)
