"""Mechanical review of a busycoq HALTING proof (the counterpart of bb8_list/proofs/check.py,
which only accepts `~ halts tm c0`).

  python check_halt.py path\to\File.v [more.v ...]

For each file:
  1. the header comment `(* machine: <TM string> *)` must match the Coq transition table exactly
     (same parser and rules as check.py, imported from bb8_list/proofs);
  2. the file must contain exactly `Theorem halt : halts tm c0.` (halts from the blank tape);
  3. the file is compiled with coqc (logical paths as build.py, plus the file's folder as `Scratch`
     when it is not in bb8_list/proofs);
  4. `Print Assumptions halt` must report "Closed under the global context".
"""
import re, subprocess, sys, tempfile
from pathlib import Path
PROOFS = Path(__file__).resolve().parents[2] / 'proofs'
sys.path.insert(0, str(PROOFS))
import build, check as chk


def check_one(p: Path):
    text = p.read_text(encoding='utf-8')
    machine = chk.declared(text)
    rows = machine.split('_')
    setup = re.search(r'From\s+BB8\s+Require\s+(?:Import|Export)\s+Individual(\d)2', text)
    if not setup or int(setup.group(1)) != len(rows):
        raise ValueError('state count / Individual setup mismatch')
    table, wc = chk.table_from_coq(text)
    for i, row in enumerate(rows):
        for s in (0, 1):
            want = row[3 * s:3 * s + 3]
            want = '---' if want == '---' or want[2] == 'Z' else want
            got = table.get(('ABCDEFGH'[i], s), '---' if wc else None)
            if got != want:
                raise ValueError(f'transition {"ABCDEFGH"[i]}{s}: Coq has {got}, machine string has {want}')
    if not re.search(r'Theorem\s+halt\s*:\s*halts\s+tm\s+c0\s*\.', text):
        raise ValueError('theorem statement must be exactly: Theorem halt : halts tm c0.')
    if p.parent.resolve() == PROOFS.resolve():
        build.build(p.resolve(), {})
        lib = 'BB8'
        flags = build.FLAGS
    else:
        flags = build.FLAGS + ['-Q', str(p.parent.resolve()), 'Scratch']
        r = subprocess.run([str(build.COQC), *flags, str(p)], cwd=p.parent, capture_output=True, text=True)
        if r.returncode:
            raise ValueError('compile failed:\n' + r.stdout[-3000:] + r.stderr[-3000:])
        lib = 'Scratch'
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / 'probe.v'
        probe.write_text(f'From {lib} Require {p.stem}.\nPrint Assumptions {p.stem}.halt.\n')
        r = subprocess.run([str(build.COQC), *flags, str(probe)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode or 'Closed under the global context' not in out:
        raise ValueError('assumption check failed:\n' + out)
    return machine


if __name__ == '__main__':
    bad = 0
    for a in sys.argv[1:]:
        p = Path(a).resolve()
        try:
            m = check_one(p)
            print(f'PASS {p.name}: {m} halts (machine-checked, no axioms)')
        except (ValueError, SystemExit) as e:
            bad += 1
            print(f'FAIL {p.name}: {e}')
    sys.exit(1 if bad else 0)
