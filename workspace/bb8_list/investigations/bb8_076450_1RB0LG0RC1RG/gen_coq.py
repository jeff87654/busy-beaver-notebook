"""Generate the busycoq proof for 1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0RH (and the two
H1-variants) from planner8 runs.

Usage: python gen_coq.py [main|v1|v2] out.v
"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive

MACHINES = {
    'main': "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0RH",
    'v1': "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF1RA",
    'v2': "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0LC",
}

B = lambda s: tuple(int(c) for c in s)
ABB = B('10100100')
BAB = B('10010100')
WJ = B('01001010')   # j-run of the bounce family
WK = B('01010010')   # k-run of the bounce family


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def V1(jc, jl, kc, kl, r):
    return ('G', [BLANK], [0, 0, 1, 0] + mkrun(WJ, jl, jc) + mkrun(WK, kl, kc) + [0, 1, 0] + r, '>')


def CP(nc, nl, mc, ml):
    return ('A', [BLANK], [0] + mkrun(ABB, nl, nc) + mkrun(BAB, ml, mc) + [1, BLANK], '>')


def CQ(nc, nl, mc, ml):
    return ('A', [BLANK], [0] + mkrun(ABB, nl, nc) + [1, 0, 0] + mkrun(BAB, ml, mc) + [1, BLANK], '>')


J = {'j': 1}
K = {'k': 1}
N = {'n': 1}
R = [V('r')]

# name, relation, statement, unfold, start, target
PHASES = [
    ('bounce1', '*',
     'forall j k r, V1 j (S k) r -->* V1 (S (S j)) k r',
     'V1', V1(0, J, 1, K, R), V1(2, J, 0, K, R)),
    ('entry', '+',
     'forall n r, const 0 {{A}}> 0 >> %s^^n *> 1 >> 0 >> 0 >> 1 >> r -->+ V1 0 n r' % cl(ABB),
     'V1', ('A', [BLANK], [0] + mkrun(ABB, N) + [1, 0, 0, 1] + R, '>'), V1(0, {}, 0, N, R)),
    ('exitP', '*',
     'forall j r, V1 j 0 (0 >> 1 >> 0 >> 0 >> r) -->* const 0 {{A}}> 0 >> %s^^(S j) *> 1 >> 0 >> 0 >> r' % cl(ABB),
     'V1', V1(0, J, 0, {}, [0, 1, 0, 0] + R), ('A', [BLANK], [0] + mkrun(ABB, J, 1) + [1, 0, 0] + R, '>')),
    ('exitQ', '*',
     'forall j r, V1 j 0 (0 >> 0 >> 1 >> 0 >> 1 >> 0 >> 0 >> r) -->* const 0 {{A}}> 0 >> %s^^(S (S j)) *> r' % cl(ABB),
     'V1', V1(0, J, 0, {}, [0, 0, 1, 0, 1, 0, 0] + R), ('A', [BLANK], [0] + mkrun(ABB, J, 2) + R, '>')),
    ('exitQ0', '*',
     'forall j, V1 j 0 (const 0) -->* CQ 2 (S j)',
     'V1, CQ', V1(0, J, 0, {}, [BLANK]), CQ(2, {}, 1, J)),
    ('ruleZP', '+',
     'forall n, CP n 0 -->+ CQ 2 n',
     'CP, CQ', CP(0, N, 0, {}), CQ(2, {}, 0, N)),
]


def script_to_coq(script, rel):
    out = []
    first = True
    i = 0
    while i < len(script):
        op = script[i]
        if op[0] == 'steps':
            n = op[1]
            nxt = script[i + 1]
            if first and rel == '+':
                if n == 0:
                    raise RuntimeError('-->+ lemma starting with a non-step')
                out.append('start_progress.')
            else:
                out.append('execute.')
            first = False
            if nxt[0] == 'cross':
                out.extend(['follow %s.' % nxt[1]] * nxt[2])
            elif nxt[0] == 'align':
                kind, x0, xs, cnt = nxt[1]
                c = pl.cnt_str(cnt)
                if '+' in c or not c.isidentifier():
                    raise RuntimeError('align on composite count %r' % (cnt,))
                if kind == 'ALIGN':
                    out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
                else:
                    out.append('rewrite (align_lpow_const %d %s %s). simpl app.' % (x0, cl(xs), c))
            else:
                raise RuntimeError('unexpected op %r' % (nxt,))
            i += 2
        elif op[0] == 'end':
            n = op[1]
            if first and rel == '+':
                out.append('start_progress.' if n > 0 else 'FAIL')
                n -= 1
                first = False
                out.append('finish_norm.')
            else:
                out.append('do %d step. finish_norm.' % n)
            i += 1
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return out


def crossing_lemma(name, lm):
    q, d, xs, ys, ctx = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['ctx']
    ctxs = ''.join('%d >> ' % c for c in ctx)
    if d == '>':
        stmt = 'forall n l r, %sl {{%s}}> %s^^n *> r -->* %s^^n *> %sl {{%s}}> r' % (ctxs, q, cl(xs), cl(ys), ctxs, q)
    else:
        stmt = 'forall n l r, %s^^n *> l <{{%s}} %sr -->* l <{{%s}} %s^^n *> %sr' % (cl(xs), q, ctxs, q, cl(ys), ctxs)
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n'
            % (name, stmt))


HEADER = r'''(** * BB(8) holdout, subtask 76450: %(tm)s never halts *)

(** Formalization of [bb8_list/investigations/bb8_076450_1RB0LG0RC1RG.md].
    Tape words: a = 10, b = 100, x = 1; abb = 10100100, bab = 10010100.
    Configuration family (head in state A on the blank cell left of the word):
      CP n m = 0^inf A> 0 (abb)^n (bab)^m 1 0^inf
      CQ n m = 0^inf A> 0 (abb)^n 100 (bab)^m 1 0^inf
    Rules (all n, m >= 0):
      ruleRP : CP n (S m) -->+ CQ (2n+1) m
      ruleRQ : CQ n (S m) -->+ CP (2n+2) m
      ruleZP : CP n 0     -->+ CQ 2 n
      ruleZQ : CQ n 0     -->+ CQ 2 (2n+1)
    The doubling rules RP, RQ, ZQ go through the bounce family
      V1 j k r = 0^inf G> 0 0 1 0 (01001010)^j (01010010)^k 0 1 0 r
    with  bounce1 : V1 j (S k) r -->* V1 (S (S j)) k r.
    The blank tape reaches CQ 2 0 after %(init)d steps.
    Generated by gen_coq.py (planner8.py mirrors [execute] on symbolic tapes). *)

From BB8 Require Import Individual82.
From Coq Require Import Lia PeanoNat.
Set Default Goal Selector "!".

(* machine: %(tm)s *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
%(table)s
  end.

Notation "c --> c'" := (c -[ tm ]-> c')   (at level 40).
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

(** ** Tape normalization (as in BB7_16582_1RB1LD.v) *)

Lemma align_lpow : forall (x : Sym) xs ys n,
  (x::xs)^^n *> x >> ys = x >> (xs ++ [x])^^n *> ys.
Proof.
  induction n.
  - reflexivity.
  - simpl. repeat rewrite Str_app_assoc. rewrite IHn. reflexivity.
Qed.

Lemma align_lpow_const : forall (x : Sym) xs n,
  (x::xs)^^n *> const x = x >> (xs ++ [x])^^n *> const x.
Proof. intros. rewrite const_unfold at 1. apply align_lpow. Qed.

Ltac align_tape := repeat ((rewrite align_lpow || rewrite align_lpow_const); simpl app).
Ltac norm_nat := repeat progress (rewrite ?Nat.add_succ_r, ?Nat.add_0_r; simpl).
Ltac finish_norm := apply evstep_refl'; norm_nat; align_tape; try reflexivity; lia_refl.

(** ** Configurations *)

Definition CP (n m : nat) : Q * tape :=
  const 0 {{A}}> 0 >> %(abb)s^^n *> %(bab)s^^m *> 1 >> const 0.

Definition CQ (n m : nat) : Q * tape :=
  const 0 {{A}}> 0 >> %(abb)s^^n *> 1 >> 0 >> 0 >> %(bab)s^^m *> 1 >> const 0.

Definition V1 (j k : nat) (r : side) : Q * tape :=
  const 0 {{G}}> 0 >> 0 >> 1 >> 0 >> %(wj)s^^j *> %(wk)s^^k *> 0 >> 1 >> 0 >> r.

(** ** Crossing a run of 8-cell blocks (blocks in stream order, nearest the head first;
    the literal cells before [l] / [r] are context that is read and restored) *)

'''

TAIL = r'''
(** ** Iterated bounce *)

Lemma bounce : forall k j r, V1 j k r -->* V1 (j + 2 * k) 0 r.
Proof.
  induction k; intros.
  - finish.
  - follow bounce1. follow IHk. finish.
Qed.

(** ** The four rules *)

Lemma ruleRP : forall n m, CP n (S m) -->+ CQ (S (n + n)) m.
Proof.
  intros. unfold CP.
  eapply progress_evstep_trans.
  { apply (entry n (0 >> 1 >> 0 >> 0 >> %(bab)s^^m *> 1 >> const 0)). }
  follow bounce. follow exitP. unfold CQ. finish.
Qed.

Lemma ruleRQ : forall n m, CQ n (S m) -->+ CP (S (S (n + n))) m.
Proof.
  intros. unfold CQ.
  eapply progress_evstep_trans.
  { apply (entry n (0 >> 0 >> 1 >> 0 >> 1 >> 0 >> 0 >> %(bab)s^^m *> 1 >> const 0)). }
  follow bounce. follow exitQ. unfold CP. finish.
Qed.

Lemma ruleZQ : forall n, CQ n 0 -->+ CQ 2 (S (n + n)).
Proof.
  intros. unfold CQ at 1.
  eapply progress_evstep_trans.
  { apply (entry n (const 0)). }
  follow bounce. follow exitQ0. finish.
Qed.

(** ** Reaching the family from the blank tape *)

Lemma init_reach : c0 -->* CQ 2 0.
Proof. unfold CQ. do %(init)d step. finish_norm. Qed.

(** ** Non-halting *)

Definition cfg (i : bool * nat * nat) : Q * tape :=
  match i with
  | (true, n, m) => CP n m
  | (false, n, m) => CQ n m
  end.

Lemma cfg_step : forall i, exists i', cfg i -->+ cfg i'.
Proof.
  intros [[[] n] [| m]].
  - exists (false, 2%%nat, n). apply ruleZP.
  - exists (false, S (n + n), m). apply ruleRP.
  - exists (false, 2%%nat, S (n + n)). apply ruleZQ.
  - exists (true, S (S (n + n)), m). apply ruleRQ.
Qed.

Theorem nonhalt : ~ halts tm c0.
Proof.
  apply multistep_nonhalt with (cfg (false, 2%%nat, 0%%nat)).
  - apply init_reach.
  - apply progress_nonhalt_simple. apply cfg_step.
Qed.
'''


def table(tms):
    rows = []
    for qi, ch in enumerate(tms.split('_')):
        q = 'ABCDEFGH'[qi]
        ents = []
        for s in (0, 1):
            e = ch[3 * s:3 * s + 3]
            if e == '---':
                ents.append('| %s, %d => None' % (q, s))
            else:
                ents.append('| %s, %d => Some (%s, %s, %s)' % (q, s, e[0], e[1], e[2]))
        rows.append('  ' + '  '.join('%-24s' % x for x in ents).rstrip())
    return '\n'.join(rows)


def init_steps(tms):
    """First step at which the blank-tape run is in configuration CQ 2 0 (literal simulation)."""
    from tmlib import Sim, expand
    sim = Sim(tms, '', pad=4000)
    target = expand('abb*2 b x')
    for _ in range(100000):
        sim.step()
        if sim.state == 0 and sim.tape[sim.pos] == 0 and sim.at_left_A0() and sim.word() == target:
            return sim.steps
    raise RuntimeError('CQ 2 0 not reached')


def main():
    which = sys.argv[1]
    outp = sys.argv[2]
    tms = MACHINES[which]
    pl.set_tm(tms)
    pl.LEMMAS.clear()
    bodies = []
    for name, rel, stmt, unf, start, target in PHASES:
        script, _ = drive(name, start, target, maxev=400, verbose=False)
        tac = script_to_coq(script, rel)
        body = 'Lemma %s : %s.\nProof.\n  intros. unfold %s.\n' % (name, stmt, unf)
        line = '  '
        for t in tac:
            if len(line) + len(t) > 100:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        bodies.append(body)
        nsteps = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('%-8s literal steps %4d, ops %d' % (name, nsteps, len(script)), file=sys.stderr)
    subst = dict(tm=tms, table=table(tms), abb=cl(ABB), bab=cl(BAB), wj=cl(WJ), wk=cl(WK), init=init_steps(tms))
    text = HEADER % subst
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += TAIL % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(pl.LEMMAS), 'crossing lemmas', file=sys.stderr)


if __name__ == '__main__':
    main()
