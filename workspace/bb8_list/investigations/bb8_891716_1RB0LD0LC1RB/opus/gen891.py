"""Complete busycoq proof for 891716 (main machine, or the relative with TM=...).

  python gen891.py OUT.v [TITLE]

Machine-level pieces explored and proved by bb8_list/autoproof (engine.py / coqgen.py): R1m, R4m (three phases),
the pass lemma Pass, and for each R3 rule a start segment (F-form -> first pass start) and an end segment
(last pass start -> F-form; it contains the last passes and the transfer loop of the deposits).
The pass iteration PassIt and the chains R3Am/R3Bm/R3Cm are hand-written (template r3glue.v.in)."""
import sys, os, time
OPUS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OPUS)
from w891 import *
import coqgen, coqgen_util
sys.path.insert(0, os.path.dirname(OPUS))
from genphases import split_phases
import passcfg

pl.LEMMAS.clear()
texts = []


def gen(name, s, t, progress, pos=()):
    t0 = time.time()
    tree = engine.explore(s, t, positive=frozenset(pos))
    g = coqgen.RuleGen(name, engine)
    txt = coqgen.rule_lemma(name, s, t, tree, g, progress=progress, positive=pos)
    texts.extend(g.lemmas + [txt])
    print('  %s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), file=sys.stderr)


def stmt(s, t, arrow='-->+'):
    cnts, vs = coqgen.free_vars(s, t)
    return 'forall %s, %s %s %s' % (' '.join(cnts + vs), coqgen.cfg_coq(s), arrow, coqgen.cfg_coq(t))


# R1
gen('R1m', *R['R1m'], True)
# R4 by phases
s, t = R['R4m']
phs = [p for p in split_phases(s, t) if pl.canon(p[0]) != pl.canon(p[1])]
pn = []
for i, (a, b, isloop) in enumerate(phs):
    nm = 'R4m_ph%d' % (i + 1)
    gen(nm, a, b, i == 0)
    pn.append(nm)
cnts, vs = coqgen.free_vars(s, t)
args = ' '.join(cnts + vs)
body = ['intros.', 'eapply progress_evstep_trans; [apply (%s %s) |].' % (pn[0], args)]
body += ['follow (%s %s).' % (nm, args) for nm in pn[1:]] + ['finish_norm.']
texts.append('Lemma R4m : %s.\nProof.\n  %s\nQed.\n' % (stmt(s, t), '\n  '.join(body)))
# the pass lemma
gen('Pass', *passcfg.pass_rule(), True)
# R3 segments: start -> first pass start (progress), last pass start -> target
SEG = {
    'R3A0': (R['R3Am'][0], PS(2, {'k': 1}, 1, {'k': 1, 'r': 1}, 0, {}), True),
    'R3B0': (R['R3Bm'][0], PS(3, {'c': 1}, 1, {'c': 1}, 0, {}), True),
    'R3C0': (R['R3Cm'][0], PS(4, {'c': 1, 'm': 1}, 1, {'c': 1}, 0, {}), True),
    # target of R3Am with the refill (01)^(2r+2) written 0 1 0 1 (0101)^r (the glue rewrites [0;1]^^(2 * r))
    'R3A1': (PS(2, {}, 1, {'r': 1}, 0, {'k': 1}),
             cfgL(P + bblk({}, 1) + mkrun((0, 0, 1, 0, 1), {'k': 1}) + [0, 0, 1, 0, 1] + mkrun(U2, {'r': 1})
                  + digit({'y': 1}) + T), False),
    'R3B1': (PS(3, {}, 1, {}, 0, {'c': 1}), R['R3Bm'][1], False),
    'R3C1': (PS(4, {'m': 1}, 1, {}, 0, {'c': 1}), R['R3Cm'][1], False),
}
for nm, (s, t, prog) in SEG.items():
    gen(nm, s, t, prog)

glue = open(os.path.join(OPUS, 'r3glue.v.in')).read()
for nm in ('R3Am', 'R3Bm', 'R3Cm'):
    glue = glue.replace('@%s@' % nm, stmt(*R[nm]))
title = sys.argv[2] if len(sys.argv) > 2 else 'BB(8) holdout 891716: %s never halts' % TM
head = open('C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof/header.v.in').read() \
    .replace('@TITLE@', title).replace('@N@', str(len(TM.split('_')))).replace('@TM@', TM) \
    .replace('@TABLE@', coqgen_util.table(TM))
fam = open(os.path.join(os.path.dirname(OPUS), 'family891.v.in')).read()
text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
    + '\n(** ** Machine-level pieces (generated) *)\n\n' + '\n'.join(texts) + '\n' + glue + '\n' + fam
open(sys.argv[1], 'w', newline='\n').write(text)
print('wrote', sys.argv[1], len(text), file=sys.stderr)
