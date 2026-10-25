"""Generate complete, axiom-free Coq halting proofs for:
  1. BB9_champ20_3round.v:
     1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RA0RI_0LG---
     The 9-state 3-round (E_3, Sigma > f_omega^2(3 ^^^ 20)) champion extension of champ_231.
  2. BB9_champ20_kkhkhk.v:
     1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---
     (KKHKHK_231_144, which halts on Round 1 via the 5-stage parity-shifted cascade at I1 = ---,
      and also satisfies the Odd-k halting lemma for all k = 2m + 1 >= 5.)
"""
import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util

M_3ROUND = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RA0RI_0LG---"
M_KKHKHK = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"

def get_base_stages():
    return [
        ('R1', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 1, 1] + mkrun((1, 1), {'a': 1}, 0) + [0, 0, V('r')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 1, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [1, 1, 0, 0] + mkrun((1, 1), {'a': 1}, 0) + [0, 0, V('r')]), '<')),
        ('R2', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, 1, 1] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 0, 0, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [1, 1, 1, 0, 0] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '<')),
        ('R2_gen', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, 1, 1, V('r')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 0, 0, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [1, 1, 1, 0, 0, V('r')]), '<')),
        ('ENTRY', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, V('r')]), '<'),
         ('D', pl.norm_side([0, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 1, 0, 1, BLANK]), [V('r')], '>')),
        ('LOOP', True,
         ('D', pl.norm_side([0, 1, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [0, V('X')]), [0, 0, V('r')], '>'),
         ('D', pl.norm_side([0, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 1, 0, 1, V('X')]), [V('r')], '>')),
        ('FINAL', True,
         ('D', pl.norm_side([0, 1, 1] + mkrun((1, 1), {'s': 1}, 0) + [0, 0, 1, 0, 1, 0, 1, 0, 1] + mkrun((0, 1, 0, 1), {'m': 1}, 0) + [BLANK]),
               pl.norm_side([1, 1] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '>'),
         ('E', [BLANK], pl.norm_side(mkrun((1, 0, 0, 1), {'m': 1}, 0) + [1, 0, 0, 1, 1, 0, 0, 1, 1, 1] + mkrun((1, 1), {'s': 1}, 0) + [1, 1, 1, 0, 0] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '<')),
        ('R4A', True,
         ('D', pl.norm_side([0, 1, 1] + mkrun((1, 1), {'s': 1}, 0) + [0, 0, 1, 0, 1] + mkrun((0, 1, 0, 1), {'k': 1}, 0) + [BLANK]), [1, BLANK], '>'),
         ('G', pl.norm_side([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0] + mkrun((1, 0, 1, 0), {'k': 1}, 0) + [BLANK]), pl.norm_side(mkrun((1, 1), {'s': 1}, 0) + [BLANK]), '>')),
        ('GLOOP', True,
         ('G', [0, V('X')], pl.norm_side([1, 1] + mkrun((1, 1), {'s': 1}, 0) + [BLANK]), '>'),
         ('G', [0, 1, 0, 1, 0, V('X')], pl.norm_side(mkrun((1, 1), {'s': 1}, 0) + [BLANK]), '>')),
        ('GHALT', False,
         ('G', pl.norm_side(mkrun((0, 1, 0, 1), {'s': 1}, 0) + [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0] + mkrun((1, 0, 1, 0), {'k': 1}, 0) + [BLANK]), [BLANK], '>'),
         ('C', pl.norm_side([1, 0, 0, 1] + mkrun((1, 0, 1, 0), {'k': 1}, 0) + [BLANK]), pl.norm_side([1, 1, 0, 0, 1, 1, 0, 0, 1] + mkrun((1, 0, 0, 1), {'s': 1}, 0) + [BLANK]), '>')),
        ('SROUND', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1,), {'n': 1}, 0) + [0, 0, 1, V('r')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 1, 1] + mkrun((1,), {'n': 1}, 0) + [1, 0, 0, V('r')]), '<')),
        ('INITA', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'k': 1}, 0) + [1, 0, 0, 0, 0, 0, 0, 1, BLANK]), '<'),
         ('G', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, BLANK], pl.norm_side(mkrun((1, 1), {'k': 1}, 0) + [BLANK]), '>')),
    ]

def get_3round_stages():
    return get_base_stages() + [
        ('MOD1_BASE', True,
         ('C', [1, 0, 0, 1, 1, 0, 1, 0, BLANK], [1, 1, 0, 0, 1, 1, 0, 0, 1, V('r')], '>'),
         ('E', [BLANK], [1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, V('r')], '<')),
        ('INIT109', True,
         ('C', [1, 0, 0, 1, 1, 0, 1, 0, 1, 0, V('X')], [1, 1, 0, 0, 1, 1, 0, 0, 1, V('r')], '>'),
         ('H', [1, 1, 0, 0, 1, V('X')], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, V('r')], '>')),
        ('REBUILD108', True,
         ('H', [1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, V('X')], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '>'),
         ('H', [1, 1, 0, 0, 1, V('X')], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, V('r')], '>')),
        ('EXIT_MOD1', True,
         ('H', [1, 1, 0, 0, 1, 1, 0, 1, 0, BLANK], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '>'),
         ('E', [BLANK], [1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, V('r')], '<')),
        ('EXIT_MOD2_A', True,
         ('H', [1, 1, 0, 0, 1, 1, 0, BLANK], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '>'),
         ('E', [BLANK], [1, 0, 0] + [1]*13 + [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '<')),
        ('EXIT_MOD2_B', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'k': 1}, 0) + [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1] + mkrun((1, 1), {'k': 1}, 0) + [0, 0, 1, 1, 1, 1, 0, 0, V('r')]), '<')),
        ('EXIT_MOD0_A', True,
         ('H', [1, 1, 0, 0, 1, BLANK], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '>'),
         ('E', [BLANK], [1] + [1]*8 + [0, 0, 0, 0] + [1]*11 + [0, 0, 1, 1, 1, 1, 0, 0, V('r')], '<')),
        ('ODD_FINAL', False,
         ('E', [BLANK], pl.norm_side([1, 1, 1, 1, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, 1, 0, 0, 1, 1, V('r')]), '<'),
         ('I', [0, 1, 1, 0, 0, 1, BLANK], pl.norm_side([1]*12 + mkrun((1, 1), {'b': 1}, 0) + [0, 0, V('r')]), '>')),
    ]

GLUE_3ROUND = r"""(** ** The digit-list family *)

Fixpoint rgt (ds : list nat) : side :=
  match ds with
  | [] => 1 >> const 0
  | d :: t => [1;1]^^d *> 0 >> 0 >> rgt t
  end.

(** Kd ds a b = 0^inf <E (1 (11)^b 00 (11)^a 00 (11)^d_1 00 ... (11)^d_n 00 1 0^inf), nearest digit first *)
Definition Kd (ds : list nat) (a b : nat) : Q * tape :=
  (const 0) <{{E}} (1 >> [1;1]^^b *> 0 >> 0 >> [1;1]^^a *> 0 >> 0 >> rgt ds).

Lemma rgt_zeros : forall k t, rgt (repeat 0%nat k ++ t) = [0;0]^^k *> rgt t.
Proof. induction k; intros. - reflexivity. - simpl. rewrite IHk. reflexivity. Qed.

Lemma rgt_ones : forall k t, rgt (repeat 1%nat k ++ t) = [1;1;0;0]^^k *> rgt t.
Proof. induction k; intros. - reflexivity. - simpl. rewrite IHk. reflexivity. Qed.

Lemma rgt_twos : forall k t, rgt (repeat 2%nat k ++ t) = [1;1;1;1;0;0]^^k *> rgt t.
Proof. induction k; intros. - reflexivity. - simpl. rewrite IHk. reflexivity. Qed.

Lemma rgt_ones_end : forall s, rgt (repeat 1%nat s) = 1 >> [1;0;0;1]^^s *> const 0.
Proof.
  induction s; simpl; [reflexivity |].
  rewrite IHs. reflexivity.
Qed.

Lemma repeat_snoc : forall (x : nat) n U, repeat x n ++ x :: U = repeat x (S n) ++ U.
Proof. induction n; intros; simpl. - reflexivity. - rewrite IHn. reflexivity. Qed.

(** ** The base K-level rules *)

Lemma KR1 : forall ds a b, Kd ds (S a) b -->+ Kd ds a (b + 3).
Proof.
  intros. unfold Kd. replace (b + 3) with (3 + b) by lia.
  eapply progress_evstep_trans; [apply R1 |].
  finish_norm.
Qed.

Lemma KR2 : forall y t b, Kd (S y :: t) 0 b -->+ Kd (y :: t) (b + 3) 0.
Proof.
  intros. unfold Kd. simpl rgt. replace (b + 3) with (3 + b) by lia.
  eapply progress_evstep_trans; [apply R2 |].
  finish_norm.
Qed.

Lemma blocks0101_snoc : forall i Y,
  [0;1;0;1]^^i *> 0 >> 1 >> 0 >> 1 >> Y = [0;1;0;1]^^(S i) *> Y.
Proof.
  intros. change (0 >> 1 >> 0 >> 1 >> Y) with ([0;1;0;1] *> Y).
  rewrite lpow_shift'. reflexivity.
Qed.

Lemma LOOPS : forall i s X r,
  (0 >> 1 >> 1 >> [1;1]^^(i + s) *> 0 >> X) {{D}}> ([0;0]^^i *> r) -->*
  (0 >> 1 >> 1 >> [1;1]^^s *> 0 >> [0;1;0;1]^^i *> X) {{D}}> r.
Proof.
  induction i; intros.
  - finish.
  - simpl lpow.
    eapply evstep_trans; [apply progress_evstep, LOOP |].
    follow (IHi s (0 >> 1 >> 0 >> 1 >> X) r).
    apply evstep_refl'. rewrite blocks0101_snoc. reflexivity.
Qed.

Lemma KR3 : forall m s y t,
  Kd (repeat 0%nat (S m) ++ S y :: t) 0 (S m + s) -->+
  Kd (repeat 1%nat m ++ S (S (S s)) :: y :: t) 1 0.
Proof.
  intros m s y t. unfold Kd. rewrite rgt_zeros. simpl rgt.
  eapply progress_evstep_trans; [apply ENTRY |].
  follow (LOOPS (S m) s (0 >> 1 >> 0 >> 1 >> const 0) (1 >> 1 >> [1;1]^^y *> 0 >> 0 >> rgt t)).
  rewrite blocks0101_snoc. simpl lpow.
  apply progress_evstep.
  eapply progress_evstep_trans; [apply FINAL |].
  rewrite rgt_ones. simpl rgt. finish_norm.
Qed.

Lemma GLOOPS : forall s X,
  (0 >> X) {{G}}> ([1;1]^^s *> const 0) -->*
  ([0;1;0;1]^^s *> 0 >> X) {{G}}> const 0.
Proof.
  induction s; intros.
  - finish.
  - simpl lpow.
    eapply evstep_trans; [apply progress_evstep, GLOOP |].
    follow (IHs (1 >> 0 >> 1 >> 0 >> X)).
    finish_norm.
Qed.

Definition c_end (k s : nat) : Q * tape :=
  (1 >> 0 >> 0 >> 1 >> [1;0;1;0]^^k *> const 0) {{C}}>
  (1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).

Lemma KR4x : forall k s,
  Kd (repeat 0%nat k) 0 (k + s) -->* c_end k s.
Proof.
  intros k s. unfold Kd.
  rewrite <- (app_nil_r (repeat 0%nat k)), rgt_zeros. simpl rgt.
  apply progress_evstep.
  eapply progress_evstep_trans; [apply ENTRY |].
  follow (LOOPS k s (0 >> 1 >> 0 >> 1 >> const 0) (1 >> const 0)).
  rewrite blocks0101_snoc. simpl lpow.
  apply progress_evstep.
  eapply progress_evstep_trans; [apply R4A |].
  follow (GLOOPS s (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> 0 >> [1;0;1;0]^^k *> const 0)).
  apply GHALT.
Qed.

(** ** Accelerated blank-tape start to Kd (repeat 1 20) 1 2 *)

Lemma SROUNDS : forall m n r,
  (const 0) <{{E}} (1 >> [1]^^n *> 0 >> 0 >> [1]^^m *> r) -->*
  (const 0) <{{E}} (1 >> [1]^^(3 * m + n) *> 0 >> 0 >> r).
Proof.
  induction m; intros.
  - finish.
  - change ([1]^^(S m) *> r) with (1 >> [1]^^m *> r).
    eapply evstep_trans; [apply progress_evstep, SROUND |].
    replace (1 >> 1 >> 1 >> [1]^^n *> 1 >> 0 >> 0 >> [1]^^m *> r)
      with (1 >> [1]^^(3 + n) *> 0 >> 0 >> [1]^^m *> r) by (align_tape; reflexivity).
    eapply evstep_trans; [apply (IHm (3 + n) r) |].
    replace (3 * m + (3 + n)) with (3 * S m + n) by lia. finish.
Qed.

Lemma init_reach : c0 -->* Kd (repeat 1%nat 20) 1 2.
Proof.
  assert (H1 : c0 -->* (const 0) <{{E}} (1 >> [1]^^0 *> 0 >> 0 >> [1]^^13 *> 0 >> 0 >> 0 >> 0 >> 1 >> const 0)).
  { unfold c0. do 310 step. finish. }
  follow H1.
  follow (SROUNDS 13 0 (0 >> 0 >> 0 >> 0 >> 1 >> const 0)).
  change (1 >> [1]^^(3 * 13 + 0) *> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> const 0)
    with (1 >> [1;1]^^19 *> 1 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> const 0).
  eapply evstep_trans; [apply progress_evstep, (INITA 19) |].
  follow (GLOOPS 19 (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> 0 >> 1 >> 0 >> 1 >> const 0)).
  unfold Kd. do 194 step. finish.
Qed.

(** ** Modulo-3 Rebuild and Halting Lemmas from c_end k s *)

Lemma lpow_1010_shift2 : forall n X,
  (1 >> 0 >> [1;0;1;0]^^n *> X : side) = [1;0;1;0]^^n *> 1 >> 0 >> X.
Proof.
  induction n; intros; simpl; [reflexivity | rewrite IHn; reflexivity].
Qed.

Lemma blocks111100_snoc : forall i Y,
  [1;1;1;1;0;0]^^i *> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> Y = [1;1;1;1;0;0]^^(S i) *> Y.
Proof.
  intros. change (1 >> 1 >> 1 >> 1 >> 0 >> 0 >> Y) with ([1;1;1;1;0;0] *> Y).
  rewrite lpow_shift'. reflexivity.
Qed.

Lemma REBUILD3_LOOPS : forall m X r,
  (1 >> 1 >> 0 >> 0 >> 1 >> [1;0;1;0]^^(3 * m) *> X) {{H}}>
  (1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> r) -->*
  (1 >> 1 >> 0 >> 0 >> 1 >> X) {{H}}>
  (1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> [1;1;1;1;0;0]^^(2 * m) *> r).
Proof.
  induction m as [| m IHm]; intros X r.
  - finish.
  - replace (3 * S m) with (S (S (S (3 * m)))) by lia. simpl lpow.
    eapply evstep_trans; [apply progress_evstep, REBUILD108 |].
    eapply evstep_trans; [apply progress_evstep, REBUILD108 |].
    follow (IHm X (1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> r)).
    rewrite !blocks111100_snoc.
    replace (S (S (2 * m))) with (2 * S m) by lia. finish.
Qed.

Lemma R1iter : forall a ds b, Kd ds a b -->* Kd ds 0 (b + 3 * a).
Proof.
  induction a; intros.
  - replace (b + 3 * 0) with b by lia. finish.
  - eapply evstep_trans; [apply progress_evstep, KR1 |].
    follow (IHa ds (b + 3)).
    replace (b + 3 * S a) with (b + 3 + 3 * a) by lia. finish.
Qed.

(** Rebuild for k = 2 + 3 * m (k == 2 mod 3, including Round 1 where k_1 = 20 = 2 + 3 * 6): *)
Lemma KR_mod2 : forall m s,
  c_end (2 + 3 * m) s -->*
  Kd (22%nat :: repeat 2%nat (2 * m + 1) ++ 0%nat :: repeat 1%nat s) 0 5.
Proof.
  intros m s. unfold c_end.
  replace (2 + 3 * m) with (S (S (3 * m))) by lia.
  simpl lpow; simpl app; simpl Str_app.
  eapply evstep_trans; [apply progress_evstep, INIT109 |].
  rewrite lpow_1010_shift2.
  follow (REBUILD3_LOOPS m (1 >> 0 >> const 0) (0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)).
  eapply evstep_trans; [apply progress_evstep, EXIT_MOD2_A |].
  change (1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >>
          0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)
    with (1 >> [1]^^0 *> 0 >> 0 >> [1]^^13 *> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).
  follow (SROUNDS 13 0 (0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)).
  change (1 >> [1]^^(3 * 13 + 0) *> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)
    with (1 >> [1;1]^^19 *> 1 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).
  eapply evstep_trans; [apply progress_evstep, (EXIT_MOD2_B 19) |].
  assert (Hk :
    (const 0) <{{E}} (1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 0 >> 0 >>
      1 >> 1 >> 1 >> 1 >> 1 >> 1 >> [1;1]^^19 *> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
      [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0) =
    Kd (22%nat :: repeat 2%nat (2 * m + 1) ++ 0%nat :: repeat 1%nat s) 1 2).
  { unfold Kd. replace (2 * m + 1) with (S (2 * m)) by lia.
    simpl repeat. simpl app. simpl rgt.
    rewrite rgt_twos. simpl rgt. rewrite rgt_ones_end. reflexivity. }
  rewrite Hk.
  eapply evstep_trans; [apply progress_evstep, KR1 |].
  finish.
Qed.

(** Rebuild for k = 1 + 3 * m (k == 1 mod 3, including Round 2 where k_2 = 1 + 3 * m_2): *)
Lemma KR_mod1 : forall m s,
  c_end (1 + 3 * m) s -->*
  Kd (3%nat :: repeat 2%nat (2 * m) ++ 0%nat :: repeat 1%nat s) 0 3.
Proof.
  intros [| m'] s.
  - unfold c_end. simpl plus. simpl lpow.
    eapply evstep_trans; [apply progress_evstep, MOD1_BASE |].
    assert (Hk :
      (const 0) <{{E}} (1 >> 0 >> 0 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >>
        0 >> 0 >> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0) =
      Kd (3%nat :: repeat 2%nat 0 ++ 0%nat :: repeat 1%nat s) 1 0).
    { unfold Kd. simpl. rewrite rgt_ones_end. reflexivity. }
    rewrite Hk.
    eapply evstep_trans; [apply progress_evstep, KR1 |].
    finish.
  - unfold c_end.
    replace (1 + 3 * S m') with (S (S (3 * m' + 2))) by lia.
    simpl lpow; simpl app; simpl Str_app.
    eapply evstep_trans; [apply progress_evstep, INIT109 |].
    rewrite lpow_1010_shift2, <- lpow_merge.
    change ([1;0;1;0]^^2 *> 1 >> 0 >> const 0)
      with (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> const 0).
    follow (REBUILD3_LOOPS m' (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> const 0) (0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)).
    eapply evstep_trans; [apply progress_evstep, REBUILD108 |].
    eapply evstep_trans; [apply progress_evstep, EXIT_MOD1 |].
    assert (Hk :
      (const 0) <{{E}} (1 >> 0 >> 0 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >>
        0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
        [1;1;1;1;0;0]^^(2 * m') *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0) =
      Kd (3%nat :: repeat 2%nat (2 * S m') ++ 0%nat :: repeat 1%nat s) 1 0).
    { unfold Kd. replace (2 * S m') with (S (S (2 * m'))) by lia.
      simpl repeat. simpl app. simpl rgt.
      rewrite rgt_twos. simpl rgt. rewrite rgt_ones_end. reflexivity. }
    rewrite Hk.
    eapply evstep_trans; [apply progress_evstep, KR1 |].
    finish.
Qed.

(** General R1/R2 helper for the 5-stage halting cascade at k = 3 + 3 * m: *)
Lemma R1_gen_step : forall a b r,
  (const 0) <{{E}} (1 >> [1;1]^^b *> 0 >> 0 >> [1;1]^^(S a) *> 0 >> 0 >> r) -->+
  (const 0) <{{E}} (1 >> [1;1]^^(b + 3) *> 0 >> 0 >> [1;1]^^a *> 0 >> 0 >> r).
Proof.
  intros. replace (b + 3) with (3 + b) by lia.
  eapply progress_evstep_trans; [apply R1 |]. finish_norm.
Qed.

Lemma R1_gen_iter : forall a b r,
  (const 0) <{{E}} (1 >> [1;1]^^b *> 0 >> 0 >> [1;1]^^a *> 0 >> 0 >> r) -->*
  (const 0) <{{E}} (1 >> [1;1]^^(b + 3 * a) *> 0 >> 0 >> 0 >> 0 >> r).
Proof.
  induction a; intros b r.
  - replace (b + 3 * 0) with b by lia. finish.
  - eapply evstep_trans; [apply progress_evstep, R1_gen_step |].
    follow (IHa (b + 3) r).
    replace (b + 3 * S a) with (b + 3 + 3 * a) by lia. finish.
Qed.

Lemma D_step_gen : forall b r,
  (const 0) <{{E}} (1 >> [1;1]^^b *> 0 >> 0 >> 0 >> 0 >> 1 >> 1 >> r) -->*
  (const 0) <{{E}} (1 >> [1;1]^^(3 * b + 9) *> 0 >> 0 >> 0 >> 0 >> r).
Proof.
  intros b r.
  eapply evstep_trans; [apply progress_evstep, R2_gen |].
  replace (3 * b + 9)%nat with (0 + 3 * (3 + b))%nat by lia.
  eapply evstep_trans; [| apply (R1_gen_iter (3 + b) 0 r)].
  finish_norm.
Qed.

Definition c_halt3 (m s : nat) : Q * tape :=
  (0 >> 1 >> 1 >> 0 >> 0 >> 1 >> const 0) {{I}}>
  (1 >> 1 >> [1;1]^^2063 *> 0 >> 0 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
   [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).

Lemma c_halt3_halted : forall m s, halted tm (c_halt3 m s).
Proof. intros. unfold c_halt3. simpl. reflexivity. Qed.

(** Halting for k = 3 + 3 * m (k == 0 mod 3, including Round 3 where k_3 = 3 + 3 * m_3): *)
Lemma KR_mod0_halt : forall m s,
  c_end (3 + 3 * m) s -->* c_halt3 m s.
Proof.
  intros m s. unfold c_end.
  replace (3 + 3 * m) with (S (S (3 * m + 1))) by lia.
  simpl lpow; simpl app; simpl Str_app.
  eapply evstep_trans; [apply progress_evstep, INIT109 |].
  rewrite lpow_1010_shift2, <- lpow_merge.
  change ([1;0;1;0]^^1 *> 1 >> 0 >> const 0)
    with (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> const 0).
  follow (REBUILD3_LOOPS m (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> const 0) (0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)).
  eapply evstep_trans; [apply progress_evstep, REBUILD108 |].
  eapply evstep_trans; [apply progress_evstep, EXIT_MOD0_A |].
  set (tail := 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
               [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).
  change (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;0;0]^^(2 * m) *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)
    with (1 >> [1;1]^^4 *> 0 >> 0 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >>
          0 >> 0 >> 1 >> 1 >> tail).
  follow (D_step_gen 4 (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (3 * 4 + 9)%nat with 21%nat.
  follow (D_step_gen 21 (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (3 * 21 + 9)%nat with 72%nat.
  follow (D_step_gen 72 (1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (3 * 72 + 9)%nat with 225%nat.
  follow (D_step_gen 225 (1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (3 * 225 + 9)%nat with 684%nat.
  follow (D_step_gen 684 (1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (1 >> [1;1]^^(3 * 684 + 9) *> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)
    with (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> [1;1]^^2058 *> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail).
  eapply evstep_trans; [apply (ODD_FINAL 2058 tail) |].
  unfold c_halt3, tail. finish.
Qed.

(** ** Exact clearing functions and multi-round divisibility by 9 *)

Local Open Scope nat_scope.

Fixpoint iter (n : nat) (g : nat -> nat) (x : nat) : nat :=
  match n with
  | O => x
  | S n' => g (iter n' g x)
  end.

Lemma iter_S' : forall n g x, iter (S n) g x = iter n g (g x).
Proof. induction n; intros; simpl. - reflexivity. - rewrite <- IHn. reflexivity. Qed.

Lemma iter_lin : forall g, (forall a, a + 1 <= g a) -> forall n x, x + n <= iter n g x.
Proof.
  intros g Hg. induction n; intros; simpl. - lia.
  - specialize (IHn x). specialize (Hg (iter n g x)). lia.
Qed.

Fixpoint UX (j : nat) : (nat -> nat) * nat :=
  match j with
  | O => (fun x => 3 * x + 9, 3)
  | S i => (fun x => iter (x - i + 2) (fst (UX i)) (snd (UX i)),
            fst (UX i) (snd (UX i)))
  end.

Definition U (j : nat) : nat -> nat := fst (UX j).
Definition X (j : nat) : nat := snd (UX j).

Lemma U_0 : forall x, U 0 x = 3 * x + 9.
Proof. reflexivity. Qed.

Lemma U_S : forall j x, U (S j) x = iter (x - j + 2) (U j) (X j).
Proof. reflexivity. Qed.

Lemma X_0 : X 0 = 3.
Proof. reflexivity. Qed.

Lemma X_S : forall j, X (S j) = U j (X j).
Proof. reflexivity. Qed.

Opaque U X.

Lemma UX_grow : forall j, (forall x, x + 9 <= U j x) /\ (j + 3 <= X j).
Proof.
  induction j as [| i [IHu IHx]].
  - split; [intro x; rewrite U_0; lia | rewrite X_0; lia].
  - split.
    + intro x. rewrite U_S.
      assert (Hstep : forall a, a + 9 <= U i a) by exact IHu.
      assert (Hiter : forall n y, y + 9 * n <= iter n (U i) y).
      { induction n; intros y; simpl; [lia | specialize (IHn y); specialize (Hstep (iter n (U i) y)); lia]. }
      pose proof (Hiter (x - i + 2) (X i)). lia.
    + rewrite X_S. specialize (IHu (X i)). lia.
Qed.

Lemma Ugrow : forall j x, x + 9 <= U j x.
Proof. intro j. apply UX_grow. Qed.

Lemma Xgrow : forall j, j + 3 <= X j.
Proof. intro j. apply UX_grow. Qed.

Lemma CHx : forall v Us B, Kd (v :: Us) 0 B -->* Kd (0%nat :: Us) 0 (iter v (U 0) B).
Proof.
  induction v; intros Us B.
  - apply evstep_refl.
  - eapply evstep_trans; [apply progress_evstep, KR2 |].
    eapply evstep_trans; [apply R1iter |].
    rewrite iter_S', U_0.
    replace (0 + 3 * (B + 3)) with (3 * B + 9) by lia.
    apply IHv.
Qed.

Definition CDPx (j : nat) : Prop :=
  forall v Us B, j <= B ->
    Kd (repeat 0%nat j ++ v :: Us) 0 B -->* Kd (repeat 0%nat (S j) ++ Us) 0 (iter v (U j) B).

Fixpoint Yb (t n x : nat) : nat :=
  match n with
  | O => x
  | S n' => U (t + n') (Yb t n' x)
  end.

Lemma Yb_X : forall j, Yb 0 j 3 = X j.
Proof. induction j. - reflexivity. - simpl Yb. rewrite IHj, X_S. reflexivity. Qed.

Lemma Yb_ge : forall t n x, t <= x -> t + n <= Yb t n x.
Proof.
  intros t n x Hx. induction n as [| n' IHn]. - simpl. lia.
  - simpl Yb. pose proof (Ugrow (t + n') (Yb t n' x)). lia.
Qed.

Lemma BLKx : forall D, (forall j', j' < D -> CDPx j') ->
  forall n t V x, t + n <= D -> t <= x ->
  Kd (repeat 0%nat t ++ repeat 1%nat n ++ V) 0 x -->* Kd (repeat 0%nat (t + n) ++ V) 0 (Yb t n x).
Proof.
  intros D HD. induction n as [| n IHn]; intros t V x Hd Hx.
  - replace (t + 0) with t by lia. apply evstep_refl.
  - rewrite <- repeat_snoc.
    follow (IHn t (1%nat :: V) x ltac:(lia) Hx).
    follow (HD (t + n) ltac:(lia) 1%nat V (Yb t n x) (Yb_ge t n x Hx)).
    replace (t + S n) with (S (t + n)) by lia. apply evstep_refl.
Qed.

From Coq Require Import Wf_nat.

Lemma CDPx_all : forall j, CDPx j.
Proof.
  intro j. induction j as [j IH] using lt_wf_ind.
  destruct j as [| n].
  - intros v Us B _. simpl. apply CHx.
  - intro v. induction v as [| w IHw]; intros Us B HB.
    + rewrite repeat_snoc. apply evstep_refl.
    + remember (B - S n) as s eqn:Hs.
      assert (HB' : B = S n + s) by lia.
      assert (Hr : Kd (repeat 0%nat (S n) ++ S w :: Us) 0 B -->*
                   Kd (repeat 1%nat n ++ S (S (S s)) :: w :: Us) 0 3).
      { rewrite HB'. eapply evstep_trans; [apply progress_evstep, KR3 |].
        follow (R1iter 1 (repeat 1%nat n ++ S (S (S s)) :: w :: Us) 0). finish. }
      follow Hr.
      follow (BLKx (S n) IH n 0 (S (S (S s)) :: w :: Us) 3 ltac:(lia) ltac:(lia)).
      rewrite Yb_X.
      follow (IH n ltac:(lia) (S (S (S s))) (w :: Us) (X n) ltac:(pose proof (Xgrow n); lia)).
      replace (iter (S (S (S s))) (U n) (X n)) with (U (S n) B)
        by (rewrite U_S; f_equal; lia).
      follow (IHw Us (U (S n) B) ltac:(pose proof (Ugrow (S n) B); lia)).
      rewrite iter_S'. apply evstep_refl.
Qed.

(** General constant-digit block clearing for repeat (S d) n: *)
Fixpoint Yb_d (d t n x : nat) : nat :=
  match n with
  | O => x
  | S n' => iter (S d) (U (t + n')) (Yb_d d t n' x)
  end.

Lemma iter_U_grow : forall d j x, x + 9 <= iter (S d) (U j) x.
Proof.
  induction d as [| d IHd]; intros j x.
  - simpl iter. apply Ugrow.
  - change (iter (S (S d)) (U j) x) with (U j (iter (S d) (U j) x)).
    pose proof (IHd j x). pose proof (Ugrow j (iter (S d) (U j) x)). lia.
Qed.

Lemma Yb_d_add : forall d n t x, x + 9 * n <= Yb_d d t n x.
Proof.
  intros d n. induction n as [| n' IHn]; intros t x.
  - simpl. lia.
  - change (Yb_d d t (S n') x) with (iter (S d) (U (t + n')) (Yb_d d t n' x)).
    pose proof (IHn t x).
    pose proof (iter_U_grow d (t + n') (Yb_d d t n' x)).
    lia.
Qed.

Lemma Yb_d_ge : forall d t n x, t <= x -> t + 9 * n <= Yb_d d t n x.
Proof.
  intros d t n x Hx. pose proof (Yb_d_add d n t x). lia.
Qed.

Lemma BLKd : forall d n t V x, t <= x ->
  Kd (repeat 0%nat t ++ repeat (S d) n ++ V) 0 x -->*
  Kd (repeat 0%nat (t + n) ++ V) 0 (Yb_d d t n x).
Proof.
  intro d. induction n as [| n IHn]; intros t V x Hx.
  - replace (t + 0) with t by lia. apply evstep_refl.
  - rewrite <- repeat_snoc.
    follow (IHn t (S d :: V) x Hx).
    pose proof (Yb_d_ge d t n x Hx) as Hge.
    follow (CDPx_all (t + n) (S d) V (Yb_d d t n x) ltac:(lia)).
    replace (t + S n) with (S (t + n)) by lia. apply evstep_refl.
Qed.

(** Clearing a full round list: (S v) :: repeat 2 p ++ 0 :: repeat 1 s *)
Definition clear_round (v p s b : nat) : nat :=
  Yb_d 0 (2 + p) s (Yb_d 1 1 p (iter (S v) (U 0) b)).

Lemma clear_round_ge : forall v p s b,
  b + 9 + 9 * p + 9 * s <= clear_round v p s b.
Proof.
  intros v p s b. unfold clear_round.
  pose proof (iter_U_grow v 0 b).
  pose proof (Yb_d_add 1 p 1 (iter (S v) (U 0) b)).
  pose proof (Yb_d_add 0 s (2 + p) (Yb_d 1 1 p (iter (S v) (U 0) b))).
  lia.
Qed.

Lemma clear_round_reach : forall v p s b,
  Kd (S v :: repeat 2%nat p ++ 0%nat :: repeat 1%nat s) 0 b -->*
  Kd (repeat 0%nat (2 + p + s)) 0 (clear_round v p s b).
Proof.
  intros v p s b. unfold clear_round.
  change (S v :: repeat 2%nat p ++ 0%nat :: repeat 1%nat s)
    with (repeat 0%nat 0 ++ S v :: (repeat 2%nat p ++ 0%nat :: repeat 1%nat s)).
  follow (CDPx_all 0 (S v) (repeat 2%nat p ++ 0%nat :: repeat 1%nat s) b ltac:(lia)).
  pose proof (iter_U_grow v 0 b) as H1.
  follow (BLKd 1 p 1 (0%nat :: repeat 1%nat s) (iter (S v) (U 0) b) ltac:(lia)).
  rewrite repeat_snoc.
  change (1 + p) with (S p).
  change (S (S p)) with (2 + p).
  rewrite <- (app_nil_r (repeat 1%nat s)).
  pose proof (Yb_d_add 1 p 1 (iter (S v) (U 0) b)) as H2.
  follow (BLKd 0 s (2 + p) [] (Yb_d 1 1 p (iter (S v) (U 0) b)) ltac:(lia)).
  rewrite app_nil_r. apply evstep_refl.
Qed.

(** Divisibility by 3 and 9 of U and X: *)
Lemma UX_div3 : forall j, (forall x, exists q, U j x = 3 * q) /\ (exists q, X j = 3 * q).
Proof.
  induction j as [| j [Hu Hx]].
  - split; [intros x; exists (x + 3); rewrite U_0; lia | exists 1; rewrite X_0; lia].
  - split.
    + intros x. rewrite U_S.
      destruct (x - j + 2) as [| m]; [exact Hx | simpl iter; apply Hu].
    + rewrite X_S. apply Hu.
Qed.

Lemma U0_div9 : forall q, exists r, U 0 (3 * q) = 9 * r.
Proof. intros q. exists (q + 1). rewrite U_0. lia. Qed.

Lemma UX_S_div9 : forall j,
  (forall x, exists r, U (S j) x = 9 * r) /\ (exists r, X (S j) = 9 * r).
Proof.
  induction j as [| j [Hu Hx]].
  - split.
    + intros x. rewrite U_S, X_0.
      replace (x - 0 + 2) with (S (S x)) by lia. simpl iter.
      destruct (proj1 (UX_div3 0) (iter x (U 0) 3)) as [q Hq].
      rewrite Hq. apply U0_div9.
    + rewrite X_S, X_0. exists 2. rewrite U_0. reflexivity.
  - split.
    + intros x. rewrite U_S.
      destruct (x - S j + 2) as [| m]; [exact Hx | simpl iter; apply Hu].
    + rewrite X_S. apply Hu.
Qed.

Lemma clear_round_div9 : forall v p s' b,
  exists r, clear_round v p (S s') b = 9 * r.
Proof.
  intros v p s' b. unfold clear_round. simpl Yb_d.
  replace (2 + p + s') with (S (1 + p + s')) by lia.
  apply (proj1 (UX_S_div9 (1 + p + s'))).
Qed.

(** ** The 3-Round Halting Trajectory from the Blank Tape *)

Definition bf1 : nat := Yb 0 20 5.

Lemma bf1_def : bf1 = Yb 0 20 5.
Proof. reflexivity. Qed.

Opaque bf1.

Lemma bf1_ge_27 : 27 <= bf1.
Proof.
  rewrite bf1_def.
  change (Yb 0 20 5) with (U 19 (Yb 0 19 5)).
  pose proof (Yb_ge 0 19 5 ltac:(lia)).
  pose proof (Ugrow 19 (Yb 0 19 5)). lia.
Qed.

Lemma bf1_div9 : exists q1, bf1 = 9 * q1.
Proof.
  rewrite bf1_def. simpl Yb. apply (proj1 (UX_S_div9 18)).
Qed.

Lemma run_round1 : c0 -->* Kd (repeat 0%nat 20) 0 bf1.
Proof.
  follow init_reach.
  follow (R1iter 1 (repeat 1%nat 20) 2).
  change (2 + 3 * 1) with 5.
  change (repeat 1%nat 20) with (repeat 0%nat 0 ++ repeat 1%nat 20 ++ []).
  follow (BLKx 20 (fun j' _ => CDPx_all j') 20 0 [] 5 ltac:(lia) ltac:(lia)).
  rewrite app_nil_r, bf1_def. apply evstep_refl.
Qed.

Definition s1 : nat := bf1 - 20.
Definition bf2 : nat := clear_round 21 13 s1 5.

Lemma bf2_def : bf2 = clear_round 21 13 s1 5.
Proof. reflexivity. Qed.

Opaque bf2.

Lemma bf2_div9 : exists q2, bf2 = 9 * q2.
Proof.
  pose proof bf1_ge_27 as Hbf1.
  rewrite bf2_def. unfold s1.
  replace (bf1 - 20) with (S (bf1 - 21)) by lia.
  apply clear_round_div9.
Qed.

Lemma bf2_gt_k2 : 15 + s1 + 1 <= bf2.
Proof.
  rewrite bf2_def. pose proof (clear_round_ge 21 13 s1 5). lia.
Qed.

Definition m2 : nat := (bf1 - 6) / 3.
Definition s2 : nat := bf2 - (15 + s1).
Definition bf3 : nat := clear_round 2 (2 * m2) s2 3.

Lemma bf3_def : bf3 = clear_round 2 (2 * m2) s2 3.
Proof. reflexivity. Qed.

Opaque bf3.

Lemma bf3_gt_k3 : 2 + 2 * m2 + s2 + 1 <= bf3.
Proof.
  rewrite bf3_def. pose proof (clear_round_ge 2 (2 * m2) s2 3). lia.
Qed.

Definition m3 : nat := (2 + 2 * m2 + s2 - 3) / 3.
Definition s3 : nat := bf3 - (2 + 2 * m2 + s2).

Lemma round2_reach :
  Kd (22%nat :: repeat 2%nat 13 ++ 0%nat :: repeat 1%nat s1) 0 5 -->*
  Kd (repeat 0%nat (2 + 13 + s1)) 0 bf2.
Proof.
  rewrite bf2_def. exact (clear_round_reach 21 13 s1 5).
Qed.

Lemma round3_reach :
  Kd (3%nat :: repeat 2%nat (2 * m2) ++ 0%nat :: repeat 1%nat s2) 0 3 -->*
  Kd (repeat 0%nat (2 + 2 * m2 + s2)) 0 bf3.
Proof.
  rewrite bf3_def. exact (clear_round_reach 2 (2 * m2) s2 3).
Qed.

Lemma round_arith_gen : forall b1 b2 b3 q1 q2,
  27 <= b1 ->
  b1 = 9 * q1 ->
  15 + (b1 - 20) + 1 <= b2 ->
  b2 = 9 * q2 ->
  2 + 2 * ((b1 - 6) / 3) + (b2 - (15 + (b1 - 20))) + 1 <= b3 ->
  let s1_v := b1 - 20 in
  let m2_v := (b1 - 6) / 3 in
  let s2_v := b2 - (15 + s1_v) in
  let m3_v := (2 + 2 * m2_v + s2_v - 3) / 3 in
  let s3_v := b3 - (2 + 2 * m2_v + s2_v) in
  20 + s1_v = b1 /\
  2 + 13 + s1_v = 1 + 3 * m2_v /\
  (1 + 3 * m2_v) + s2_v = b2 /\
  2 + 2 * m2_v + s2_v = 3 + 3 * m3_v /\
  (3 + 3 * m3_v) + s3_v = b3.
Proof.
  intros b1 b2 b3 q1 q2 Hbf1 Hq1 Hbf2 Hq2 Hbf3 s1_v m2_v s2_v m3_v s3_v.
  assert (Hm2 : m2_v = 3 * q1 - 2).
  { unfold m2_v. rewrite Hq1.
    replace (9 * q1 - 6) with ((3 * q1 - 2) * 3) by lia.
    rewrite Nat.div_mul; lia. }
  assert (Hm3 : m3_v = 3 * q2 - q1).
  { unfold m3_v, s2_v, s1_v. rewrite Hm2, Hq1, Hq2.
    replace (2 + 2 * (3 * q1 - 2) + (9 * q2 - (15 + (9 * q1 - 20))) - 3)
      with ((3 * q2 - q1) * 3) by lia.
    rewrite Nat.div_mul; lia. }
  unfold s3_v, s2_v, s1_v in *.
  repeat split; lia.
Qed.

Lemma run_3rounds_gen : forall b1 s1_v b2 m2_v s2_v b3 m3_v s3_v,
  20 + s1_v = b1 ->
  2 + 13 + s1_v = 1 + 3 * m2_v ->
  (1 + 3 * m2_v) + s2_v = b2 ->
  2 + 2 * m2_v + s2_v = 3 + 3 * m3_v ->
  (3 + 3 * m3_v) + s3_v = b3 ->
  c0 -->* Kd (repeat 0%nat 20) 0 b1 ->
  Kd (22%nat :: repeat 2%nat 13 ++ 0%nat :: repeat 1%nat s1_v) 0 5 -->*
    Kd (repeat 0%nat (2 + 13 + s1_v)) 0 b2 ->
  Kd (3%nat :: repeat 2%nat (2 * m2_v) ++ 0%nat :: repeat 1%nat s2_v) 0 3 -->*
    Kd (repeat 0%nat (2 + 2 * m2_v + s2_v)) 0 b3 ->
  c0 -->* c_halt3 m3_v s3_v.
Proof.
  intros b1 s1_v b2 m2_v s2_v b3 m3_v s3_v
         Hs1 Hk2 Hs2 Hk3 Hs3 Hr1 Hr2 Hr3.
  follow Hr1.
  rewrite <- Hs1.
  follow (KR4x 20 s1_v).
  change 20 with (2 + 3 * 6).
  follow (KR_mod2 6 s1_v).
  change (2 * 6 + 1) with 13.
  follow Hr2.
  rewrite Hk2, <- Hs2.
  follow (KR4x (1 + 3 * m2_v) s2_v).
  follow (KR_mod1 m2_v s2_v).
  follow Hr3.
  rewrite Hk3, <- Hs3.
  follow (KR4x (3 + 3 * m3_v) s3_v).
  apply KR_mod0_halt.
Qed.

Theorem run_to_halt3 : c0 -->* c_halt3 m3 s3.
Proof.
  destruct bf1_div9 as [q1 Hq1].
  destruct bf2_div9 as [q2 Hq2].
  destruct (round_arith_gen bf1 bf2 bf3 q1 q2
              bf1_ge_27 Hq1 bf2_gt_k2 Hq2 bf3_gt_k3)
    as [Hs1 [Hk2 [Hs2 [Hk3 Hs3]]]].
  exact (run_3rounds_gen bf1 s1 bf2 m2 s2 bf3 m3 s3
           Hs1 Hk2 Hs2 Hk3 Hs3
           run_round1 round2_reach round3_reach).
Qed.

Theorem halt : halts tm c0.
Proof.
  destruct (with_counter run_to_halt3) as [n Hn].
  eapply halts_multistep; [| exact Hn].
  apply halted_halts. apply c_halt3_halted.
Qed.
"""

def gen_3round():
    pl.set_tm(M_3ROUND)
    pl.LEMMAS.clear()
    stage_texts = []
    for nm, prog, s, t in get_3round_stages():
        ops, end, how = engine.run_until_stuck(s, pl.canon(t), target=t)
        assert (how == 'target' or not prog) and engine.equiv(end, t), (nm, how)
        stage_texts.append(coqgen.stage_lemma(nm, s, ops, t, progress=prog).replace('repeat rewrite (align_lpow', 'rewrite (align_lpow'))
    head = open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof\header.v.in').read()
    title = 'The 9-state 3-round champion extension 1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RA0RI_0LG--- halts'
    head = head.replace('@TITLE@', title).replace('@N@', '9').replace('@TM@', M_3ROUND).replace('@TABLE@', coqgen_util.table(M_3ROUND))
    text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
         + '\n(** ** Phase lemmas (generated) *)\n\n' + '\n'.join(stage_texts) + '\n' + GLUE_3ROUND
    out_path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs\BB9_champ20_3round.v'
    open(out_path, 'w', newline='\n').write(text)
    print("Wrote", out_path, len(text))

if __name__ == '__main__':
    gen_3round()
