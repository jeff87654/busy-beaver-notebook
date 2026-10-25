"""Scratch generator: phase lemmas of the 891716 machine via planner8 -> Coq."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import planner8 as pl
from planner8 import drive
from coqgen_util import crossing_lemma, table
from scr2coq import script_to_coq2
import phc
import ph891
NL = chr(10)
M = ph891.M

def build(name, start, target, stmt=None):
    script, _ = drive(name, start, target, matchers=(), maxev=400, verbose=False)
    if script[-1][0] != 'end':
        raise SystemExit('planner did not reach target of %s: %r' % (name, script[-3:]))
    if len(script) == 1 and script[0][0] == 'end':
        n = script[0][1]
        tac = ['eapply progress_intro; [prove_step | simpl_tape].'] + (['do %d step.' % (n - 1)] if n > 1 else []) + ['finish_norm.']
    else:
        tac = script_to_coq2(script)
    body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt or phc.stmt(start, target))
    line = '  '
    for t in tac:
        if len(line) + len(t) > 100:
            body += line.rstrip() + NL; line = '  '
        line += t + ' '
    body += line.rstrip() + '\nQed.\n'
    return body

def emit(out, names):
    pl.set_tm(M)
    pl.LEMMAS.clear()
    phases = ''
    for nm in names:
        s, t = ph891.PH[nm]
        phases += build(nm, s, t) + NL
    cross = ''.join(crossing_lemma(n, pl.LEMMAS[n]) + NL for n in sorted(pl.LEMMAS))
    hdr = open(os.path.join(HERE, 'head891.v.in')).read()
    txt = hdr.replace('%(table)s', table(M)).replace('%(tm)s', M) + cross + phases
    open(out, 'w', newline=NL).write(txt)
    print('wrote', out, len(txt))

if __name__ == '__main__':
    emit(sys.argv[1], sys.argv[2:])
