"""Run coqc -time on a file and print the slowest sentences. Usage: python tools/coqtime.py coq/File.v [N]"""
import re, subprocess, sys
from pathlib import Path
v = Path(sys.argv[1]).resolve(); N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
here = v.parent
r = subprocess.run([COQC, '-Q', str(here), 'ZF', '-Q', str((here / '../../third_party/busycoq/verify').resolve()), 'BusyCoq', '-time', str(v)],
                   cwd=here, capture_output=True, text=True)
rows = []
for m in re.finditer(r'Chars (\d+) - (\d+) \[(.*?)\] ([0-9.]+) secs', r.stdout):
    rows.append((float(m.group(4)), int(m.group(1)), m.group(3)[:60]))
src = v.read_text(encoding='utf-8')
tot = sum(t for t, _, _ in rows)
for t, c, s in sorted(rows, reverse=True)[:N]:
    line = src[:c].count('\n') + 1  # approx (chars vs bytes)
    print(f'{t:8.3f}s  line~{line}  {s}')
print(f'total {tot:.1f}s', 'ERR' if r.returncode else '', r.stderr[-2000:])
