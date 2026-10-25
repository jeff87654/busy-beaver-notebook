"""Build the pagb program-layer proofs (zf/pagb/prog/coq, logical root PAGBP) with coqc 8.20 at Idle
priority, one coqc at a time.  Usage: python build.py [File.v ...]   (default: every *.v here)

Other roots (read only, compiled by their owners' build scripts):
  M254TGL = ../../logic/coq          (CodesTG.v, EnumTG.v: the frozen abstract enumerator)
  M254L   = ../../../m254/logic/coq   (Codes254.v, re-exported by CodesTG)
  M254TGT = ../../tm/coq             (RM.v, DagTG.v, RMEquiv.v: the TM layer's frozen dagtg, dagtg_wf)"""
import ctypes, re, subprocess, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE

HERE = Path(__file__).resolve().parent
LOGIC = (HERE / '..' / '..' / 'coq').resolve()
VEN = (HERE / '..' / '..' / 'vendor' / 'theories').resolve()
TM = (HERE / '..' / '..' / 'tm' / 'coq').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
ROOTS = {'PAGBP': HERE, 'PAGB': LOGIC, 'PAGBT': TM}
FLAGS = ['-Q', str(VEN), 'Undecidability', '-Q', str(LOGIC), 'PAGB', '-Q', str(TM), 'PAGBT', '-Q', str(HERE), 'PAGBP', '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
REQ = re.compile(r'From\s+(PAGBP|PAGB|PAGBT)\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')


def deps(v):
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    return [ROOTS[r] / f'{n}.v' for r, names in REQ.findall(text) for n in names.split()
            if (ROOTS[r] / f'{n}.v').exists()]


def build(v, done, stack=()):
    if v in done:
        return done[v]
    assert v not in stack, f'dependency cycle at {v}'
    newest = v.stat().st_mtime
    for d in deps(v):
        newest = max(newest, build(d, done, stack + (v,)))
    vo = v.with_suffix('.vo')
    if v.parent != HERE:            # foreign root: must already be compiled by its owner
        if not vo.exists() or vo.stat().st_mtime < newest:
            raise SystemExit(f'{vo} missing or stale: build it with its own build.py')
        done[v] = vo.stat().st_mtime
        return done[v]
    if not vo.exists() or vo.stat().st_mtime < newest:
        t = time.time()
        r = subprocess.run([COQC, *FLAGS, str(v)], cwd=v.parent, capture_output=True, text=True,
                           creationflags=0x08000000 | 0x40)
        if r.returncode:
            sys.stderr.write(f'FAILED {v.name}\n{r.stdout}{r.stderr}\n')
            raise SystemExit(1)
        print(f'compiled {v.name} in {time.time() - t:.1f}s', flush=True)
        if r.stdout.strip():
            print(r.stdout, flush=True)
    done[v] = vo.stat().st_mtime
    return done[v]


if __name__ == '__main__':
    targets = [HERE / a for a in sys.argv[1:]] or sorted(HERE.glob('*.v'))
    done = {}
    for t in targets:
        build(t.resolve(), done)
