"""Compile zf/m254tg/e2e/E2E_TG.v (Idle priority). The layer directories must already be built by their own scripts.

Roots: M254TGT = ../tm/coq, M254TGP = ../prog/coq, M254TGL = ../logic/coq, M254TG = ../settheory, M254TGA = ../ac,
plus the frozen zf/m254 roots the logic layer reads (M254S, M254L) and the shared libraries."""
import ctypes, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
HERE = Path(__file__).resolve().parent
M = HERE.parent; ZF = M.parent
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(ZF / 'stdzf' / 'vendor' / 'theories'), 'Undecidability',
         '-Q', str(ZF / 'stdzf' / 'coq'), 'ZF',
         '-Q', str(ZF / 'regcon'), 'RegCon',
         '-Q', str((ZF / '..' / 'third_party' / 'busycoq' / 'verify').resolve()), 'BusyCoq',
         '-Q', str(ZF / 'zfc'), 'ZFC',
         '-Q', str(ZF / 'm254' / 'settheory'), 'M254S',
         '-Q', str(ZF / 'm254' / 'logic' / 'coq'), 'M254L',
         '-Q', str(M / 'settheory'), 'M254TG',
         '-Q', str(M / 'ac'), 'M254TGA',
         '-Q', str(M / 'logic' / 'coq'), 'M254TGL',
         '-Q', str(M / 'tm' / 'coq'), 'M254TGT',
         '-Q', str(M / 'prog' / 'coq'), 'M254TGP',
         '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
f = sys.argv[1] if len(sys.argv) > 1 else 'E2E_TG.v'
r = subprocess.run([COQC, *FLAGS, f], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout); print(r.stderr); sys.exit(r.returncode)
