"""Scratch generator: R1, R23 (tail l), Conv and Fin (b >= 2) machine-level lemmas with nested-loop glue."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
from coqgen_util import crossing_lemma, table
import phc
import ph891, ph891b
from ph891 import PH, Srun, Arun, S
import gen891
NL = chr(10)

def Lstr(Lfun, jc):
    """Coq text of the left stream with the deposit run of count jc (a Coq nat expression, e.g. 'j', '(j + e)', 'S j')."""
    toks = Lfun(jc)
    return phc.side2coq(toks)

def glue(name, loop, Lfun_text, ext, nvars, extra=''):
    """LOOPN_<name>: e iterations; Lfun_text(j) -> Coq left stream (with run count j)"""
    vs = ' '.join(nvars)
    return f'''
Lemma LOOPN_{name} : forall e j {vs},
  ({Lfun_text('j')}) {{{{C}}}}> ([1;0]^^(S e) *> const 0) -->*
  ({Lfun_text('(j + e)')}) {{{{C}}}}> (1 >> 0 >> const 0).
Proof.
  induction e; intros.
  - replace (j + 0) with j by lia. finish.
  - change ([1;0]^^(S (S e)) *> const 0) with (1 >> 0 >> [1;0]^^(S e) *> const 0).
    eapply evstep_trans; [apply progress_evstep, {loop} |].
    change ({Lfun_text('(S j)')}) with ({Lfun_text('(S j)')}).
    follow (IHe (S j) {vs}).
    replace (S j + e) with (j + S e) by lia. finish.
Qed.
'''

if __name__ == '__main__':
    out = sys.argv[1]
    pl.set_tm(ph891.M); pl.LEMMAS.clear()
    names = ['R1v', 'ENT_R23v', 'LOOP_R23v', 'ENT_Conv', 'LOOP_Conv', 'EXT_Conv', 'ENT_Fin', 'LOOP_Fin', 'EXT_Fin']
    phases = ''
    for nm in names:
        s, t = PH[nm]
        phases += gen891.build(nm, s, t) + NL
    cross = ''.join(crossing_lemma(n, pl.LEMMAS[n]) + NL for n in sorted(pl.LEMMAS))
    hdr = open(os.path.join(HERE, 'head891.v.in')).read()
    txt = hdr.replace('%(table)s', gen891.table(gen891.M)).replace('%(tm)s', gen891.M) + cross + phases
    open(out, 'w', newline=NL).write(txt)
    print('wrote', out, len(txt))
