"""Mechanical review of the ZF-machine verification.

  python check_zf.py            (run from zf/)

1. Re-parses A361.tm independently and checks that coq/ZF2Dag.v's literal
   table `zf2_table` is exactly that transition table (every row, no extras) and that the start state is
   0.boot.A.  (The Coq development proves `tm` equals `zf2_table`; this script closes the loop to the file.)
2. Builds coq/Main.v (and dependencies) with coqc 8.20.
3. Checks the final theorem statement text and that `Print Assumptions` reports a closed proof.
A human reviewer then only needs to read coq/Logic.v (the formal system) and the theorem statement.
"""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TM = HERE / 'R3s336.tm'
DAG = HERE / 'coq' / 'ZF2Dag.v'
MAIN = HERE / 'coq' / 'Main.v'
COQC = Path(r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe')
BUSY = (HERE / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(HERE / 'coq'), 'ZF']
EXPECTED_THM = 'halts tm c0 <-> prov (Wel v0 v0)'


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
    m = re.search(r'Definition zf2_table[^\[]*\[(.*?)\]\.', text, re.S)
    rows = {}
    for s, r, w, d, n in re.findall(r'\("([^"]+)",\s*(true|false),\s*(true|false),\s*(true|false),\s*"([^"]+)"\)', m.group(1)):
        key = (s, '1' if r == 'true' else '0')
        assert key not in rows
        rows[key] = ('1' if w == 'true' else '0', 'R' if d == 'true' else 'L', n)
    return rows


def main():
    start, rows = parse_tm(TM)
    assert start == '0.boot.A', start
    coq_rows = parse_coq_table(DAG)
    assert rows == coq_rows, 'coq/ZF2Dag.v zf2_table differs from zf2.tm'
    states = {s for s, _ in rows} | {n for _, _, n in rows.values()}
    print(f'{TM.name}: {len(rows)} transitions, {len(states)} states (incl. halt); literal table matches')
    if not MAIN.exists():
        print('coq/Main.v not present yet: build step skipped')
        return 1
    sys.path.insert(0, str(HERE / 'coq'))
    import build
    build.build(MAIN, {})
    text = MAIN.read_text(encoding='utf-8')
    m = re.search(r'Theorem\s+zf_machine\s*:\s*(.*?)\.\s*\n', text, re.S)
    assert m, 'Theorem zf_machine not found in Main.v'
    stmt = ' '.join(m.group(1).split())
    assert stmt == EXPECTED_THM, f'unexpected statement: {stmt!r}'
    probe = HERE / 'coq' / 'Probe_assumptions.v'
    probe.write_text('From ZF Require Import Main.\nPrint Assumptions zf_machine.\n', encoding='utf-8')
    r = subprocess.run([str(COQC), *FLAGS, str(probe)], cwd=probe.parent, capture_output=True, text=True)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out
    assert 'Closed under the global context' in out, out
    print('Theorem zf_machine :', stmt)
    print('Print Assumptions: Closed under the global context')
    print('CHECK PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
