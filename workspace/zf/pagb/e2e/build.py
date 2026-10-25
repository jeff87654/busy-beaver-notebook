"""Compile zf/pagb/e2e/Headline.v (Idle priority).  The layers must already be built by their own scripts
(coq/build.py, tm/coq/build.py, prog/coq/build.py).
Roots: PAGBE = . (this file: PAGBE.Headline), Undecidability = ../vendor/theories, PAGB = ../coq, PAGBT = ../tm/coq, PAGBP = ../prog/coq, BusyCoq."""
import ctypes, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
HERE = Path(__file__).resolve().parent
M = HERE.parent
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(M / 'vendor' / 'theories'), 'Undecidability',
         '-Q', str((M / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()), 'BusyCoq',
         '-Q', str(M / 'coq'), 'PAGB',
         '-Q', str(M / 'tm' / 'coq'), 'PAGBT',
         '-Q', str(M / 'prog' / 'coq'), 'PAGBP',
         '-Q', str(HERE), 'PAGBE',
         '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
f = sys.argv[1] if len(sys.argv) > 1 else 'Headline.v'
r = subprocess.run([COQC, *FLAGS, f], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace',
                   creationflags=0x08000000 | 0x40)
print(r.stdout); print(r.stderr); sys.exit(r.returncode)
