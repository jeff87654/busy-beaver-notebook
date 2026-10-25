"""Build and check zf/regcon with coqc 8.20 at Idle priority, sequentially.
Usage: python build.py [File.v ...]   (default: all files, then check Print Assumptions)"""
import ctypes, subprocess, sys, time
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
HERE = Path(__file__).resolve().parent
UNDEC = HERE.parent / 'vendor' / 'theories'   # zf/axtext copy of zf/stdzf/vendor
STDZF = HERE.parent / 'coq' / 'R3'                       # zf-axtext R3s development (logical path ZF)
FLAGS = ['-Q', str(UNDEC), 'Undecidability', '-Q', str(HERE), 'RegCon', '-Q', str(STDZF), 'ZF',
         '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
ORDER = ['Rel.v', 'WF.v', 'Main.v', 'MinZF.v', 'Link.v', 'MainR3s.v']
files = sys.argv[1:] or ORDER
out = ''
for f in files:
    t = time.time()
    r = subprocess.run([COQC, *FLAGS, f], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = r.stdout + r.stderr
    if f != 'Check.v' or r.returncode:
        print(out[-6000:])
    if r.returncode:
        print('FAILED', f); sys.exit(1)
    print(f'{time.time()-t:6.1f}s {f}', flush=True)
