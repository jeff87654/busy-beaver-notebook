"""Generate complete, axiom-free Coq halting proofs for the 7-state record pair:
  - champ_231: 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB (BB7_champ20_1RB0RG.v)
  - champ_232: 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB (BB7_champ20_1RB0RG_G0_1LC.v)
"""
import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, coqgen, coqgen_util

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

def get_stages():
    return [
        ('R1', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 1, 1] + mkrun((1, 1), {'a': 1}, 0) + [0, 0, V('r')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 1, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [1, 1, 0, 0] + mkrun((1, 1), {'a': 1}, 0) + [0, 0, V('r')]), '<')),
        ('R2', True,
         ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, 1, 1] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '<'),
         ('E', [BLANK], pl.norm_side([1, 0, 0, 1, 1, 1] + mkrun((1, 1), {'b': 1}, 0) + [1, 1, 1, 0, 0] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '<')),
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

GLUE = r"""(** ** The digit-list family *)

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

Lemma repeat_snoc : forall (x : nat) n U, repeat x n ++ x :: U = repeat x (S n) ++ U.
Proof. induction n; intros; simpl. - reflexivity. - rewrite IHn. reflexivity. Qed.

(** ** The four rules *)

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

Lemma c_end_halted : forall k s, halted tm (c_end k s).
Proof. intros. unfold c_end. simpl. reflexivity. Qed.

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

Lemma KR4 : forall k s,
  exists c, Kd (repeat 0%nat k) 0 (k + s) -->* c /\ halted tm c.
Proof.
  intros k s. exists (c_end k s). split; [apply KR4x | apply c_end_halted].
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
  { unfold c0. do @STEP1@ step. finish. }
  follow H1.
  follow (SROUNDS 13 0 (0 >> 0 >> 0 >> 0 >> 1 >> const 0)).
  change (1 >> [1]^^(3 * 13 + 0) *> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> const 0)
    with (1 >> [1;1]^^19 *> 1 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 1 >> const 0).
  eapply evstep_trans; [apply progress_evstep, (INITA 19) |].
  follow (GLOOPS 19 (1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> 0 >> 1 >> 0 >> 1 >> const 0)).
  unfold Kd. do @STEP2@ step. finish.
Qed.

(** ** Exact clearing functions and clearing lemma *)

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

Lemma iter_lin : forall g, (forall a, a + 1 <= g a) -> forall n x, x + n <= iter n g x.
Proof.
  intros g Hg. induction n; intros; simpl. - lia.
  - specialize (IHn x). specialize (Hg (iter n g x)). lia.
Qed.

(** U j x : the value of b after clearing ONE unit of a digit at depth j (j zero digits before it) from b = x.
    X j   : the value of b after clearing j ones at depths 0 .. j-1, starting from b = 3.
      U 0 x = 3x + 9,  U (j+1) x = (U j)^(x - j + 2) (X j),  X 0 = 3,  X (j+1) = U j (X j). *)
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

Lemma growth : forall j, (forall x, x + j + 2 <= U j x) /\ 2 * j + 3 <= X j.
Proof.
  induction j as [| j [Hu Hx]].
  - split; [intros; rewrite U_0; lia | rewrite X_0; lia].
  - split.
    + intros x. rewrite U_S.
      pose proof (iter_lin (U j) ltac:(intros a; specialize (Hu a); lia) (x - j + 2) (X j)). lia.
    + rewrite X_S. pose proof (Hu (X j)). lia.
Qed.

Lemma Ugrow : forall j x, x + j + 2 <= U j x.
Proof. intros. apply growth. Qed.

Lemma Xgrow : forall j, 2 * j + 3 <= X j.
Proof. intros. apply growth. Qed.

Lemma CHx : forall v Us B, Kd (v :: Us) 0 B -->* Kd (0 :: Us) 0 (iter v (U 0) B).
Proof.
  induction v; intros Us B.
  - apply evstep_refl.
  - eapply evstep_trans; [apply progress_evstep, KR2 |].
    follow (R1iter (B + 3) (v :: Us) 0).
    rewrite iter_S', U_0. replace (3 * B + 9) with (0 + 3 * (B + 3)) by lia.
    apply IHv.
Qed.

Definition CDPx (j : nat) : Prop := forall v Us B, j <= B ->
  Kd (repeat 0 j ++ v :: Us) 0 B -->* Kd (repeat 0 (S j) ++ Us) 0 (iter v (U j) B).

(** n ones cleared at depths t .. t+n-1 *)
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
  Kd (repeat 0 t ++ repeat 1 n ++ V) 0 x -->* Kd (repeat 0 (t + n) ++ V) 0 (Yb t n x).
Proof.
  intros D HD. induction n as [| n IHn]; intros t V x Hd Hx.
  - replace (t + 0) with t by lia. apply evstep_refl.
  - rewrite <- repeat_snoc.
    follow (IHn t (1 :: V) x ltac:(lia) Hx).
    follow (HD (t + n) ltac:(lia) 1 V (Yb t n x) (Yb_ge t n x Hx)).
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
      assert (Hr : Kd (repeat 0 (S n) ++ S w :: Us) 0 B -->*
                   Kd (repeat 1 n ++ S (S (S s)) :: w :: Us) 0 3).
      { rewrite HB'. eapply evstep_trans; [apply progress_evstep, KR3 |].
        follow (R1iter 1 (repeat 1 n ++ S (S (S s)) :: w :: Us) 0). finish. }
      follow Hr.
      follow (BLKx (S n) IH n 0 (S (S (S s)) :: w :: Us) 3 ltac:(lia) ltac:(lia)).
      rewrite Yb_X.
      follow (IH n ltac:(lia) (S (S (S s))) (w :: Us) (X n) ltac:(pose proof (Xgrow n); lia)).
      replace (iter (S (S (S s))) (U n) (X n)) with (U (S n) B)
        by (rewrite U_S; f_equal; lia).
      follow (IHw Us (U (S n) B) ltac:(pose proof (Ugrow (S n) B); lia)).
      rewrite iter_S'. apply evstep_refl.
Qed.

(** ** The run from the blank tape *)

Definition bf : nat := Yb 0 20 5.

Lemma bf_def : bf = Yb 0 20 5.
Proof. reflexivity. Qed.

Opaque bf.

Lemma bf_ge_20 : 20 <= bf.
Proof. rewrite bf_def. pose proof (Yb_ge 0 20 5 ltac:(lia)). lia. Qed.

Lemma run_to_zero : c0 -->* Kd (repeat 0 20) 0 bf.
Proof.
  follow init_reach.
  follow (R1iter 1 (repeat 1 20) 2).
  change (2 + 3 * 1) with 5.
  change (repeat 1 20) with (repeat 0 0 ++ repeat 1 20 ++ []).
  follow (BLKx 20 (fun j' _ => CDPx_all j') 20 0 [] 5 ltac:(lia) ltac:(lia)).
  rewrite app_nil_r, bf_def. apply evstep_refl.
Qed.

Theorem halt : halts tm c0.
Proof.
  pose proof bf_ge_20 as Hbf.
  destruct (KR4 20 (bf - 20)) as [c [H1 H2]].
  replace (20 + (bf - 20)) with bf in H1 by lia.
  assert (Hrun : c0 -->* c) by (follow run_to_zero; exact H1).
  destruct (with_counter Hrun) as [n Hn].
  eapply halts_multistep; [| exact Hn].
  apply halted_halts. exact H2.
Qed.
"""

def gen_file(tm, out_path, title, step1, step2):
    pl.set_tm(tm)
    pl.LEMMAS.clear()
    stage_texts = []
    for nm, prog, s, t in get_stages():
        ops, end, how = engine.run_until_stuck(s, pl.canon(t), target=t)
        assert how == 'target' and engine.equiv(end, t), nm
        stage_texts.append(coqgen.stage_lemma(nm, s, ops, t, progress=prog).replace('repeat rewrite (align_lpow', 'rewrite (align_lpow'))
    head = open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof\header.v.in').read()
    head = head.replace('@TITLE@', title).replace('@N@', '7').replace('@TM@', tm).replace('@TABLE@', coqgen_util.table(tm))
    glue = GLUE.replace('@STEP1@', str(step1)).replace('@STEP2@', str(step2))
    text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
         + '\n(** ** Phase lemmas (generated) *)\n\n' + '\n'.join(stage_texts) + '\n' + glue
    open(out_path, 'w', newline='\n').write(text)
    print("Wrote", out_path, len(text))

if __name__ == '__main__':
    proofs_dir = r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs'
    gen_file(M1, os.path.join(proofs_dir, 'BB7_champ20_1RB0RG.v'),
             'The 7-state 20-digit tripling champion 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB halts',
             310, 194)
    gen_file(M2, os.path.join(proofs_dir, 'BB7_champ20_1RB0RG_G0_1LC.v'),
             'The 7-state 20-digit tripling champion twin 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB halts',
             324, 240)
