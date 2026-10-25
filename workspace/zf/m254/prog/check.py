"""Check the m254 program layer from scratch.

1. Regenerate Dag254.v and Cert254.v (tools/gen_coq.py) and require them to be
   byte-identical to the checked-in files (paths.json and the Wade compile are the only inputs).
2. Reject Admitted / admit / Axiom / Parameter in coq/*.v.
3. Rebuild coq/ from clean (Idle priority) and require every Print Assumptions to be closed.

Usage: python -I check.py"""
import re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
COQ = HERE / 'coq'
GEN = ['Dag254.v', 'Cert254.v']

old = {f: (COQ / f).read_bytes() for f in GEN}
subprocess.run([sys.executable, '-I', str(HERE / 'tools' / 'gen_coq.py')], check=True, capture_output=True)
for f in GEN:
    if (COQ / f).read_bytes() != old[f]:
        sys.exit(f'FAIL: regenerated {f} differs from the checked-in file')
print('generated files reproduce')

bad = [f'{v.name}:{i + 1}' for v in COQ.glob('*.v')
       for i, l in enumerate(re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S).splitlines())
       if re.search(r'\b(Admitted|admit|Axiom|Parameter)\b', l)]
if bad:
    sys.exit('FAIL: ' + ', '.join(bad))
print('no Admitted / axioms in the sources')

for p in COQ.iterdir():
    if p.suffix in ('.vo', '.vok', '.vos', '.glob'):   # own files only; M254 / M254L are built by their owners
        p.unlink()
r = subprocess.run([sys.executable, str(COQ / 'build.py'), 'Main254.v'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
print(r.stdout)
if r.returncode:
    sys.exit('FAIL: build\n' + r.stderr)
lines = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith('compiled ')]
if not lines or any(l.strip() != 'Closed under the global context' for l in lines):
    sys.exit('FAIL: some Print Assumptions output is not closed')
print('CHECK PASS: prog254 closed under the global context')
