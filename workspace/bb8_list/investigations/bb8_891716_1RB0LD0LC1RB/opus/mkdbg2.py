"""Debug file: header of draft.v, the generated pieces Pass/R3?0/R3?1 admitted, then the glue section of draft.v."""
import re
src = open('draft.v').read()
head = src[:src.index('(** ** Crossing lemmas (generated) *)')]
out = head
for nm in 'Pass R3A0 R3B0 R3C0 R3A1 R3B1 R3C1'.split():
    m = re.search(r'^Lemma %s : .*?\.\nProof\.' % nm, src, re.S | re.M)
    out += m.group(0)[:-len('Proof.')] + 'Proof. Admitted.\n\n'
out += src[src.index('(** ** R3 machine-level rules'):src.index('(** ** The family')]
open('dbg2.v', 'w', newline='\n').write(out)
