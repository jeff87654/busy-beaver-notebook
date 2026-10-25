"""Top-level check for the zfc_254 formalization (zf/m254).

Steps (each layer's own script does its own clean rebuild where noted):
  1. no Admitted / admit / Axiom / Parameter in any m254 .v file (section Hypotheses are discharged; Print Assumptions is the real test);
  2. settheory: clean rebuild (build.py -> CHECK PASS);
  3. logic: clean rebuild (build.py), Print Assumptions closed;
  4. tm: check_tm254.py (input hashes, Table254.v = zfc_254.tm, generators reproduce, clean rebuild, closed);
  5. prog: check.py (generated files reproduce, clean rebuild, closed);
  6. e2e: clean compile of E2E254.v; the statements are the expected ones and every Print Assumptions
     reports "Closed under the global context".
The shared dependencies zf/stdzf, zf/regcon, zf/zfc and busycoq are used as built (each has its own check).
Usage: python -I zf/m254/check.py"""
import ctypes, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
M = Path(__file__).resolve().parent
LAYERS = [M / 'settheory', M / 'logic' / 'coq', M / 'tm' / 'coq', M / 'prog' / 'coq', M / 'e2e']


def fail(msg):
    print('CHECK FAIL:', msg)
    sys.exit(1)


def run(args, cwd):
    print('>>', ' '.join(map(str, args)), flush=True)
    r = subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    out = r.stdout + r.stderr
    print(out[-3000:], flush=True)
    if r.returncode:
        fail(f'{args} exited with {r.returncode}')
    return out


# 1. no admitted proofs or axioms
bad = re.compile(r'\b(Admitted|admit|Axiom|Axioms|Parameter|Parameters|Conjecture)\b')
for d in LAYERS:
    for v in d.glob('*.v'):
        text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
        if bad.search(text):
            fail(f'{v} contains {bad.search(text).group(0)}')
print('no Admitted/Axiom/Parameter in m254 sources')

# clean
for d in LAYERS:
    for f in list(d.glob('*.vo')) + list(d.glob('*.vok')) + list(d.glob('*.vos')) + list(d.glob('*.glob')):
        f.unlink()
print('removed all compiled files in', ', '.join(str(d.relative_to(M)) for d in LAYERS))

# 2-5. layers
out = run(['build.py'], M / 'settheory')
if 'CHECK PASS' not in out:
    fail('settheory build did not print CHECK PASS')
out = run(['build.py'], M / 'logic' / 'coq')
run(['-I', M / 'tm' / 'check_tm254.py'], M / 'tm')
run(['-I', M / 'prog' / 'check.py'], M / 'prog')

# 6. end to end
out = run(['-I', M / 'e2e' / 'build.py'], M / 'e2e')
e2e = (M / 'e2e' / 'E2E254.v').read_text(encoding='utf-8')
for stmt in ['Theorem zf254_halts_iff_ZF : halts tm c0 <-> @tprv sig0 zfp fon cls ZF.Std_iface.ZFc bot.',
             'halts tm c0 <-> @tprv sig0 zfp fon cls (fun phi => ZF.Std_iface.ZFc phi \\/ phi = ZFC.Z_wo.ax_ac) bot.']:
    if stmt not in e2e:
        fail('unexpected statement in E2E254.v: ' + stmt)
if out.count('Closed under the global context') != 2 or 'Axioms:' in out:
    fail('E2E254 assumptions are not closed')
print('CHECK PASS: zfc_254.tm halts iff ZFc (resp. ZFc + AC) proves falsity; no axioms')
