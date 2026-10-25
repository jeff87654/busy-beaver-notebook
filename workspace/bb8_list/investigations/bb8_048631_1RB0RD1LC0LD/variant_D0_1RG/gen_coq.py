"""Generate the busycoq proof file (parts) for 1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB."""
import sys, pickle
import planner9 as P
import fam9 as F
from planner9 import C

BL = P.BLANK
R0 = F.R0

def tl_lemmas():
    start = ('E', [('run', (0,0,1), C(0, c=1)), ('run', (1,1,1), C(1, b=1)), P.V('l')], list(R0), '>')
    tgt = ('E', [('run', (0,0,1), C(3, c=1)), ('run', (1,1,1), C(0, b=1)), P.V('l')], list(R0), '>')
    script, end = P.drive('TL1', start, tgt, maxev=200, verbose=False)
    assert script[-1] == ('end',)
    txt = P.lemma_text('TL1', start, tgt, script, '-->+')
    txt += '''
Lemma TLs : forall b c c' l, c' = c + 3 * b ->
  ([0;0;1]^^c *> [1;1;1]^^b *> l) {{E}}> (1 >> 0 >> 0 >> 1 >> 1 >> const 0) -->*
  ([0;0;1]^^c' *> l) {{E}}> (1 >> 0 >> 0 >> 1 >> 1 >> const 0).
Proof.
  induction b; intros c c' l Hc.
  - subst. rewrite Nat.mul_0_r, Nat.add_0_r. apply evstep_refl.
  - eapply evstep_trans.
    + apply progress_evstep. replace (S b) with (b + 1) by lia. apply TL1.
    + apply IHb. lia.
Qed.
'''
    return txt

def family_def(name, tpl):
    return 'Definition %s (z y x : nat) : Q * tape :=\n  %s.\n' % (name, P.cfg_coq(tpl))

def evar_lemma(name, stmt, unfold_from, unfold_to, script):
    """c -->+ T proved as c -->+ ?c1 (script, then evstep_refl) and ?c1 = T (unfold, reflexivity)."""
    tac = P.script_to_coq(script, True)
    body = 'Lemma %s : %s.\nProof.\n  intros. unfold %s. eapply progress_to_eq.\n  {\n' % (name, stmt, unfold_from)
    line = '    '
    for t in tac + ['apply evstep_refl.']:
        if len(line) + len(t) > 110:
            body += line.rstrip() + '\n'
            line = '    '
        line += t + ' '
    body += line.rstrip() + '\n  }\n  unfold %s. first [reflexivity | rewrite ?kN_eq; lia_refl].\nQed.\n' % unfold_to
    return body


def round_lemma(name, ph, SC, fam_from, fam_to, args_from, args_to):
    tpl, start, script, got, tnext = SC[ph]
    stmt = 'forall z y x, %s %s -->+ %s %s' % (fam_from, args_from, fam_to, args_to)
    return evar_lemma(name, stmt, fam_from, fam_to, script)




def init_lemma(script, target_args):
    tac = P.script_to_coq(script, False)
    body = ('Lemma INIT : c0 -->* PA %s.\nProof.\n'
            '  change c0 with (A;; const 0 {{0}} const 0). eapply evstep_to_eq.\n  {\n') % target_args
    line = '    '
    for t in tac + ['apply evstep_refl.']:
        if len(line) + len(t) > 110:
            body += line.rstrip() + '\n'
            line = '    '
        line += t + ' '
    body += line.rstrip() + '\n  }\n  unfold PA. first [reflexivity | rewrite ?kN_eq; lia_refl].\nQed.\n'
    return body


def tm_def(tm):
    rows = tm.split('_')
    lines = ["Definition tm : TM := fun '(q, s) =>", '  match q, s with']
    for i, row in enumerate(rows):
        q = 'ABCDEFGH'[i]
        parts = []
        for sy in (0, 1):
            e = row[3 * sy:3 * sy + 3]
            rhs = 'None' if e == '---' else 'Some (%s, %s, %s)' % (e[0], e[1], e[2])
            parts.append('| %s, %d => %s' % (q, sy, rhs))
        lines.append('  ' + '  '.join(parts))
    lines.append('  end.')
    return chr(10).join(lines)


def args_coq(t):
    return ' '.join(P.ccoq(c) for c in t)


if __name__ == '__main__':
    out = open('coq_head.v.in').read()
    ORIG = '1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB'
    if P.TM != ORIG:
        out = out.replace('(** * BB(8) holdout, subtask 48631: ' + ORIG + ' never halts *)',
                          '(** * BB(8) holdout variant (D0 of subtask 48631): ' + P.TM + ' never halts *)' + chr(10) + chr(10) +
                          '(** Same families and rules as BB8_48631_1RB0RD.v (' + ORIG + '); the scripts are regenerated for this machine. *)')
    out = out.replace('(* machine: ' + ORIG + ' *)', '(* machine: %s *)' % P.TM)
    i0 = out.index('Definition tm : TM')
    i1 = out.index('  end.', i0) + len('  end.')
    out = out[:i0] + tm_def(P.TM) + out[i1:]
    SC = pickle.load(open('rounds.pkl', 'rb'))
    EN = pickle.load(open('endings.pkl', 'rb'))
    tlt = tl_lemmas()
    P.LEMMAS.update(pickle.load(open('lemmas.pkl', 'rb')))
    P.LEMMAS.update(pickle.load(open('lemmas2.pkl', 'rb')))
    out += '\n(** ** Crossing a run of blocks (generated) *)\n\n'
    for nm, lm in sorted(P.LEMMAS.items()):
        out += P.crossing_lemma(nm, lm) + '\n'
    out += '\n(** ** The tripling loop TL *)\n\n' + tlt
    out += '\n(** ** Families *)\n\n'
    for ph, nm in (('A', 'PA'), ('B', 'PB'), ('C', 'PC')):
        out += family_def(nm, SC[ph][0]) + '\n'
    out += '\n(** ** Rounds (z -> z - 1) *)\n\n'
    out += round_lemma('RA', 'A', SC, 'PA', 'PB', '(z + 1) (y + 12) (x + 6)', 'z (y + 5) (27 * x + kN 4083)') + '\n'
    out += round_lemma('RB', 'B', SC, 'PB', 'PC', '(z + 1) (y + 12) (x + 6)', 'z (y + 6) (27 * x + kN 4136)') + '\n'
    out += round_lemma('RC', 'C', SC, 'PC', 'PA', '(z + 1) (y + 12) (x + 6)', 'z (y + 4) (27 * x + kN 4166)') + '\n'
    out += '\n(** ** Endings (z = 0) and the y-ending of the first phase *)\n\n'
    for key, ff, ft in (('EA', 'PA', 'PB'), ('EB', 'PB', 'PC'), ('EC', 'PC', 'PA')):
        start, script, exp, targs = EN[key]
        stmt = 'forall y x, %s 0 (y + 20) (x + 6) -->+ %s %s' % (ff, ft, args_coq(targs))
        out += evar_lemma(key, stmt, ff, ft, script) + '\n'
    start, script, exp, targs = EN['Y4']
    stmt = 'forall z x, PA (z + 5) (kN 4) (x + 6) -->+ PC %s' % args_coq(targs)
    out += evar_lemma('Y4', stmt, 'PA', 'PC', script) + '\n'
    out += '\n(** ** From the blank tape to the first family configuration *)\n\n'
    start, script, exp, targs = EN['INIT']
    out += init_lemma(script, args_coq(targs)) + '\n'
    out += open('coq_tail.v.in').read()
    open(sys.argv[1], 'w', newline=chr(10)).write(out)
