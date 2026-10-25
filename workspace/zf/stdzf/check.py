"""Clean rebuild and check of stdzf (Idle priority).  Usage: python check.py
Deletes the compiled files of stdzf/coq, rebuilds everything up to Std_Main.v, rebuilds zf/regcon
(which imports Std_iface), compiles Check.v and requires 6 x 'Closed under the global context' and no
Admitted/Axiom in the sources."""
import ctypes, re, subprocess, sys, runpy
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
HERE = Path(__file__).resolve().parent
COQ = HERE / 'coq'
REGCON = HERE.parent / 'regcon'
for f in COQ.glob('*'):
    if f.suffix in ('.vo', '.vok', '.vos', '.glob') or f.name.endswith('.aux'):
        f.unlink()
bad = [f.name for f in COQ.glob('*.v') if re.search(r'\b(Admitted|admit|Axiom|Parameter)\b', re.sub(r'\(\*.*?\*\)', '', f.read_text(encoding='utf-8'), flags=re.S))]
if bad:
    print('Admitted/Axiom found in', bad); print('CHECK FAIL'); sys.exit(1)
def build(*files):
    r = subprocess.run([sys.executable, str(COQ / 'build.py'), *files], cwd=HERE)
    if r.returncode: print('CHECK FAIL'); sys.exit(1)
build('Std_glue.v', 'Std_ZFeq.v', 'Std_brzf.v', 'Std_brax.v', 'Std_brpow.v', 'Haiku_pow.v')
r = subprocess.run([sys.executable, 'build.py', 'Rel.v', 'WF.v', 'Main.v', 'MinZF.v', 'Link.v'], cwd=REGCON)
if r.returncode: print('regcon build failed'); print('CHECK FAIL'); sys.exit(1)
build('Std_Main.v')
coqc = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
flags = ['-Q', str(COQ), 'ZF', '-Q', str(HERE / 'vendor' / 'theories'), 'Undecidability', '-Q', str(REGCON), 'RegCon', '-w', 'none']
r = subprocess.run([coqc, *flags, 'Check.v'], cwd=COQ, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout, r.stderr)
ok = r.returncode == 0 and r.stdout.count('Closed under the global context') == 6
print('CHECK', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
