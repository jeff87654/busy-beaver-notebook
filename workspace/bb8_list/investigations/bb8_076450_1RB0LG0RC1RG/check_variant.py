"""Same checks as bb8_list/proofs/check.py, for proof files kept in this scratch folder (logical path Scratch)."""
import re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'proofs'))
import build, check as chk
HERE = Path(__file__).resolve().parent / 'coq'
FLAGS = build.FLAGS + ['-Q', str(HERE), 'Scratch']
for a in sys.argv[1:]:
    p = (HERE / a).resolve()
    text = p.read_text(encoding='utf-8')
    machine = chk.declared(text)
    rows = machine.split('_')
    table, wc = chk.table_from_coq(text)
    for i, row in enumerate(rows):
        for s in (0, 1):
            want = row[3*s:3*s+3]
            want = '---' if want == '---' or want[2] == 'Z' else want
            assert table.get(('ABCDEFGH'[i], s)) == want, (i, s)
    assert re.search(r'Theorem\s+nonhalt\s*:\s*~\s*halts\s+tm\s+c0\s*\.', text)
    r = subprocess.run([str(build.COQC), *FLAGS, str(p)], cwd=HERE, capture_output=True, text=True)
    if r.returncode:
        print('FAIL compile', p.name, r.stdout[-3000:], r.stderr[-3000:]); continue
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / 'probe.v'
        probe.write_text(f'From Scratch Require {p.stem}.\nPrint Assumptions {p.stem}.nonhalt.\n')
        r = subprocess.run([str(build.COQC), *FLAGS, str(probe)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    ok = r.returncode == 0 and 'Closed under the global context' in out
    print(('PASS' if ok else 'FAIL'), p.name, machine, '' if ok else out)
