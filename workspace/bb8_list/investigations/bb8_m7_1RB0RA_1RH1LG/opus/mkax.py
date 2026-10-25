"""Axiom versions of the machine-level rule lemmas (for developing the glue quickly)."""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
srcs = [HERE.parents[2] / 'proofs' / 'BB8_m7_1RB0RA_1RH1LG.v', HERE / 'tr.v', HERE.parent / 'gen' / 'cycle.v']
names = sys.argv[2].split(',')
out = []
for src in srcs:
    text = src.read_text()
    for nm in names:
        m = re.search(r'^Lemma %s : (.*?)\.\nProof\.' % re.escape(nm), text, re.M | re.S)
        if m:
            out.append('Axiom %s : %s.' % (nm, m.group(1)))
hdr = (HERE.parents[2] / 'autoproof' / 'header.v.in').read_text()
print(len(out), 'axioms', file=sys.stderr)
Path(sys.argv[1]).write_text('\n\n'.join(out) + '\n', newline='\n')
