"""Build zf/m254tg/ac with coqc 8.20 at Idle priority.

Usage: python build.py [File.v ...]   (default: every target in ORDER, then Check.v -> CHECK PASS)

Dependencies (From ZFC Require ...) are rebuilt when out of date.  At most FOUR coqc processes run
machine-wide among all users of this script: each compile first takes one of the slot locks in
.locks/ (msvcrt byte lock, released automatically if the holder dies)."""
import ctypes, msvcrt, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
HERE = Path(__file__).resolve().parent
ZF = HERE.parent.parent
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(ZF / 'stdzf' / 'vendor' / 'theories'), 'Undecidability',
         '-Q', str(ZF / 'stdzf' / 'coq'), 'ZF',
         '-Q', str(ZF / 'regcon'), 'RegCon',
         '-Q', str((ZF / '..' / 'third_party' / 'busycoq' / 'verify').resolve()), 'BusyCoq',
         '-Q', str(ZF / 'zfc'), 'ZFC',
         '-Q', str(ZF / 'm254' / 'settheory'), 'M254S',
         '-Q', str(HERE.parent / 'settheory'), 'M254TG',
         '-Q', str(HERE), 'M254TGA',
         '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
REQ = re.compile(r'From\s+M254TGA\s+Require\s+(?:Import\s+|Export\s+)?([\w\s.]+?)\.(?:\s|$)')
NSLOTS = 4


def acquire():
    (HERE / '.locks').mkdir(exist_ok=True)
    while True:
        for i in range(NSLOTS):
            fd = os.open(str(HERE / '.locks' / f'slot{i}'), os.O_RDWR | os.O_CREAT)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                return fd
            except OSError:
                os.close(fd)
        time.sleep(2)


def release(fd):
    os.lseek(fd, 0, 0)
    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    os.close(fd)


def deps(v):
    text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
    out = []
    for names in REQ.findall(text):
        for n in names.split():
            f = HERE / f'{n}.v'
            if f.exists():
                out.append(f)
    return out


def build(v, done, force=False, stack=()):
    if v in done:
        return done[v]
    assert v not in stack, f'dependency cycle at {v}'
    newest = v.stat().st_mtime
    for d in deps(v):
        newest = max(newest, build(d, done, False, stack + (v,)))
    vo = v.with_suffix('.vo')
    out = ''
    stale = lambda: force or not vo.exists() or vo.stat().st_mtime < max(newest, v.stat().st_mtime)
    if stale():
        lfd = os.open(str(HERE / '.locks' / f'{v.stem}.lock'), os.O_RDWR | os.O_CREAT)
        while True:  # one compile of a given file at a time
            try:
                msvcrt.locking(lfd, msvcrt.LK_NBLCK, 1); break
            except OSError:
                time.sleep(1)
        try:
            if stale():
                out = compile_one(v)
        finally:
            os.lseek(lfd, 0, 0); msvcrt.locking(lfd, msvcrt.LK_UNLCK, 1); os.close(lfd)
    done[v] = vo.stat().st_mtime
    done[(v, 'out')] = out
    return done[v]


def compile_one(v):
    if True:
        fd = acquire()
        try:
            t = time.time()
            r = subprocess.run([COQC, *FLAGS, v.name], cwd=HERE, capture_output=True, text=True,
                               encoding='utf-8', errors='replace')
        finally:
            release(fd)
        out = r.stdout + r.stderr
        if r.returncode:
            sys.stdout.write(f'FAILED {v.name}\n{out[-8000:]}\n')
            raise SystemExit(1)
        print(f'compiled {v.name} in {time.time() - t:.1f}s', flush=True)
        if out.strip() and v.name != 'Check.v':
            print(out[-3000:])
        return out


if __name__ == '__main__':
    args = sys.argv[1:]
    done = {}
    if args:
        for a in args:
            build((HERE / a).resolve(), done)
    else:
        chk = (HERE / 'Check.v').resolve()
        build(chk, done, force=True)
        out = done[(chk, 'out')]
        print(out)
        bad = ('Axioms:' in out) or ('admit' in out.lower())
        ok = (not bad) and out.count('Closed under the global context') >= 1
        print('CHECK', 'PASS' if ok else 'FAIL')
        sys.exit(0 if ok else 1)
