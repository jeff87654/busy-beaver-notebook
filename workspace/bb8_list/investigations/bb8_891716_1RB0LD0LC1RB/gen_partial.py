"""Generate the partial proof: engine-proved R1 and R4 (phases), R3A/R3B/R3C statements Admitted, abstract totality argument."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
from rules891 import *
import engine, coqgen, coqgen_util
from genphases import split_phases


def main(outp):
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    R = rules()
    texts = []
    # R1
    s, t = R['R1m']
    tree = engine.explore(s, t)
    gen = coqgen.RuleGen('R1m', engine)
    txt = coqgen.rule_lemma('R1m', s, t, tree, gen, progress=True)
    texts += gen.lemmas + [txt]
    # R4 by phases
    s, t = R['R4m']
    phs = [p for p in split_phases(s, t) if pl.canon(p[0]) != pl.canon(p[1])]
    pn = []
    for i, (a, b, isloop) in enumerate(phs):
        nm = 'R4m_ph%d' % (i + 1)
        tree = engine.explore(a, b)
        gen = coqgen.RuleGen(nm, engine)
        txt = coqgen.rule_lemma(nm, a, b, tree, gen, progress=(i == 0))
        texts += gen.lemmas + [txt]
        pn.append(nm)
    cnts, vs = coqgen.free_vars(s, t)
    args = ' '.join(cnts + vs)
    stmt = '%s -->+ %s' % (coqgen.cfg_coq(s), coqgen.cfg_coq(t))
    body = ['intros.', 'eapply progress_evstep_trans; [apply (%s %s) |].' % (pn[0], args)]
    for nm in pn[1:]:
        body.append('follow (%s %s).' % (nm, args))
    body.append('finish_norm.')
    texts.append('Lemma R4m : forall %s, %s.\nProof.\n  %s\nQed.\n' % (args, stmt, '\n  '.join(body)))
    # Pass lemma (one zero digit and two units of the long run per pass, a (10101) deposited at the far end)
    import passcfg
    s, t = passcfg.pass_rule()
    tree = engine.explore(s, t)
    gen = coqgen.RuleGen('Pass', engine)
    txt = coqgen.rule_lemma('Pass', s, t, tree, gen, progress=True)
    texts += gen.lemmas + [txt]
    # R3 statements, admitted
    adm = []
    for nm in ('R3Am', 'R3Bm', 'R3Cm'):
        s, t = R[nm]
        cnts, vs = coqgen.free_vars(s, t)
        adm.append('(* TODO: machine-level proof (bilinear loops, see the report) *)\nLemma %s : forall %s, %s -->+ %s.\nProof. Admitted.\n'
                   % (nm, ' '.join(cnts + vs), coqgen.cfg_coq(s), coqgen.cfg_coq(t)))
    nst = len(TM.split('_'))
    head = open('C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof/header.v.in').read() \
        .replace('@TITLE@', 'BB(8) holdout 891716: %s (partial: R3 machine-level lemmas admitted)' % TM) \
        .replace('@N@', str(nst)).replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
    fam = open(os.path.join(HERE, 'family891.v.in')).read()
    text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() + '\n(** ** Machine-level rules *)\n\n' \
        + '\n'.join(texts) + '\n' + '\n'.join(adm) + '\n' + fam
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, len(text))


if __name__ == '__main__':
    main(sys.argv[1])
