"""Generate the busycoq NON-HALTING proofs for 1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---
and its G0/H0 variants, from planner8 runs (phases defined in explore.py).

Usage: python gen_coq.py VARIANT out.v        (VARIANT = main, G0_1LH_H0_0RA, ..., see VARIANTS)
       python gen_coq.py all DIR               (writes every variant into DIR)
Fixed parts: coq_head.v.in and coq_tail.v.in (Python %-templates).
script_to_coq, crossing_lemma and table (coqgen_util.py) are copied unchanged from
../bb8_076450_1RB1LE0LC1RE/gen_coq.py.
"""
import os
import sys
import planner8 as pl
from planner8 import drive, mkrun, BLANK
import explore as ex
from coqgen_util import script_to_coq, crossing_lemma, table

PREFIX = '1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_'
T10 = mkrun((1, 0), {'i': 1})


def topz_simple(c, w):
    return ('  intros. destruct (EX (B * 4 + %d) %d []) as [B1 [H1 H2]].\n'
            '  exists (S (B * 4 + %d)), B1. rewrite app_nil_r in H1. exact H1.' % (c, w, c))


def init_ex(ds_coq, word_steps, j, w):
    return ('  assert (Hi : c0 -->* Kc %s 1 1) by (unfold Kc; simpl; do %d step; finish).\n'
            '  destruct (EX %d %d []) as [B1 [H1 H2]].\n'
            '  exists (S %d), B1. rewrite app_nil_r in H1. eapply evstep_trans; [exact Hi | exact H1].'
            % (ds_coq, word_steps, j, w, j))


# name -> (G0 H0 suffix, file name, END4b planner target (left side), END4b Coq left side,
#          c, tail, topz proof, init proof, comments)
VARIANTS = {
    'main': dict(
        v='0LH1LF_1RF---', file='BB8_76450_1RB1RA.v',
        end4=[1, 0] + T10 + [1, 1, BLANK], end4_coq='1 >> 0 >> [1;0]^^i *> 1 >> 1 >> const 0',
        end4_comment='0^inf 1 1 (01)^(i+1)',
        c=4, tail='[2%nat]', top_comment='Kc (1^(4 b0 + 4) ++ [2]) 1 1 (digits 2,1,...,1)',
        topz=topz_simple(4, 1), init=init_ex('[2%nat]', 52, 0, 1),
        init_comment='Kc [2] 1 1 after 52 steps'),
    'G0_1LH_H0_0RA': dict(
        v='1LH1LF_0RA---', file='BB8_76450_1RB1RA_G0_1LH_H0_0RA.v',
        end4=[1, 0] + T10 + [1, 1, BLANK], end4_coq='1 >> 0 >> [1;0]^^i *> 1 >> 1 >> const 0',
        end4_comment='0^inf 1 1 (01)^(i+1)',
        c=4, tail='[2%nat]', top_comment='Kc (1^(4 b0 + 4) ++ [2]) 1 1 (digits 2,1,...,1)',
        topz=topz_simple(4, 1), init=init_ex('[2%nat]', 50, 0, 1),
        init_comment='Kc [2] 1 1 after 50 steps'),
    'G0_1LH_H0_1LA': dict(
        v='1LH1LF_1LA---', file='BB8_76450_1RB1RA_G0_1LH_H0_1LA.v',
        end4=[1, 0] + T10 + [1, 1, 0, 1, BLANK],
        end4_coq='1 >> 0 >> [1;0]^^i *> 1 >> 1 >> 0 >> 1 >> const 0',
        end4_comment='0^inf 1 0 1 1 (01)^(i+1)',
        c=4, tail='[2%nat; 1%nat]', top_comment='Kc (1^(4 b0 + 4) ++ [2; 1]) 1 1 (digits 1,2,1,...,1)',
        topz=('  intros. destruct (EX (B * 4 + 4) 1 [1%nat]) as [B1 [H1 H2]].\n'
              '  destruct (IN (B * 4 + 4) 1 [] B1 ltac:(lia)) as [B2 [H3 H4]].\n'
              '  exists (S (S (B * 4 + 4))), B2. rewrite app_nil_r in H3.\n'
              '  eapply evstep_trans; [exact H1 | exact H3].'),
        init=('  assert (Hi : c0 -->* Kc [2%nat; 1%nat] 1 1) by (unfold Kc; simpl; do 52 step; finish).\n'
              '  destruct (EX 0 1 [1%nat]) as [B1 [H1 H2]].\n'
              '  destruct (IN 0 1 [] B1 ltac:(lia)) as [B2 [H3 H4]].\n'
              '  exists 2%nat, B2. rewrite app_nil_r in H3.\n'
              '  eapply evstep_trans; [exact Hi |]. eapply evstep_trans; [exact H1 | exact H3].'),
        init_comment='Kc [2; 1] 1 1 after 52 steps'),
    'G0_1LH_H0_1RA': dict(
        v='1LH1LF_1RA---', file='BB8_76450_1RB1RA_G0_1LH_H0_1RA.v',
        end4=[1, 0] + T10 + [1, 1, 1, BLANK], end4_coq='1 >> 0 >> [1;0]^^i *> 1 >> 1 >> 1 >> const 0',
        end4_comment='0^inf 1 1 1 (01)^(i+1)',
        c=4, tail='[3%nat]', top_comment='Kc (1^(4 b0 + 4) ++ [3]) 1 1 (digits 3,1,...,1)',
        topz=topz_simple(4, 2), init=init_ex('[3%nat]', 50, 0, 2),
        init_comment='Kc [3] 1 1 after 50 steps'),
    'G0_1LH_H0_1RB': dict(
        v='1LH1LF_1RB---', file='BB8_76450_1RB1RA_G0_1LH_H0_1RB.v',
        end4=[1, 0, 1, 0] + T10 + [1, BLANK], end4_coq='1 >> 0 >> 1 >> 0 >> [1;0]^^i *> 1 >> const 0',
        end4_comment='0^inf 1 (01)^(i+2)',
        c=5, tail='[1%nat]', top_comment='Kc (1^(4 b0 + 5) ++ [1]) 1 1 (digits 1,...,1)',
        topz=topz_simple(5, 0), init=init_ex('[1%nat; 1%nat]', 50, 1, 0),
        init_comment='Kc [1; 1] 1 1 after 50 steps'),
    'G0_1LH_H0_0RB': dict(
        v='1LH1LF_0RB---', file='BB8_76450_1RB1RA_G0_1LH_H0_0RB.v',
        end4=[1, 0] + T10 + [1, BLANK], end4_coq='1 >> 0 >> [1;0]^^i *> 1 >> const 0',
        end4_comment='0^inf 1 (01)^(i+1)',
        c=4, tail='[1%nat]', top_comment='Kc (1^(4 b0 + 4) ++ [1]) 1 1 (digits 1,...,1)',
        topz=topz_simple(4, 0), init=init_ex('[1%nat]', 50, 0, 0),
        init_comment='Kc [1] 1 1 after 50 steps'),
    'H0_1LA': dict(
        v='0LH1LF_1LA---', file='BB8_76450_1RB1RA_H0_1LA.v',
        end4=T10 + [1, 1, 1, 1, 1, BLANK], end4_coq='[1;0]^^i *> 1 >> 1 >> 1 >> 1 >> 1 >> const 0',
        end4_comment='0^inf 1 1 1 1 1 (01)^i',
        c=3, tail='[5%nat]', top_comment='Kc (1^(4 b0 + 3) ++ [5]) 1 1 (digits 5,1,...,1)',
        topz=topz_simple(3, 4),
        init=('  assert (Hi : c0 -->* Kc [] 5 1) by (unfold Kc; simpl; do 64 step; finish).\n'
              '  destruct (R1iter 5 [] 0) as [B1 [H1 H2]].\n'
              '  exists 0%nat, B1. eapply evstep_trans; [exact Hi | exact H1].'),
        init_comment='Kc [] 5 1 after 64 steps'),
}

PHASES = [
    ('TR1', 'forall l, (1 >> 0 >> 1 >> l) {{B}}> const 0 -->+ '
            '(1 >> 1 >> 1 >> 1 >> 0 >> l) {{A}}> const 0'),
    ('TR2', 'forall r l, ([1]^^r *> 0 >> 1 >> l) {{A}}> const 0 -->+ '
            '(1 >> 1 >> 1 >> 1 >> [1]^^r *> 0 >> l) {{A}}> const 0'),
    ('ENTRY', 'forall m l, ([1]^^m *> 0 >> 0 >> l) {{A}}> const 0 -->+ '
              '(1 >> 1 >> 1 >> 1 >> [1]^^m *> 0 >> l) {{C}}> const 0'),
    ('LOOP', 'forall r l rr, (1 >> 1 >> 1 >> [1]^^r *> 0 >> 0 >> l) {{C}}> 0 >> rr -->+ '
             '(1 >> 1 >> [1]^^r *> 0 >> l) {{C}}> 0 >> 1 >> 0 >> rr'),
    ('FINAL', 'forall r i l, (1 >> 1 >> 1 >> [1]^^r *> 0 >> 1 >> l) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
              '(1 >> 0 >> [1;0]^^i *> 1 >> 1 >> 1 >> [1]^^r *> 0 >> l) {{B}}> const 0'),
    ('END4b', None),
]


def gen(name, outp):
    var = VARIANTS[name]
    tm = PREFIX + var['v']
    pl.set_tm(tm)
    pl.LEMMAS.clear()
    ph = dict(ex.PH)
    ph['END4b'] = (('C', [1, 1, 0, BLANK], [0] + T10 + [BLANK], '>'), ('B', var['end4'], [BLANK], '>'))
    bodies = []
    for pname, stmt in PHASES:
        if stmt is None:
            stmt = ('forall i, (1 >> 1 >> 0 >> const 0) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                    '(%s) {{B}}> const 0' % var['end4_coq'])
        start, target = ph[pname]
        script, _ = drive(pname, start, target, matchers=(), maxev=400, verbose=False)
        if len(script) == 1 and script[0][0] == 'end':
            # purely literal phase: take the first step explicitly (start_progress would run to the end)
            tac = ['eapply progress_intro; [prove_step | simpl_tape].',
                   'do %d step. finish_norm.' % (script[0][1] - 1)]
        else:
            tac = script_to_coq(script, True)
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (pname, stmt)
        line = '  '
        for t in tac:
            if len(line) + len(t) > 100:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        bodies.append(body)
        nsteps = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('  %-6s literal steps %4d, ops %d' % (pname, nsteps, len(script)), file=sys.stderr)
    subst = dict(tm=tm, table=table(tm), c=var['c'], tail=var['tail'], topz=var['topz'], init=var['init'],
                 top_comment=var['top_comment'], end4_comment=var['end4_comment'],
                 init_comment=var['init_comment'])
    text = open('coq_head.v.in').read() % subst
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += open('coq_tail.v.in').read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(pl.LEMMAS), 'crossing lemmas', file=sys.stderr)


def main():
    if sys.argv[1] == 'all':
        for name, var in VARIANTS.items():
            gen(name, os.path.join(sys.argv[2], var['file']))
    else:
        gen(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()
