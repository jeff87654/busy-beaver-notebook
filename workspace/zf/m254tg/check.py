"""Top-level check for the ZF + GU machine (zf/m254tg): m254tg_wade.tm (296 states) halts from the blank
tape iff ZF + GU (resp. ZF + Reg + GU, ZF + AC + GU, ZF + Reg + AC + GU) is inconsistent.

Steps:
  1. the frozen machine machine/m254tg_wade.tm has sha256 1b89758c...;
  2. no Admitted / admit / Axiom / Parameter in any m254tg .v file (Print Assumptions is the real test);
  3. remove every compiled file in the m254tg layers, then rebuild layer by layer:
     settheory (build.py -> CHECK PASS), ac (build.py -> CHECK PASS), logic (check.py: frozen EnumTG sha, clean rebuild, closed), tm (check_tm.py: table = .tm file,
     generators reproduce, clean rebuild, closed), prog (check.py: generated files reproduce,
     clean rebuild, closed);
  4. e2e: compile E2E_TG.v; the statements are the expected ones and every Print Assumptions
     reports "Closed under the global context".
The shared dependencies zf/stdzf, zf/regcon, zf/zfc, busycoq and the frozen zf/m254 roots
(M254S, M254L) are used as built (each has its own check: zf/m254/check.py).
Usage: python -I zf/m254tg/check.py"""
import ctypes, hashlib, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
M = Path(__file__).resolve().parent
TM_SHA = '1b89758c51ed6eaec9c4581e447c5d74fe2b077270d8c555a1b2d94422c1e520'
LAYERS = [M / 'settheory', M / 'ac', M / 'logic' / 'coq', M / 'tm' / 'coq', M / 'prog' / 'coq', M / 'e2e']


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


# 1. the frozen machine
if hashlib.sha256((M / 'machine' / 'm254tg_wade.tm').read_bytes()).hexdigest() != TM_SHA:
    fail('machine/m254tg_wade.tm does not have the frozen sha256')
print('machine/m254tg_wade.tm sha256 ok:', TM_SHA)

# 2. no admitted proofs or axioms
bad = re.compile(r'\b(Admitted|admit|Axiom|Axioms|Parameter|Parameters|Conjecture)\b')
for d in LAYERS:
    for v in d.glob('*.v'):
        text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
        if bad.search(text):
            fail(f'{v} contains {bad.search(text).group(0)}')
print('no Admitted/Axiom/Parameter in m254tg sources')

# 3. clean, then the layers in dependency order (logic reads settheory; prog reads tm and logic)
for d in LAYERS:
    for f in list(d.glob('*.vo')) + list(d.glob('*.vok')) + list(d.glob('*.vos')) + list(d.glob('*.glob')):
        f.unlink()
print('removed all compiled files in', ', '.join(str(d.relative_to(M)) for d in LAYERS))
out = run(['build.py'], M / 'settheory')
if 'CHECK PASS' not in out:
    fail('settheory build did not print CHECK PASS')
out = run(['build.py'], M / 'ac')
if 'CHECK PASS' not in out:
    fail('ac build did not print CHECK PASS')
out = run(['-I', M / 'logic' / 'check.py'], M / 'logic')
if 'CHECK PASS' not in out:
    fail('logic check did not print CHECK PASS')
run(['-I', M / 'tm' / 'check_tm.py'], M / 'tm')
out = run(['-I', M / 'prog' / 'check.py'], M / 'prog')
if 'CHECK PASS' not in out:
    fail('prog check did not print CHECK PASS')

# 4. end to end
out = run(['-I', M / 'e2e' / 'build.py'], M / 'e2e')
e2e = (M / 'e2e' / 'E2E_TG.v').read_text(encoding='utf-8')
for stmt in ['halts tm c0 <-> @tprv sig0 zfp fon cls (fun phi => ZF.Std_iface.ZFc phi \/ phi = M254TG.SU_gu.GU) bot.',
             '(fun phi => (ZF.Std_iface.ZFc phi \/ phi = RegCon.MinZF.ax_reg\') \/ phi = M254TG.SU_gu.GU) bot.',
             '(fun phi => (ZF.Std_iface.ZFc phi \/ phi = ZFC.Z_wo.ax_ac) \/ phi = M254TG.SU_gu.GU) bot.',
             '(fun phi => ((ZF.Std_iface.ZFc phi \/ phi = RegCon.MinZF.ax_reg\') \/ phi = ZFC.Z_wo.ax_ac) \/ phi = M254TG.SU_gu.GU) bot.']:
    if stmt not in e2e:
        fail('unexpected statement in E2E_TG.v: ' + stmt)
for name, body in [('tg296_halts_iff_ZFCGU',
                    '(fun phi => (ZF.Std_iface.ZFc phi \\/ phi = ZFC.Z_wo.ax_ac) \\/ phi = M254TG.SU_gu.GU) bot.'),
                   ('tg296_halts_iff_ZFCRGU',
                    '(fun phi => ((ZF.Std_iface.ZFc phi \\/ phi = RegCon.MinZF.ax_reg\') \\/ phi = ZFC.Z_wo.ax_ac) \\/ phi = M254TG.SU_gu.GU) bot.')]:
    m = re.search(r'Theorem ' + name + r' :\s*halts tm c0 <-> @tprv sig0 zfp fon cls\s*(.*?bot\.)', e2e, re.S)
    if not m or m.group(1) != body:
        fail('unexpected statement of ' + name + ' in E2E_TG.v')
if out.count('Closed under the global context') != 4 or 'Axioms:' in out:
    fail('E2E_TG assumptions are not closed')
print('CHECK PASS: m254tg_wade.tm halts iff ZFc + GU (resp. + Reg, + AC, + Reg + AC) proves falsity; no axioms')
