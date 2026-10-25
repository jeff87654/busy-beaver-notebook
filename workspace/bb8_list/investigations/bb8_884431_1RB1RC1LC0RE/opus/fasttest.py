"""Fast check of the template: machine-level rule lemmas stated with Admitted, then the family part (scratch only)."""
import re, sys
src = open(sys.argv[1]).read()
head = src[:src.index('(** ** Crossing lemmas (generated) *)')]
rules = src[src.index('(** ** Machine-level pieces (generated) *)'):src.index('(** ** The digit-list family')]
fam = src[src.index('(** ** The digit-list family'):]
stmts = re.findall(r'^(Lemma \w+ : .*?\.)\nProof\.', rules, re.S | re.M)
out = head + '\n'.join(s + '\nProof. Admitted.\n' for s in stmts) + '\n' + fam
open(sys.argv[2], 'w', newline='\n').write(out)
print(len(stmts), 'admitted rule statements')
