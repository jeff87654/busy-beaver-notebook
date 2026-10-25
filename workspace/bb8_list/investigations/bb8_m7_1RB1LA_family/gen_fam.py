"""Complete busycoq proof for the 1RB1LA family (representative or any of the 7 variants via TM=...).

  python gen_fam.py OUT.v [TITLE|-] [mach]

Machine-level pieces explored and proved by bb8_list/autoproof (engine.py / coqgen.py): R1m, the pass lemmas Pass/PassB,
R3A0/R3A1/R3B0/R3B1/R3C0/R3C1 and R4_0/R4_1. The pass iteration and the rule chains are hand-written (glue_fam.v.in)."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
import gen_stage1 as g1
from gen_stage1 import R, stmt
import coqgen, coqgen_util
import planner8 as pl

texts = g1.build()
OLD = '  - simpl.\n    eapply progress_evstep_trans; [apply PassB_st1 |].'
NEW = '  - simpl. repeat rewrite zero_const.\n    eapply progress_evstep_trans; [apply PassB_st1 |].'
texts = [t.replace(OLD, NEW) for t in texts]
TM = g1.TM
glue = open(os.path.join(HERE, 'glue_fam.v.in')).read()
for nm in ('R3Am', 'R3Bm', 'R3Cm', 'R4m'):
    glue = glue.replace('@%s@' % nm, stmt(*R[nm]))
title = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else 'BB(8) m7 family: %s never halts' % TM
head = open('C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof/header.v.in').read() \
    .replace('@TITLE@', title).replace('@N@', str(len(TM.split('_')))).replace('@TM@', TM) \
    .replace('@TABLE@', coqgen_util.table(TM))
fam = open(os.path.join(HERE, 'family_fam.v.in')).read()
init = os.environ.get('INIT', '2,2,0').split(',')
fam = fam.replace('@INITA@', init[0]).replace('@INITD@', init[1]).replace('@INITB@', init[2])
mach = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
    + '\n(** ** Machine-level pieces (generated) *)\n\n' + '\n'.join(texts) + '\n'
NL = chr(10)
DEVHEAD = head.split('(* machine:')[0] + NL + 'From BB8 Require Import zz_FamMach.' + NL + NL
if len(sys.argv) > 3 and sys.argv[3] == 'mach':
    text = mach
elif len(sys.argv) > 3 and sys.argv[3] == 'dev':
    text = DEVHEAD + glue + (NL + fam if not os.environ.get("NOFAM") else "")
else:
    text = mach + '\n' + glue + '\n' + fam
open(sys.argv[1], 'w', newline='\n').write(text)
print('wrote', sys.argv[1], len(text), file=sys.stderr)
