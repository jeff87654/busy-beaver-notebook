"""Check zf/pagb/coq: clean rebuild of every .v here (the vendored library subset is built as needed),
no Admitted/admit/Axiom/Parameter in our sources, the headline statements are the expected ones,
and every Print Assumptions reports "Closed under the global context".
Usage: python -I zf/pagb/coq/check.py"""
import ctypes, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
HERE = Path(__file__).resolve().parent


def fail(msg):
    print('CHECK FAIL:', msg)
    sys.exit(1)


bad = re.compile(r'\b(Admitted|admit|Axiom|Axioms|Parameter|Parameters|Conjecture|Hypothesis)\b')
srcs = sorted(HERE.glob('*.v'))
for v in srcs:
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    m = bad.search(text)
    # section Hypotheses are discharged at End; they are allowed (Print Assumptions is the real test)
    if m and m.group(0) != 'Hypothesis':
        fail(f'{v.name} contains {m.group(0)}')
print('no Admitted/Axiom/Parameter in', len(srcs), 'files')

for v in srcs:
    for ext in ('.vo', '.vok', '.vos', '.glob'):
        f = v.with_suffix(ext)
        if f.exists():
            f.unlink()
r = subprocess.run([sys.executable, '-I', str(HERE / 'build.py')], cwd=HERE, capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
out = r.stdout + r.stderr
print('\n'.join(l for l in out.splitlines() if l.startswith('compiled') or 'Closed' in l or 'Axioms' in l
                or 'FAILED' in l or 'Error' in l))
if r.returncode:
    fail('build failed')

spec = (HERE / 'Spec.v').read_text(encoding='utf-8')
comp = (HERE / 'PA_Comp.v').read_text(encoding='utf-8')
logic = (HERE / 'PA_Logic.v').read_text(encoding='utf-8')
for stmt, text in [
    ('Definition PA_proves_GC : Prop := @tprv _ _ falsity_on class PAeq GC_form.', spec),
    ('Theorem GC_adequate rho : rho ⊨ GC_form <-> Goldbach_nat.', spec),
    ('Theorem PA_GC_refutation : PA_proves_GC <-> PA_NG_inconsistent.', spec),
    ('Theorem pprov_NG_iff_PA_GC : pprov (eq NGw) Fw <-> PA_proves_GC.', comp),
    ('Theorem enum_halts_iff_PA_GC : enum_halts <-> PA_proves_GC.', logic)]:
    if stmt not in text:
        fail('missing statement: ' + stmt)
n = out.count('Print Assumptions')  # not printed; count the results instead
closed = out.count('Closed under the global context')
expected = sum(t.read_text(encoding='utf-8').count('Print Assumptions') for t in srcs)
if closed != expected or 'Axioms:' in out:
    fail(f'{closed} closed assumption reports, expected {expected}')
print(f'CHECK PASS: {len(srcs)} files, {closed} Print Assumptions all closed')
