"""Build the dependency closure of given files of the Coq undecidability library (coq-8.20 branch)
with coqc 8.20 at Idle priority, sequentially.  Usage: python undecbuild.py ROOT FILE.v ...
(FILE paths relative to ROOT/theories).  Prints the closure and compiles stale files."""
import ctypes, re, subprocess, sys, time
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
ROOT = Path(sys.argv[1]).resolve() / 'theories'
FLAGS = ['-Q', str(ROOT), 'Undecidability', '-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated',
         '-set', 'Default Proof Using = Type']
REQ = re.compile(r'(?:From\s+([\w.]+)\s+)?Require\s+(?:Import\s+|Export\s+)?(.*?)\.(?:\s|$)', re.S)

def strip(t):
    while True:
        u = re.sub(r'\(\*(?:(?!\(\*|\*\)).)*\*\)', '', t, flags=re.S)
        if u == t: return t
        t = u

def resolve(prefix, name):
    full = (prefix + '.' + name) if prefix else name
    parts = full.split('.')
    if parts[0] != 'Undecidability': return None
    f = ROOT.joinpath(*parts[1:]).with_suffix('.v')
    if f.exists(): return f
    # partial qualification: the name is a suffix of a module path below the prefix directory
    base = ROOT.joinpath(*prefix.split('.')[1:]) if prefix else ROOT
    tail = '/' + '/'.join(name.split('.'))
    cands = sorted(p for p in base.rglob(name.split('.')[-1] + '.v') if p.with_suffix('').as_posix().endswith(tail))
    return cands[0] if cands else None

def deps(f):
    t = strip(f.read_text(encoding='utf-8'))
    out = []
    for pre, names in REQ.findall(t):
        for n in names.split():
            if pre and not pre.startswith('Undecidability'): continue
            if not pre and not n.startswith('Undecidability'): continue
            r = resolve(pre, n)
            if r is None: print('UNRESOLVED', f.relative_to(ROOT), pre, n); continue
            out.append(r)
    return out

order, seen = [], set()
def visit(f, stack=()):
    if f in seen: return
    seen.add(f)
    for d in deps(f): visit(d, stack + (f,))
    order.append(f)
for a in sys.argv[2:]: visit((ROOT / a).resolve())
print(len(order), 'files')
for f in order:
    vo = f.with_suffix('.vo')
    newest = max([f.stat().st_mtime] + [d.with_suffix('.vo').stat().st_mtime for d in deps(f) if d.with_suffix('.vo').exists()])
    if vo.exists() and vo.stat().st_mtime >= newest: continue
    t = time.time()
    r = subprocess.run([COQC, *FLAGS, str(f)], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print('FAILED', f.relative_to(ROOT)); print(r.stdout[-3000:], r.stderr[-3000:]); sys.exit(1)
    print(f'{time.time()-t:6.1f}s {f.relative_to(ROOT)}', flush=True)
