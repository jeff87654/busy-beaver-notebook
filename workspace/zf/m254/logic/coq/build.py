"""Build zf/m254/logic/coq with coqc 8.20 at Idle priority (one coqc at a time).

Usage: python build.py [File.v ...]   (default: every *.v here, in dependency order)
Namespaces: M254L = this directory; M254S = ../../settheory (built by its own build.py);
ZF = zf/stdzf/coq; Undecidability = zf/stdzf/vendor/theories (same flags as settheory)."""
import ctypes, re, subprocess, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE

HERE = Path(__file__).resolve().parent
ZF = HERE.parent.parent.parent
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(ZF / 'stdzf' / 'vendor' / 'theories'), 'Undecidability',
         '-Q', str(ZF / 'stdzf' / 'coq'), 'ZF',
         '-Q', str(ZF / 'regcon'), 'RegCon',
         '-Q', str((ZF / '..' / 'third_party' / 'busycoq' / 'verify').resolve()), 'BusyCoq',
         '-Q', str(ZF / 'zfc'), 'ZFC',
         '-Q', str(ZF / 'm254' / 'settheory'), 'M254S',
         '-Q', str(HERE), 'M254L',
         '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
REQ = re.compile(r'From\s+M254L\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')


def deps(v):
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    return [HERE / f'{n}.v' for names in REQ.findall(text) for n in names.split() if (HERE / f'{n}.v').exists()]


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
        r = subprocess.run([COQC, *FLAGS, str(v)], cwd=v.parent, capture_output=True, text=True,
                           creationflags=0x40)
        if r.returncode:
            sys.stderr.write(f'FAILED {v.name}\n{r.stdout}{r.stderr}\n')
            raise SystemExit(1)
        print(f'compiled {v.name} in {time.time() - t:.1f}s', flush=True)
        if r.stdout.strip():
            print(r.stdout)
    done[v] = vo.stat().st_mtime
    return done[v]


if __name__ == '__main__':
    targets = [HERE / a for a in sys.argv[1:]] or sorted(HERE.glob('*.v'))
    done = {}
    for t in targets:
        build(t.resolve(), done)
