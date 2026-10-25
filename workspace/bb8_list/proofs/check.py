"""Mechanical review of a busycoq non-halting or halting proof.

  python check.py BB7_16582_1RB1LD.v [more.v ...]

A proof file must contain a header comment `(* machine: <standard TM string> *)`,
a definition `Definition tm : TM := fun '(q, s) => match q, s with ... end.`, and
`Theorem nonhalt : ~ halts tm c0.` (or `Theorem halt : halts tm c0.` for a halting proof). The checker then:
  1. compiles the file (and its dependencies) with coqc;
  2. checks that the transition table of `tm` equals the declared machine string exactly
     (`---` / `1RZ`-style halts must be `None`), and that the state count matches the Individual setup imported;
  3. checks the theorem statement text is exactly `~ halts tm c0` (never halts from the blank tape);
  4. runs `Print Assumptions nonhalt` and requires "Closed under the global context"
     (no Admitted, no axioms).
A human reviewer then only needs to confirm that the declared machine string is the intended machine.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import build

HERE = build.HERE
QS = 'ABCDEFGHIJKLMNOP'


def table_from_coq(text):
    m = re.search(r"Definition\s+tm\s*:\s*TM\s*:=\s*fun\s*'\(q,\s*s\)\s*=>\s*match\s+q,\s*s\s+with(.*?)end\.", text, re.S)
    if not m:
        raise ValueError('no `Definition tm : TM := fun \'(q, s) => match q, s with ... end.` found')
    body = m.group(1)
    table, wildcard_none = {}, False
    # 12+ states: the state L shadows busycoq's direction L, so tables write the direction as TM.L (BB122.v)
    for q, s, rhs in re.findall(r'\|\s*([A-P_])\s*,\s*([01_])\s*=>\s*(None|Some\s*\(\s*[01]\s*,\s*(?:TM\.)?[LR]\s*,\s*[A-P]\s*\))', body):
        if q == '_' and s == '_':
            if rhs != 'None':
                raise ValueError('wildcard case must be None')
            wildcard_none = True
            continue
        if q == '_' or s == '_':
            raise ValueError('partial wildcards are not supported by the checker')
        if rhs == 'None':
            table[(q, int(s))] = '---'
        else:
            w, d, n = re.match(r'Some\s*\(\s*([01])\s*,\s*(?:TM\.)?([LR])\s*,\s*([A-P])\s*\)', rhs).groups()
            table[(q, int(s))] = f'{w}{d}{n}'
    return table, wildcard_none


def declared(text):
    m = re.search(r'\(\*\s*machine:\s*([01LRA-PZ_\-]+)\s*\*\)', text)
    if not m:
        raise ValueError('missing header comment (* machine: <TM string> *)')
    return m.group(1)


def check(path: Path):
    text = path.read_text(encoding='utf-8')
    machine = declared(text)
    rows = machine.split('_')
    n = len(rows)
    setup = re.search(r'From\s+BB8\s+Require\s+(?:Import|Export)\s+Individual(\d+)2\.', text) or \
        re.search(r'From\s+BusyCoq\s+Require\s+(?:Import|Export)\s+Individual(\d+)2\.', text)
    if not setup or int(setup.group(1)) != n:
        raise ValueError(f'machine has {n} states but file does not import Individual{n}2')
    table, wildcard_none = table_from_coq(text)
    for i, row in enumerate(rows):
        q = QS[i]
        for s in (0, 1):
            want = row[3 * s: 3 * s + 3]
            want = '---' if want == '---' or want[2] == 'Z' else want
            got = table.get((q, s), '---' if wildcard_none else None)
            if got != want:
                raise ValueError(f'transition {q}{s}: Coq has {got}, machine string has {want}')
    extra = [k for k in table if QS.index(k[0]) >= n]
    if extra:
        raise ValueError(f'Coq table mentions states beyond the machine: {extra}')
    code = re.sub(r'\(\*.*?\*\)', '', text, flags=re.S)  # ignore comments when locating the theorem
    if re.search(r'Theorem\s+nonhalt\s*:\s*~\s*halts\s+tm\s+c0\s*\.', code):
        kind, thm, stmt = 'nonhalt', 'nonhalt', '~ halts {m}.tm c0'
    elif re.search(r'Theorem\s+halt\s*:\s*halts\s+tm\s+c0\s*\.', code):
        kind, thm, stmt = 'halt', 'halt', 'halts {m}.tm c0'
    else:
        raise ValueError('need exactly `Theorem nonhalt : ~ halts tm c0.` or `Theorem halt : halts tm c0.`')
    build.build(path.resolve(), {})
    mod = path.stem
    # The probe makes Coq itself confirm what the text checks above assumed:
    # the theorem has exactly the stated type, and every transition of the compiled `tm` equals the
    # declared machine string (evaluated by conversion, so comments or look-alike text cannot mislead).
    lines = [f'From BB8 Require Import Individual{n}2.', f'From BB8 Require {mod}.',
             f'Check ({mod}.{thm} : {stmt.format(m=mod)}).']
    for i, row in enumerate(rows):
        q = QS[i]
        for s in (0, 1):
            t = row[3 * s: 3 * s + 3]
            d = f'TM.{t[1]}' if n >= 12 else t[1]   # the state L shadows the direction L from 12 states on
            rhs = 'None' if t == '---' or t[2] == 'Z' else f'Some ({t[0]}, {d}, {t[2]})'
            lines.append(f'Check (eq_refl : {mod}.tm ({q}, {s}) = {rhs}).')
    lines.append(f'Print Assumptions {mod}.{thm}.')
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / 'probe.v'
        probe.write_text('\n'.join(lines) + '\n')
        r = subprocess.run([str(build.COQC), *build.FLAGS, str(probe)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode:
        raise ValueError(f'Coq rejected the statement/table probe:\n{out[-3000:]}')
    if 'Closed under the global context' not in out:
        raise ValueError(f'assumption check failed:\n{out[-3000:]}')
    return machine, kind


def main():
    bad = 0
    for a in sys.argv[1:]:
        p = (HERE / a).resolve()
        try:
            m, kind = check(p)
            verdict = 'never halts' if kind == 'nonhalt' else 'HALTS'
            print(f'PASS {p.name}: {m} {verdict} (machine-checked, no axioms)')
        except (ValueError, SystemExit) as e:
            bad += 1
            print(f'FAIL {p.name}: {e}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
