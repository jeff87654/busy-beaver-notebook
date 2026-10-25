"""Debug helper.  python tools/dbg.py prep MARKER : compile coq/Prog.v up to MARKER as coq/Tpre.vo.
python tools/dbg.py [TIMEOUT] < extra.v : compile 'Require Import Tpre.' + stdin as Tdbg.v, print tail."""
import subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent.parent / 'coq'
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
HDR = ('From Coq Require Import Lists.List Arith.Arith Lia Bool.Bool.\n'
       'From ZF Require Import RM ZF2Dag Logic Enum Tpre.\nImport ListNotations.\n')
if sys.argv[1] == 'prep':
    src = (here / 'ProgLib.v').read_text(encoding='utf-8')
    (here / 'Tpre.v').write_text(src[:src.index(sys.argv[2])], encoding='utf-8')
    r = subprocess.run([COQC, '-Q', str(here), 'ZF', 'Tpre.v'], cwd=here, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-3000:], 'rc', r.returncode)
    sys.exit()
T = int(sys.argv[1]) if len(sys.argv) > 1 else 600
(here / 'Tdbg.v').write_text(HDR + sys.stdin.read(), encoding='utf-8')
try:
    r = subprocess.run([COQC, '-Q', str(here), 'ZF', 'Tdbg.v'], cwd=here, capture_output=True, text=True, timeout=T)
    out = r.stdout + r.stderr
except subprocess.TimeoutExpired as e:
    o = e.stdout or ''
    out = (o if isinstance(o, str) else o.decode(errors='replace')) + ' TIMEOUT'
print(out[-6000:])
for f in here.glob('Tdbg.*'): f.unlink()
