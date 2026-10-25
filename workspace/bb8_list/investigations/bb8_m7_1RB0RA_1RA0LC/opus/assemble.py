"""assemble.py GEN.v OUT.v [stub]: generated part of GEN.v (up to the glue) + current glue.v.in/used.v.in.
With 'stub', the generated part is replaced by the header and the rule statements with Admitted (DEV ONLY, never a proof)."""
import sys, re
from pathlib import Path
src = Path(sys.argv[1]).read_text()
cut = src.index('\n(** ** The token family (hand-written part)')
gen = src[:cut]
glue = Path('glue.v.in').read_text().replace('@USED@', Path('used.v.in').read_text())
if len(sys.argv) > 3 and sys.argv[3] == 'stub':
    head = gen[:gen.index('(** ** Crossing lemmas (generated) *)')]
    rules = gen[gen.index('(** ** Machine-level rules (generated) *)'):]
    stmts = re.findall(r'^(Lemma \w+ : .*?\.)\nProof\.', rules, re.M | re.S)
    gen = head + '\n'.join(s + '\nAdmitted.\n' for s in stmts)
    init = "  do 2117 step.\n  apply evstep_refl'. reflexivity.\nQed."
    assert init in glue
    glue = glue.replace(init, '  (* stub *)\nAdmitted.')
Path(sys.argv[2]).write_text(gen + glue, newline='\n')
print('wrote', sys.argv[2], len(gen + glue))
