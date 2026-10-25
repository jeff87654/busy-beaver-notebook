"""Mechanical review of a busycoq HALTING proof kept in this folder's coq/ (logical path Scratch).
Mirrors bb8_list/proofs/check.py (which only accepts `~ halts tm c0`), with the theorem flipped:

  python check_halt.py BB8_76450_1RB0LG_0LC0RH_halt.v

  1. the transition table of `tm` equals the declared `(* machine: ... *)` string exactly;
  2. the file imports Individual82 (8 states);
  3. the theorem statement is exactly `Theorem halt : halts tm c0.`;
  4. the file compiles, and `Print Assumptions halt` reports "Closed under the global context".
"""
import re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'proofs'))
import build, check as chk   # read-only use of the project's checker helpers

HERE = Path(__file__).resolve().parent / 'coq'
FLAGS = build.FLAGS + ['-Q', str(HERE), 'Scratch']

bad = 0
for a in sys.argv[1:]:
    p = (HERE / a).resolve()
    try:
        text = p.read_text(encoding='utf-8')
        machine = chk.declared(text)
        rows = machine.split('_')
        if not re.search(r'From\s+BB8\s+Require\s+(?:Import|Export)\s+Individual%d2' % len(rows), text):
            raise ValueError('wrong Individual setup')
        table, wc = chk.table_from_coq(text)
        for i, row in enumerate(rows):
            for s in (0, 1):
                want = row[3 * s:3 * s + 3]
                want = '---' if want == '---' or want[2] == 'Z' else want
                got = table.get(('ABCDEFGH'[i], s), '---' if wc else None)
                if got != want:
                    raise ValueError('transition %s%d: Coq has %s, machine string has %s' % ('ABCDEFGH'[i], s, got, want))
        if not re.search(r'Theorem\s+halt\s*:\s*halts\s+tm\s+c0\s*\.', text):
            raise ValueError('theorem statement must be exactly: Theorem halt : halts tm c0.')
        r = subprocess.run([str(build.COQC), *FLAGS, str(p)], cwd=HERE, capture_output=True, text=True)
        if r.returncode:
            raise ValueError('compile failed:\n' + r.stdout[-3000:] + r.stderr[-3000:])
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / 'probe.v'
            probe.write_text('From Scratch Require %s.\nPrint Assumptions %s.halt.\n' % (p.stem, p.stem))
            r = subprocess.run([str(build.COQC), *FLAGS, str(probe)], capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        if r.returncode or 'Closed under the global context' not in out:
            raise ValueError('assumption check failed:\n' + out)
        print('PASS %s: %s HALTS from the blank tape (machine-checked, no axioms)' % (p.name, machine))
    except ValueError as e:
        bad += 1
        print('FAIL %s: %s' % (p.name, e))
sys.exit(1 if bad else 0)
