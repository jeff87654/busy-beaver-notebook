"""Mechanical check of the pagb TM layer (zf/pagb/tm): halts tm c0 <-> rm_halts dagpa ([], regs0).

  python -I check_tm.py          (from any directory)

0. machine/pa_wade.tm is the frozen file (sha256 ed795af79b6752d72c037d7e32eca1d23efaa6a6c0f0d07fc7ba89869f2616a6).
1. Re-parses machine/pa_wade.tm independently and checks that coq/TablePA.v's literal table
   [pa_table] is exactly its transition table (every row, no extras), start state 0.boot.A.
   (ZFTM.tm_table proves the Coq machine [tm] equals [pa_table]; this closes the loop to the file.)
2. tools/gen_coq.py reproduces DagPA.v, TablePA.v, NamesPA.v byte for byte.
3. No Admitted / admit / Axiom / Parameter in coq/*.v.
4. Clean rebuild of coq/MainTM.v (Idle priority, one coqc at a time).
5. The statements of tmpa_rm and tm_table are the expected ones (printed by coqc from the .vo files)
   and Print Assumptions reports both closed.
"""
from __future__ import annotations
import ctypes, hashlib, re, subprocess, sys
from pathlib import Path

if sys.platform == 'win32':
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
HERE = Path(__file__).resolve().parent
COQ = HERE / 'coq'
TM = HERE / '..' / 'machine' / 'pa_wade.tm'
COQC = Path(r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe')
BUSY = (HERE / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(COQ), 'PAGBT']
GENERATED = ['DagPA.v', 'TablePA.v', 'NamesPA.v']
FROZEN_SHA256 = 'ed795af79b6752d72c037d7e32eca1d23efaa6a6c0f0d07fc7ba89869f2616a6'
NOWIN = 0x08000000 | 0x40 if sys.platform == 'win32' else 0  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS
EXPECTED = {
    'tmpa_rm': 'halts tm c0 <-> rm_halts dagpa ([], regs0)',
    'tm_table': '(forall (q : state) (b : bool), table_lookup pa_table (name q) b = row_of (tm (q, b))) /\\ '
                '(forall (s : string) (b w mv : bool) (nx : string), In (s, b, w, mv, nx) pa_table -> '
                'exists q : state, name q = s) /\\ NoDup (map name all_states) /\\ NoDup (map row_key pa_table) /\\ '
                'name q0 = "0.boot.A" /\\ s0 = false /\\ Datatypes.length all_states = 450 /\\ Datatypes.length pa_table = 897',
}


def fail(msg):
    print('CHECK FAIL:', msg)
    sys.exit(1)


def parse_tm(path: Path):
    start, rows = None, {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.startswith('#!'):
            p = line[2:].split()
            if p and p[0] == 'start':
                start = p[1]
        elif line and not line.startswith('#'):
            s, r, w, d, n = line.split()
            assert r in '01' and w in '01' and d in 'LR', line
            assert (s, r) not in rows, f'duplicate row {line}'
            rows[(s, r)] = (w, d, n)
    return start, rows


def parse_coq_table(path: Path):
    text = path.read_text(encoding='utf-8')
    m = re.search(r'Definition pa_table[^\[]*\[(.*?)\]\.', text, re.S)
    rows = {}
    for s, r, w, d, n in re.findall(r'\("([^"]+)",\s*(true|false),\s*(true|false),\s*(true|false),\s*"([^"]+)"\)', m.group(1)):
        key = (s, '1' if r == 'true' else '0')
        assert key not in rows
        rows[key] = ('1' if w == 'true' else '0', 'R' if d == 'true' else 'L', n)
    return rows


def main():
    # 0. frozen machine file
    sha = hashlib.sha256(TM.read_bytes()).hexdigest()
    if sha != FROZEN_SHA256:
        fail(f'{TM.name} sha256 {sha} != frozen {FROZEN_SHA256}')
    print(f'{TM.name}: sha256 {sha} (frozen, OK)')

    # 1. literal table
    start, rows = parse_tm(TM)
    if start != '0.boot.A':
        fail(f'start state {start}')
    if rows != parse_coq_table(COQ / 'TablePA.v'):
        fail('coq/TablePA.v pa_table differs from pa_wade.tm')
    states = {s for s, _ in rows} | {n for _, _, n in rows.values()}
    print(f'{TM.name} (sha256 {hashlib.sha256(TM.read_bytes()).hexdigest()[:16]}): {len(rows)} transitions, '
          f'{len(states)} states incl. halt ({len(states) - 1} without); literal table matches TablePA.v')

    # 2. generators reproduce
    before = {f: (COQ / f).read_bytes() for f in GENERATED}
    r = subprocess.run([sys.executable, '-I', str(HERE / 'tools' / 'gen_coq.py')], capture_output=True, text=True, creationflags=NOWIN)
    if r.returncode:
        fail(r.stdout + r.stderr)
    for f in GENERATED:
        if (COQ / f).read_bytes() != before[f]:
            fail(f'tools/gen_coq.py does not reproduce {f}')
    print('generated files reproduce:', ', '.join(GENERATED))

    # 3. no admitted proofs or axioms
    bad = re.compile(r'\b(Admitted|admit|Axiom|Axioms|Parameter|Parameters|Conjecture)\b')
    for v in sorted(COQ.glob('*.v')):
        text = re.sub(r'\(\*.*?\*\)', '', v.read_text(encoding='utf-8'), flags=re.S)
        if bad.search(text):
            fail(f'{v.name} contains {bad.search(text).group(0)}')
    print('no Admitted/Axiom/Parameter in coq/*.v')

    # 4. clean rebuild
    for f in list(COQ.glob('*.vo')) + list(COQ.glob('*.vok')) + list(COQ.glob('*.vos')) + list(COQ.glob('*.glob')):
        f.unlink()
    r = subprocess.run([sys.executable, '-I', str(COQ / 'build.py'), 'MainTM.v'], cwd=COQ, capture_output=True, text=True, creationflags=NOWIN)
    print(r.stdout[-2000:], r.stderr[-2000:])
    if r.returncode:
        fail('build failed')

    # 5. statements and assumptions
    probe = COQ / 'Probe_check.v'
    probe.write_text('From Coq Require Import Lists.List Strings.String.\nFrom BusyCoq Require Import TM.\n'
                     'From PAGBT Require Import RM DagPA TablePA ZFTM MainTM.\nImport ListNotations.\n'
                     'Open Scope string_scope.\nSet Printing Width 10000.\n'
                     'Check tmpa_rm.\nCheck tm_table.\nPrint Assumptions tmpa_rm.\nPrint Assumptions tm_table.\n',
                     encoding='utf-8')
    r = subprocess.run([str(COQC), *FLAGS, str(probe)], cwd=COQ, capture_output=True, text=True, creationflags=NOWIN)
    out = r.stdout + r.stderr
    for f in [probe] + [probe.with_suffix(s) for s in ('.vo', '.vok', '.vos', '.glob')]:
        f.unlink(missing_ok=True)
    if r.returncode:
        fail(out)
    flat = ' '.join(out.split())
    for name, stmt in EXPECTED.items():
        if f'{name} : {stmt}' not in flat:
            fail(f'unexpected statement of {name}:\n{out}')
        print(f'{name} : {stmt}')
    if flat.count('Closed under the global context') != 2:
        fail(f'assumptions not closed:\n{out}')
    print('Print Assumptions tmpa_rm / tm_table: Closed under the global context')
    print('CHECK PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
