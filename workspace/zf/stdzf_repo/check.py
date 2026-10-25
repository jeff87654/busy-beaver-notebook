#!/usr/bin/env python3
"""Build and check the stdzf development from sources (portable: Linux / macOS / Windows).

    python3 check.py            # coqc from $COQC, default `coqc` on PATH (Coq 8.20.x)

1. Refuses any of our sources (coq/, regcon/, endtoend/) containing Admitted / admit / Axiom /
   Parameter outside comments (vendored code is covered by Print Assumptions).
2. Checks that each machine's literal transition table zf2_table (endtoend/<n>/ZF2Dag.v) is exactly
   the table of endtoend/machines/<machine>.tm.
3. Compiles, in dependency order, the closure of coq/Check.v (load paths
   vendor/undecidability/theories -> Undecidability, coq -> ZF, regcon -> RegCon) and then, for each
   machine n, of endtoend/<n>/E2E<n>.v (coq and endtoend/<n> -> ZF, vendor/busycoq -> BusyCoq).
4. Requires "Closed under the global context" 6 times in Check.v and 4 times in each E2E<n>.v.
   Prints CHECK PASS / CHECK FAIL.
"""
import os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
COQC = os.environ.get('COQC', 'coqc')
UNDEC = HERE / 'vendor' / 'undecidability' / 'theories'
COMMON = {'Undecidability': [UNDEC], 'RegCon': [HERE / 'regcon'], 'BusyCoq': [HERE / 'vendor' / 'busycoq']}
MACHINES = {'354': 'B354.tm'}
# (name, extra load paths, top file, expected number of closed Print Assumptions)
CONFIGS = [('stdzf', {'ZF': [HERE / 'coq']}, HERE / 'coq' / 'Check.v', 6)] + [
    (n, {'ZF': [HERE / 'coq', HERE / 'endtoend' / n]}, HERE / 'endtoend' / n / f'E2E{n}.v', 4)
    for n in MACHINES]
OWN = [HERE / 'coq', HERE / 'regcon', HERE / 'endtoend']      # sources scanned for Admitted/Axiom
WARN = ['-w', '-notation-overridden,-stdlib-vector,-notation-incompatible-prefix,'
              '-postfix-notation-not-level-1,-closed-notation-not-level-0,-deprecated']
LIBFLAGS = ['-set', 'Default Proof Using = Type']     # as in the library's _CoqProject

if os.name == 'nt':                                   # run at Idle priority on Windows
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)


def strip_comments(text):
    out, depth, i = [], 0, 0
    while i < len(text):
        if text.startswith('(*', i):
            depth += 1; i += 2
        elif text.startswith('*)', i) and depth:
            depth -= 1; i += 2
        else:
            if not depth:
                out.append(text[i])
            i += 1
    return ''.join(out)


REQ = re.compile(r'(?:From\s+([\w.]+)\s+)?Require\s+(?:Import\s+|Export\s+)?(.*?)\.(?:\s|$)', re.S)


def resolve(roots, prefix, name):
    """Map a (From prefix, module name) pair to a source file below our load paths, or None (stdlib)."""
    full = f'{prefix}.{name}' if prefix else name
    parts = full.split('.')
    if parts[0] not in roots:
        return None
    for root in roots[parts[0]]:
        f = root.joinpath(*parts[1:]).with_suffix('.v')
        if f.exists():
            return f
    # partially qualified name: a suffix of a module path below the prefix directory
    tail = '/' + '/'.join(name.split('.'))
    for root in roots[parts[0]]:
        base = root.joinpath(*prefix.split('.')[1:]) if prefix else root
        cands = sorted(p for p in base.rglob(name.split('.')[-1] + '.v')
                       if p.with_suffix('').as_posix().endswith(tail))
        if cands:
            return cands[0]
    raise SystemExit(f'cannot resolve {full}')


def deps(roots, f):
    out = []
    for prefix, names in REQ.findall(strip_comments(f.read_text(encoding='utf-8'))):
        if prefix and prefix.split('.')[0] not in roots:
            continue
        for n in names.split():
            if not prefix and n.split('.')[0] not in roots:
                continue
            r = resolve(roots, prefix, n)
            if r is not None:
                out.append(r)
    return out


def closure(roots, top):
    order, seen = [], set()
    def visit(f, stack):
        if f in seen:
            return
        if f in stack:
            raise SystemExit(f'dependency cycle at {f}')
        for d in deps(roots, f):
            visit(d, stack | {f})
        seen.add(f)
        order.append(f)
    visit(top, frozenset())
    return order


def parse_tm(path):
    start, rows = None, {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.startswith('#!'):
            p = line[2:].split()
            if p and p[0] == 'start':
                start = p[1]
        elif line and not line.startswith('#'):
            q, r, w, d, n = line.split()
            assert r in '01' and w in '01' and d in 'LR', line
            assert (q, r) not in rows, f'duplicate row {line}'
            rows[(q, r)] = (w, d, n)
    return start, rows


def parse_coq_table(path):
    m = re.search(r'Definition zf2_table[^\[]*\[(.*?)\]\.', path.read_text(encoding='utf-8'), re.S)
    rows = {}
    for q, r, w, d, n in re.findall(
            r'\("([^"]+)",\s*(true|false),\s*(true|false),\s*(true|false),\s*"([^"]+)"\)', m.group(1)):
        key = (q, '1' if r == 'true' else '0')
        assert key not in rows
        rows[key] = ('1' if w == 'true' else '0', 'R' if d == 'true' else 'L', n)
    return rows


def main():
    t0 = time.time()
    bad = [str(f.relative_to(HERE)) for d in OWN for f in d.rglob('*.v')
           if re.search(r'\b(Admitted|admit|Axiom|Parameter)\b', strip_comments(f.read_text(encoding='utf-8')))]
    if bad:
        print('forbidden keyword in:', *bad, sep='\n  ')
        print('CHECK FAIL'); return 1
    for n, tmf in MACHINES.items():
        start, rows = parse_tm(HERE / 'endtoend' / 'machines' / tmf)
        if start != '0.boot.A' or rows != parse_coq_table(HERE / 'endtoend' / n / 'ZF2Dag.v'):
            print(f'endtoend/{n}/ZF2Dag.v: zf2_table differs from {tmf}'); print('CHECK FAIL'); return 1
        states = {q for q, _ in rows} | {x for _, _, x in rows.values()}
        print(f'{tmf}: {len(rows)} transitions, {len(states) - 1} states + halt; literal table = zf2_table')
    done, ok = set(), True
    for name, extra, top, expected in CONFIGS:
        roots = {**COMMON, **extra}
        qflags = [x for p, ds in roots.items() for d in ds for x in ('-Q', str(d.relative_to(HERE)), p)]
        files = closure(roots, top)
        print(f'[{name}] {len(files)} files ({len([f for f in files if f not in done])} new)', flush=True)
        for f in files:
            if f in done:
                continue
            lib = UNDEC in f.parents
            cmd = [COQC, *qflags, *WARN, *(LIBFLAGS if lib else []), str(f.relative_to(HERE))]
            t = time.time()
            r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode:
                print(f'FAILED {f.relative_to(HERE)}\n{r.stdout}{r.stderr}')
                print('CHECK FAIL'); return 1
            done.add(f)
            if f == top:
                print(r.stdout)
                k = r.stdout.count('Closed under the global context')
                print(f'[{name}] {k}/{expected} closed', flush=True)
                ok = ok and k == expected
            else:
                print(f'{time.time() - t:7.1f}s  {f.relative_to(HERE)}', flush=True)
    print(f'total {time.time() - t0:.0f}s')
    print('CHECK', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
