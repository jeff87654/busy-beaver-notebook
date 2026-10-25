import re,sys
s=open('coq/BB8_16582_1RB1RD.v').read()
s=re.sub(r'(Lemma cr_\w+ :[^\n]*)\nProof\. induction[^\n]*Qed\.\n',lambda m:m.group(1)+'\nProof. Admitted.\n',s)
s=re.sub(r'(Lemma (?:P1|P2|Q1|Q2|X1|X0|P0|R0) :[^\n]*)\nProof\.\n.*?\nQed\.\n',lambda m:m.group(1)+'\nProof. Admitted.\n',s,flags=re.S)
open('coq/dbg.v','w').write(s)
