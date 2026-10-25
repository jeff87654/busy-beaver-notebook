"""Debug file: header + tactics of draft.v, chosen lemmas admitted, then a test block."""
import re, sys
src = open('draft.v').read()
head = src[:src.index('(** ** Crossing lemmas (generated) *)')]
keep = sys.argv[1].split(',')        # lemma statements to keep as Admitted
out = head
for nm in keep:
    m = re.search(r'^Lemma %s : .*?\.\nProof\.' % nm, src, re.S | re.M)
    out += m.group(0)[:-len('Proof.')] + 'Proof. Admitted.\n\n'
out += open(sys.argv[2]).read()
open(sys.argv[3], 'w', newline='\n').write(out)
