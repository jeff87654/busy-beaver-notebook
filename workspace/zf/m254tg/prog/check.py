"""Check the m254tg program layer (L2) from scratch.

1. The frozen machine/m254tg_wade.tm has the recorded sha256.
2. The TM layer's frozen ../tm/coq/DagTG.v (imported as M254TGT.DagTG) has exactly the node table of
   the DAG regenerated from the machine (tools/gen_coq.py); regenerating the GENERATED regions of
   ProgLibTG.v (tools/gen_prog.py) leaves the file byte-identical.
3. Reject Admitted / admit / Axiom / Parameter in coq/*.v.
4. Rebuild coq/ from clean (Idle priority) and require every Print Assumptions to be closed.

Usage: python -I check.py"""
import hashlib, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
COQ = HERE / 'coq'
TM = HERE.parent / 'machine' / 'm254tg_wade.tm'
TM_SHA = '1b89758c51ed6eaec9c4581e447c5d74fe2b077270d8c555a1b2d94422c1e520'
GEN = ['ProgLibTG.v']

if hashlib.sha256(TM.read_bytes()).hexdigest() != TM_SHA:
    sys.exit('FAIL: m254tg_wade.tm is not the frozen machine')
print('frozen machine sha256 ok')

old = {f: (COQ / f).read_bytes() for f in GEN}
r = subprocess.run([sys.executable, '-I', str(HERE / 'tools' / 'gen_coq.py')], capture_output=True, text=True)
if r.returncode:
    sys.exit('FAIL: ' + r.stdout + r.stderr)
subprocess.run([sys.executable, '-I', str(HERE / 'tools' / 'gen_prog.py')], check=True, capture_output=True)
for f in GEN:
    if (COQ / f).read_bytes() != old[f]:
        (COQ / f).write_bytes(old[f])
        sys.exit(f'FAIL: regenerated {f} differs from the checked-in file')
print('DagTG matches the machine; generated regions reproduce')

bad = [f'{v.name}:{i + 1}' for v in COQ.glob('*.v')
       for i, l in enumerate(re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S).splitlines())
       if re.search(r'\b(Admitted|admit|Axiom|Parameter)\b', l)]
if bad:
    sys.exit('FAIL: ' + ', '.join(bad))
print('no Admitted / axioms in the sources')

for p in COQ.iterdir():
    if p.suffix in ('.vo', '.vok', '.vos', '.glob'):   # own files only; M254TGT/M254TGL/M254L are built by their owners
        p.unlink()
r = subprocess.run([sys.executable, str(COQ / 'build.py'), 'MainTG.v'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
print(r.stdout)
if r.returncode:
    sys.exit('FAIL: build\n' + r.stderr)
lines = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith('compiled ')]
if not lines or any(l.strip() != 'Closed under the global context' for l in lines):
    sys.exit('FAIL: some Print Assumptions output is not closed')
print('CHECK PASS: progtg closed under the global context')
