"""Assemble the halting proof: header + generated machine-level lemmas + hand-written glue (glue.v.in)."""
import sys, re
from common import *
import gen_all
TITLE = 'BB(10) candidate 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC halts'
def main(out):
    body = gen_all.generate()
    # turn the HEND pseudo-lemma into a halting lemma
    m = re.search(r'HALTLEMMA HEND \| (.*?) \| (.*?)\n(.*?)\n\n', body + '\n\n', re.S)
    binders, start = m.group(1), m.group(2)
    hend = ('Lemma HEND : forall %s, exists c, %s -->* c /\ halted tm c.\nProof.\n'
            '  intros. eexists. split.\n  - apply HEND_st1.\n  - simpl. reflexivity.\nQed.\n' % (binders, start))
    body = body[:m.start()] + hend + body[m.end():]
    text = header(TITLE) + '\n' + body + '\n' + open('glue.v.in').read()
    open(out, 'w', newline='\n').write(text)
if __name__ == '__main__':
    main(sys.argv[1])
