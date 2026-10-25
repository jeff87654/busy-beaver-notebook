"""Build zf/pagb/coq with coqc 8.20 at Idle priority (one coqc at a time).

Usage: python build.py [File.v ...]   (default: the vendored library subset, then every *.v here)
Namespaces: Undecidability = vendor/theories (unmodified library subset, see vendor/README.md);
PAGB = this directory.  Stale files (older than a dependency) are recompiled."""
import ctypes, re, subprocess, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE

HERE = Path(__file__).resolve().parent
VEN = HERE.parent / 'vendor' / 'theories'
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
WARN = ['-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,'
              '-closed-notation-not-level-0,-deprecated']
VFLAGS = ['-Q', str(VEN), 'Undecidability', *WARN, '-set', 'Default Proof Using = Type']
FLAGS = ['-Q', str(VEN), 'Undecidability', '-Q', str(HERE), 'PAGB', *WARN]
REQ = re.compile(r'From\s+PAGB\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')


def compile_(v, flags):
    t = time.time()
    r = subprocess.run([COQC, *flags, str(v)], cwd=v.parent, capture_output=True, text=True,
                       creationflags=0x08000000 | 0x40)
    if r.returncode:
        sys.stderr.write(f'FAILED {v.name}\n{r.stdout}{r.stderr}\n')
        raise SystemExit(1)
    print(f'compiled {v.name} in {time.time() - t:.1f}s', flush=True)
    if r.stdout.strip():
        print(r.stdout, flush=True)


def build_vendor():
    newest = 0.0
    for rel in (HERE.parent / 'vendor' / 'ORDER.txt').read_text(encoding='utf-8').split():
        v = VEN / rel
        vo = v.with_suffix('.vo')
        newest = max(newest, v.stat().st_mtime)
        if not vo.exists() or vo.stat().st_mtime < newest:
            compile_(v, VFLAGS)
        newest = max(newest, vo.stat().st_mtime)
    return newest


def deps(v):
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    return [HERE / f'{n}.v' for names in REQ.findall(text) for n in names.split() if (HERE / f'{n}.v').exists()]


def build(v, done, base, stack=()):
    if v in done:
        return done[v]
    assert v not in stack, f'dependency cycle at {v}'
    newest = max(v.stat().st_mtime, base)
    for d in deps(v):
        newest = max(newest, build(d, done, base, stack + (v,)))
    vo = v.with_suffix('.vo')
    if not vo.exists() or vo.stat().st_mtime < newest:
        compile_(v, FLAGS)
    done[v] = vo.stat().st_mtime
    return done[v]


if __name__ == '__main__':
    base = build_vendor()
    targets = [HERE / a for a in sys.argv[1:]] or sorted(HERE.glob('*.v'))
    done = {}
    for t in targets:
        build(t.resolve(), done, base)
