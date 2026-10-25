"""Build the m254 program-layer proofs (zf/m254/prog/coq, logical root M254P) with coqc 8.20 at Idle
priority, one coqc at a time.  Usage: python build.py [File.v ...]   (default: every *.v here)

Other roots (read only, compiled by their owners' build scripts):
  M254L = ../../logic/coq  (Codes254.v, Enum254.v: the frozen abstract enumerator)
  M254  = ../../tm/coq     (RM.v, RMEquiv.v, Prog254.v: the frozen p254, R0, p254_wf)"""
import ctypes, re, subprocess, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE

HERE = Path(__file__).resolve().parent
LOGIC = (HERE / '..' / '..' / 'logic' / 'coq').resolve()
TM = (HERE / '..' / '..' / 'tm' / 'coq').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
ROOTS = {'M254P': HERE, 'M254L': LOGIC, 'M254': TM}
FLAGS = ['-Q', str(LOGIC), 'M254L', '-Q', str(TM), 'M254', '-Q', str(HERE), 'M254P']
REQ = re.compile(r'From\s+(M254P|M254L|M254)\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')


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
                           creationflags=0x40)
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
