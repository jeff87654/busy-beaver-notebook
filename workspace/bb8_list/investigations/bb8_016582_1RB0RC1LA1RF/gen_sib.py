"""Generate the translated-cycler proof for the two G0-siblings of the main machine.
usage: python gen_sib.py G0 out.v      (G0 = 1RE or 1RB)"""
import sys, os, threading
threading.Timer(200, lambda: os._exit(3)).start()
import planner8 as pl
from planner8 import drive, mkrun, BLANK
from gen_base import script_to_coq, crossing_lemma, table
import gen as g
G0 = sys.argv[1]
TM = "1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_%s1LE_---1LF" % G0
pl.set_tm(TM)
pl.LEMMAS.clear()
k = {'k': 1}
blk = (0, 0, 0, 1)
start = ('E', [BLANK], [0, 1, 0, 1] + mkrun(blk, k, 1) + [BLANK], '>')
target = ('E', [BLANK], [0, 1, 0, 1] + mkrun(blk, k, 2) + [BLANK], '>')
script, _ = drive('CY', start, target, matchers=(), maxev=100, verbose=True)
tac = script_to_coq(script, True)
stmt = 'forall k, %s -->+ %s' % (g.cfg_coq(start), g.cfg_coq(target))
body = 'Lemma CY : %s.\nProof.\n  intros.\n  %s\nQed.\n' % (stmt, ' '.join(tac))
text = ''
for nm in sorted(pl.LEMMAS):
    text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
head = open('head.v.in').read() % dict(tm=TM, table=table(TM))
head = head.replace('(** * BB(8), enumerator job 016582: %s never halts *)' % TM, '(** * BB(8), enumerator job 016582 sibling: %s never halts (translated cycler: E> 0 1 0 1 (0001)^k, +1 block per 18 steps) *)' % TM)
tail = '''
Definition Cc (k : nat) : Q * tape := const 0 {{E}}> 0 >> 1 >> 0 >> 1 >> [0;0;0;1]^^k *> const 0.

Lemma CYf : forall k, Cc (S k) -->+ Cc (S (S k)).
Proof. intros. unfold Cc. apply CY. Qed.

Lemma init_reach : c0 -->* Cc 1.
Proof. unfold Cc. do 41 step. repeat rewrite <- const_unfold. finish. Qed.

Theorem nonhalt : ~ halts tm c0.
Proof.
  apply multistep_nonhalt with (Cc 1). { apply init_reach. }
  apply (progress_nonhalt_simple tm nat (fun k => Cc (S k)) 0%nat).
  intros k. exists (S k). apply CYf.
Qed.
'''
open(sys.argv[2], 'w', newline=chr(10)).write(head + text + body + tail)
print('wrote', sys.argv[2])
