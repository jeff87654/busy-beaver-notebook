"""Check the m254tg logic layer: clean-build zf/m254tg/logic/coq (Idle, one coqc at a time), verify the
frozen interface hashes and that every Print Assumptions is closed.  Prints CHECK PASS or CHECK FAIL.

Usage: python check.py [--no-clean]"""
import hashlib, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
COQ = HERE / 'coq'
FROZEN = {'EnumTG.v': '794a6ce142467e9497cda8c95cd198a1168c96e320aef95d0114c3cfb3f665e4'}
TOPS = ['L1_TG.v', 'SoundTG.v', 'Comp_BundleTG.v', 'BridgeTG.v', 'Logic_GU_TG.v']

def main():
    ok = True
    for f, h in FROZEN.items():
        got = hashlib.sha256((COQ / f).read_bytes()).hexdigest()
        if got != h:
            print(f'FROZEN FILE CHANGED: {f} {got}'); ok = False
    for f in COQ.glob('*.v'):
        txt = f.read_text(encoding='utf-8')
        for bad in ('Admitted', 'admit.', 'Axiom ', 'Parameter ', 'Conjecture'):
            if bad in txt:
                print(f'{f.name}: contains {bad!r}'); ok = False
    if '--no-clean' not in sys.argv:
        for p in COQ.iterdir():
            if p.suffix in ('.vo', '.vos', '.vok', '.glob') or (p.name.startswith('.') and p.suffix == '.aux'):
                p.unlink()
    r = subprocess.run([sys.executable, str(COQ / 'build.py'), *TOPS], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    print(r.stdout, r.stderr)
    if r.returncode:
        ok = False
    n = r.stdout.count('Closed under the global context')
    lines = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith('compiled ')]
    if n < 6 or any('Closed under the global context' not in l for l in lines):
        print('unexpected assumptions output'); ok = False
    print('CHECK PASS' if ok else 'CHECK FAIL')
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main())
