"""Build stdzf proofs (ZF + Undecidability library) with coqc (Windows, no make). Usage: python build.py [File.v ...]  (default: all *.v here)"""
import re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUSY = (HERE / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
UNDEC = (HERE / '..' / 'vendor' / 'theories').resolve()   # vendored subset of ext/undec-8.20 (tools/vendor.py)
REGCON = (HERE / '..' / '..' / 'regcon').resolve()      # zf-regcon's development (read-only; built by its own build.py)
COQC = Path(r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe')
ROOTS = {'BusyCoq': BUSY, 'ZF': HERE}
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(HERE), 'ZF', '-Q', str(UNDEC), 'Undecidability', '-Q', str(REGCON), 'RegCon',
         '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
REQ = re.compile(r'From\s+(BusyCoq|ZF)\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')


def deps(v):
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    out = []
    for r, names in REQ.findall(text):
        for n in names.split():
            f = ROOTS[r] / f'{n}.v'
            if f.exists():
                out.append(f)
    return out


def build(v, done, stack=()):
    if v in done:
        return done[v]
    assert v not in stack, f'dependency cycle at {v}'
    newest = v.stat().st_mtime
    for d in deps(v):
        newest = max(newest, build(d, done, stack + (v,)))
    vo = v.with_suffix('.vo')
    if not vo.exists() or vo.stat().st_mtime < newest:
        t = time.time()
        r = subprocess.run([str(COQC), *FLAGS, str(v)], cwd=v.parent, capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(f'FAILED {v.name}\n{r.stdout}{r.stderr}\n')
            raise SystemExit(1)
        print(f'compiled {v.name} in {time.time() - t:.1f}s', flush=True)
    done[v] = vo.stat().st_mtime
    return done[v]


if __name__ == '__main__':
    targets = [HERE / a for a in sys.argv[1:]] or sorted(HERE.glob('*.v'))
    done = {}
    for t in targets:
        build(t.resolve(), done)
