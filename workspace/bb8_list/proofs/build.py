"""Build busycoq dependencies and our proofs with coqc (no make needed on Windows).

  python build.py                 # build every .v in this directory
  python build.py Smoke82.v ...   # build specific files (and their dependencies)

Logical paths: busycoq's verify/ is BusyCoq (as upstream), this directory is BB8.
Dependencies are discovered from `From BusyCoq/BB8 Require ...` lines; a file is
recompiled when its .vo is missing or older than the .v or any dependency.
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUSY = (HERE / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = Path(r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe')
ROOTS = {'BusyCoq': BUSY, 'BB8': HERE}
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(HERE), 'BB8']
REQ = re.compile(r'From\s+(BusyCoq|BB8)\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')


def deps(v: Path):
    out = []
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    for root, names in REQ.findall(text):
        for name in names.split():
            f = ROOTS[root] / f'{name}.v'
            if f.exists():
                out.append(f)
    return out


def build(v: Path, done: dict, stack=()):
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
        print(f'compiled {v.relative_to(v.parent.parent)} in {time.time() - t:.1f}s', flush=True)
    done[v] = vo.stat().st_mtime
    return done[v]


def main():
    targets = [HERE / a for a in sys.argv[1:]] or sorted(HERE.glob('*.v'))
    done = {}
    for t in targets:
        build(t.resolve(), done)
    print('ok:', ', '.join(t.name for t in targets))


if __name__ == '__main__':
    main()
