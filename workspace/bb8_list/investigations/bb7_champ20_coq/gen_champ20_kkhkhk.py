"""Generate complete, axiom-free Coq halting proof for KKHKHK_231_144:
   BB9_champ20_kkhkhk.v:
   1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---
   Proves both:
     - KR_even_halt (for all even k = 4 + 2m, including Round 1 k_1 = 20 = 4 + 2*8)
     - KR_odd_halt  (for all odd  k = 3 + 2m)
     - Theorem halt : halts tm c0
"""
import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util
from gen_champ20_3round import get_base_stages, M_KKHKHK

def get_kkhkhk_stages():
    return get_base_stages() + [
        ('INIT173', True,
         ('C', [1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, V('X')], [1, 1, 0, 0, 1, 1, 0, 0, 1, V('r')], '>'),
         ('F', [V('X')], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, V('r')], '<')),
        ('REBUILD164', True,
         ('F', [1, 0, 1, 0, 1, 0, 1, 0, V('X')], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '<'),
         ('F', [V('X')], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '<')),
        ('EXIT_EVEN_A', True,
         ('F', [BLANK], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '<'),
         ('E', [BLANK], [1]*9 + [0]*4 + [1]*11 + [0, 0] + [1]*6 + [0, 0] + [1]*6 + [0, 0, V('r')], '<')),
        ('EXIT_ODD_A', True,
         ('F', [1, 0, 1, 0, BLANK], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, V('r')], '<'),
         ('E', [BLANK], [1]*7 + [0]*4 + [1]*7 + [0, 0] + [1]*6 + [0, 0, V('r')], '<')),
        ('ODD_FINAL', False,
         ('E', [BLANK], pl.norm_side([1, 1, 1, 1, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, 1, 0, 0, 1, 1, V('r')]), '<'),
         ('I', [0, 1, 1, 0, 0, 1, BLANK], pl.norm_side([1]*12 + mkrun((1, 1), {'b': 1}, 0) + [0, 0, V('r')]), '>')),
    ]

GLUE_KKHKHK = r"""(** ** The digit-list family *)

Fixpoint rgt (ds : list nat) : side :=
  match ds with
  | [] => 1 >> const 0
  | d :: t => [1;1]^^d *> 0 >> 0 >> rgt t
  end.

Definition Kd (ds : list nat) (a b : nat) : Q * tape :=
  (const 0) <{{E}} (1 >> [1;1]^^b *> 0 >> 0 >> [1;1]^^a *> 0 >> 0 >> rgt ds).

Lemma rgt_zeros : forall k t, rgt (repeat 0%nat k ++ t) = [0;0]^^k *> rgt t.
Proof. induction k; intros. - reflexivity. - simpl. rewrite IHk. reflexivity. Qed.

Lemma rgt_ones : forall k t, rgt (repeat 1%nat k ++ t) = [1;1;0;0]^^k *> rgt t.
Proof. induction k; intros. - reflexivity. - simpl. rewrite IHk. reflexivity. Qed.

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

(** ** Parity-2 Rebuild and 5-Stage Cascade Halting from c_end k s *)

Lemma blocks11111100_snoc : forall i Y,
  [1;1;1;1;1;1;0;0]^^i *> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> Y = [1;1;1;1;1;1;0;0]^^(S i) *> Y.
Proof.
  intros. change (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> Y) with ([1;1;1;1;1;1;0;0] *> Y).
  rewrite lpow_shift'. reflexivity.
Qed.

Lemma REBUILD2_LOOPS : forall m X r,
  ([1;0;1;0]^^(2 * m) *> X) <{{F}}
  (1 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> r) -->*
  X <{{F}}
  (1 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> [1;1;1;1;1;1;0;0]^^m *> r).
Proof.
  induction m as [| m IHm]; intros X r.
  - finish.
  - replace (2 * S m) with (S (S (2 * m))) by lia.
    simpl lpow; simpl app; simpl Str_app.
    eapply evstep_trans; [apply progress_evstep, REBUILD164 |].
    follow (IHm X (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> r)).
    rewrite blocks11111100_snoc.
    finish.
Qed.

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

Definition c_halt_even (m s : nat) : Q * tape :=
  (0 >> 1 >> 1 >> 0 >> 0 >> 1 >> const 0) {{I}}>
  (1 >> 1 >> [1;1]^^2063 *> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
   1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
   [1;1;1;1;1;1;0;0]^^m *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).

Definition c_halt_odd (m s : nat) : Q * tape :=
  (0 >> 1 >> 1 >> 0 >> 0 >> 1 >> const 0) {{I}}>
  (1 >> 1 >> [1;1]^^200 *> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
   [1;1;1;1;1;1;0;0]^^m *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).

Lemma c_halt_even_halted : forall m s, halted tm (c_halt_even m s).
Proof. intros. unfold c_halt_even. simpl. reflexivity. Qed.

Lemma c_halt_odd_halted : forall m s, halted tm (c_halt_odd m s).
Proof. intros. unfold c_halt_odd. simpl. reflexivity. Qed.

(** Halting for even k = 4 + 2 * m (including Round 1 where k_1 = 20 = 4 + 2 * 8): *)
Lemma KR_even_halt : forall m s,
  c_end (4 + 2 * m) s -->* c_halt_even m s.
Proof.
  intros m s. unfold c_end.
  replace (4 + 2 * m) with (S (S (2 * S m))) by lia.
  simpl lpow; simpl app; simpl Str_app.
  eapply evstep_trans; [apply progress_evstep, INIT173 |].
  follow (REBUILD2_LOOPS (S m) (const 0) (0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)).
  simpl lpow; simpl app; simpl Str_app.
  eapply evstep_trans; [apply progress_evstep, EXIT_EVEN_A |].
  set (tail := 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
               [1;1;1;1;1;1;0;0]^^m *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).
  change (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;1;1;0;0]^^m *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)
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
  unfold c_halt_even, tail. finish.
Qed.

(** Halting for odd k = 3 + 2 * m: *)
Lemma KR_odd_halt : forall m s,
  c_end (3 + 2 * m) s -->* c_halt_odd m s.
Proof.
  intros m s. unfold c_end.
  replace (3 + 2 * m) with (S (S (2 * m + 1))) by lia.
  simpl lpow; simpl app; simpl Str_app.
  eapply evstep_trans; [apply progress_evstep, INIT173 |].
  rewrite <- lpow_merge.
  change ([1;0;1;0]^^1 *> const 0) with (1 >> 0 >> 1 >> 0 >> const 0).
  follow (REBUILD2_LOOPS m (1 >> 0 >> 1 >> 0 >> const 0) (0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)).
  eapply evstep_trans; [apply progress_evstep, EXIT_ODD_A |].
  set (tail := 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
               [1;1;1;1;1;1;0;0]^^m *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0).
  change (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >>
          [1;1;1;1;1;1;0;0]^^m *> 0 >> 0 >> 1 >> [1;0;0;1]^^s *> const 0)
    with (1 >> [1;1]^^3 *> 0 >> 0 >> 0 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >>
          0 >> 0 >> 1 >> 1 >> tail).
  follow (D_step_gen 3 (1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (3 * 3 + 9)%nat with 18%nat.
  follow (D_step_gen 18 (1 >> 1 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (3 * 18 + 9)%nat with 63%nat.
  follow (D_step_gen 63 (1 >> 0 >> 0 >> 1 >> 1 >> tail)).
  change (1 >> [1;1]^^(3 * 63 + 9) *> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail)
    with (1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> [1;1]^^195 *> 0 >> 0 >> 0 >> 0 >> 1 >> 0 >> 0 >> 1 >> 1 >> tail).
  eapply evstep_trans; [apply (ODD_FINAL 195 tail) |].
  unfold c_halt_odd, tail. finish.
Qed.

(** ** Round 1 Clearing and Halting from the Blank Tape *)

Local Open Scope nat_scope.

Lemma R1iter : forall a ds b, Kd ds a b -->* Kd ds 0 (b + 3 * a).
Proof.
  induction a; intros.
  - replace (b + 3 * 0) with b by lia. finish.
  - eapply evstep_trans; [apply progress_evstep, KR1 |].
    follow (IHa ds (b + 3)).
    replace (b + 3 * S a) with (b + 3 + 3 * a) by lia. finish.
Qed.

Fixpoint iter (n : nat) (g : nat -> nat) (x : nat) : nat :=
  match n with
  | O => x
  | S n' => g (iter n' g x)
  end.

Lemma iter_S' : forall n g x, iter (S n) g x = iter n g (g x).
Proof. induction n; intros; simpl. - reflexivity. - rewrite <- IHn. reflexivity. Qed.

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

Definition bf : nat := Yb 0 20 5.

Lemma bf_def : bf = Yb 0 20 5.
Proof. reflexivity. Qed.

Opaque bf.

Lemma bf_ge_20 : 20 <= bf.
Proof. rewrite bf_def. pose proof (Yb_ge 0 20 5 ltac:(lia)). lia. Qed.

Lemma run_to_zero : c0 -->* Kd (repeat 0%nat 20) 0 bf.
Proof.
  follow init_reach.
  follow (R1iter 1 (repeat 1%nat 20) 2).
  change (2 + 3 * 1) with 5.
  change (repeat 1%nat 20) with (repeat 0%nat 0 ++ repeat 1%nat 20 ++ []).
  follow (BLKx 20 (fun j' _ => CDPx_all j') 20 0 [] 5 ltac:(lia) ltac:(lia)).
  rewrite app_nil_r, bf_def. apply evstep_refl.
Qed.

Lemma run_r1_gen : forall b s,
  20 + s = b ->
  c0 -->* Kd (repeat 0%nat 20) 0 b ->
  c0 -->* c_halt_even 8 s.
Proof.
  intros b s Hs Hr.
  follow Hr.
  rewrite <- Hs.
  follow (KR4x 20 s).
  change 20 with (4 + 2 * 8).
  apply (KR_even_halt 8 s).
Qed.

Theorem run_to_halt : c0 -->* c_halt_even 8 (bf - 20).
Proof.
  exact (run_r1_gen bf (bf - 20) ltac:(pose proof bf_ge_20; lia) run_to_zero).
Qed.

Theorem halt : halts tm c0.
Proof.
  destruct (with_counter run_to_halt) as [n Hn].
  eapply halts_multistep; [| exact Hn].
  apply halted_halts. apply c_halt_even_halted.
Qed.
"""

def gen_kkhkhk():
    pl.set_tm(M_KKHKHK)
    pl.LEMMAS.clear()
    stage_texts = []
    for nm, prog, s, t in get_kkhkhk_stages():
        ops, end, how = engine.run_until_stuck(s, pl.canon(t), target=t)
        assert (how == 'target' or not prog) and engine.equiv(end, t), (nm, how)
        stage_texts.append(coqgen.stage_lemma(nm, s, ops, t, progress=prog).replace('repeat rewrite (align_lpow', 'rewrite (align_lpow'))
    head = open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof\header.v.in').read()
    title = 'The 9-state machine 1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG--- (KKHKHK_231_144) halts'
    head = head.replace('@TITLE@', title).replace('@N@', '9').replace('@TM@', M_KKHKHK).replace('@TABLE@', coqgen_util.table(M_KKHKHK))
    text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
         + '\n(** ** Phase lemmas (generated) *)\n\n' + '\n'.join(stage_texts) + '\n' + GLUE_KKHKHK
    out_path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs\BB9_champ20_kkhkhk.v'
    open(out_path, 'w', newline='\n').write(text)
    print("Wrote", out_path, len(text))

if __name__ == '__main__':
    gen_kkhkhk()
