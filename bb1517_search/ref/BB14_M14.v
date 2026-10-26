(** * The 14-state machine M14 halts, with score (ones on the halted tape + 1) above f_(omega+2)^3(15) (proved in BB14_M14_bound.v) *)

From BB8 Require Import Individual142.
From Coq Require Import Lia PeanoNat List Wf_nat.
Import ListNotations.
Set Default Goal Selector "!".

(* machine: 1RB1RA_1RI1RC_0LD1LG_0RE1LD_1LN1RF_1LJ0RA_1RA0LH_1LG1LH_1RK0LM_1RZ0LE_0LE0RJ_1LH1LM_0LH0LL_0LG1LN *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, TM.R, B)  | A, 1 => Some (1, TM.R, A)
  | B, 0 => Some (1, TM.R, I)  | B, 1 => Some (1, TM.R, C)
  | C, 0 => Some (0, TM.L, D)  | C, 1 => Some (1, TM.L, G)
  | D, 0 => Some (0, TM.R, E)  | D, 1 => Some (1, TM.L, D)
  | E, 0 => Some (1, TM.L, N)  | E, 1 => Some (1, TM.R, F)
  | F, 0 => Some (1, TM.L, J)  | F, 1 => Some (0, TM.R, A)
  | G, 0 => Some (1, TM.R, A)  | G, 1 => Some (0, TM.L, H)
  | H, 0 => Some (1, TM.L, G)  | H, 1 => Some (1, TM.L, H)
  | I, 0 => Some (1, TM.R, K)  | I, 1 => Some (0, TM.L, M)
  | J, 0 => None               | J, 1 => Some (0, TM.L, E)
  | K, 0 => Some (0, TM.L, E)  | K, 1 => Some (0, TM.R, J)
  | L, 0 => Some (1, TM.L, H)  | L, 1 => Some (1, TM.L, M)
  | M, 0 => Some (0, TM.L, H)  | M, 1 => Some (0, TM.L, L)
  | N, 0 => Some (0, TM.L, G)  | N, 1 => Some (1, TM.L, N)
  end.

Notation "c --> c'" := (c -[ tm ]-> c')   (at level 40).
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

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

Lemma lpow_double : forall {T} (xs : list T) m, xs^^(2 * m) = (xs ++ xs)^^m.
Proof.
  induction m. - reflexivity.
  - replace (2 * S m) with (S (S (2 * m))) by lia. cbn [lpow]. rewrite IHm, app_assoc. reflexivity.
Qed.

(** ** Basic shift lemmas *)

Lemma cr_AR_1_1 : forall n l r, l {{A}}> [1]^^n *> r -->* [1]^^n *> l {{A}}> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_DL_1_1 : forall n l r, [1]^^n *> l <{{D}} r -->* l <{{D}} [1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_HL_1_1 : forall n l r, [1]^^n *> l <{{H}} r -->* l <{{H}} [1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_NL_1_1 : forall n l r, [1]^^n *> l <{{N}} r -->* l <{{N}} [1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_HL_01_01 : forall n l r, [0; 1]^^n *> l <{{H}} r -->* l <{{H}} [0; 1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_ML_11_10 : forall n l r, [1; 1]^^n *> l <{{M}} r -->* l <{{M}} [1; 0]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_EL_1_1 : forall n l r, [1]^^n *> l <{{E}} (0 >> r) -->* l <{{E}} (0 >> [1]^^n *> r).
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

(** ** Configurations and inner cascade rules *)

Definition Ca (j b : nat) (z : side) : Q * tape :=
  ([1]^^b *> [0; 1]^^j *> const 0) {{A}}> (0 >> z).

Definition Ch (j b : nat) (z : side) : Q * tape :=
  ([0; 1]^^j *> const 0) <{{H}} (1 >> [1]^^b *> 0 >> z).

Definition Ch0 (j c d : nat) : Q * tape :=
  ([0; 1]^^j *> const 0) <{{H}} (0 >> 0 >> [1]^^c *> 0 >> [1]^^d *> const 0).

Definition Ci (p a c d : nat) : Q * tape :=
  ([1]^^(a + 1) *> [0; 1]^^p *> const 0) {{I}}> ([1]^^c *> 0 >> [1]^^d *> const 0).

Definition blk (a : nat) (z : side) : side :=
  1 >> [1]^^a *> 0 >> z.

Lemma CA_SH : forall j b z,
  Ca j b (1 >> 0 >> z) -->+ Ca (S j) b z.
Proof.
  intros j b z. unfold Ca.
  start_progress.
  follow cr_DL_1_1.
  align_tape.
  execute.
  follow cr_AR_1_1.
  finish_norm.
Qed.

Lemma CA_SH_iter : forall k j b z,
  Ca j b ([1; 0]^^k *> z) -->* Ca (j + k) b z.
Proof.
  induction k; intros j b z.
  - replace (j + 0)%nat with j by lia. finish.
  - simpl.
    eapply evstep_trans; [apply progress_evstep, CA_SH |].
    follow (IHk (S j) b z).
    replace (S j + k)%nat with (j + S k)%nat by lia. finish.
Qed.

Lemma CA_EXIT : forall j b z,
  Ca j b (0 >> z) -->+ ([1]^^(b + 2) *> [0; 1]^^j *> const 0) {{I}}> z.
Proof.
  intros j b z. unfold Ca.
  start_progress.
  finish_norm.
Qed.

Lemma CA_CH : forall j b y,
  Ca j b (1 >> 1 >> y) -->+ Ch j b (1 >> y).
Proof.
  intros j b y. unfold Ca, Ch.
  start_progress.
  follow cr_HL_1_1.
  finish_norm.
Qed.

Lemma CH_0 : forall b z,
  Ch 0 b z -->+ Ca 0 (b + 3) z.
Proof.
  intros b z. unfold Ch, Ca. simpl lpow.
  start_progress.
  follow cr_AR_1_1.
  finish_norm.
Qed.

Lemma CH_S_aux : forall j b z,
  Ch (S j) b z -->+ Ca 0 2 ([1; 0]^^j *> blk (S b) z).
Proof.
  intros j b z. unfold Ch, Ca, blk.
  start_progress.
  follow cr_HL_01_01.
  align_tape.
  execute; finish_norm.
Qed.

Lemma CH_S : forall j b z,
  Ch (S j) b z -->+ Ca j 2 (blk (S b) z).
Proof.
  intros j b z.
  eapply progress_evstep_trans; [apply CH_S_aux |].
  follow (CA_SH_iter j 0 2 (blk (S b) z)).
  finish_norm.
Qed.

Lemma CH0_aux : forall j c d,
  Ch0 j c d -->+ Ca 0 2 ([1; 0]^^j *> 0 >> [1]^^c *> 0 >> [1]^^d *> const 0).
Proof.
  intros j c d. unfold Ch0, Ca.
  eapply evstep_progress_trans; [apply cr_HL_01_01 |].
  align_tape.
  start_progress; finish_norm.
Qed.

Lemma CH0_CI : forall j c d,
  Ch0 j c d -->+ Ci j 3 c d.
Proof.
  intros j c d. unfold Ci.
  eapply progress_evstep_trans; [apply CH0_aux |].
  follow (CA_SH_iter j 0 2 (0 >> [1]^^c *> 0 >> [1]^^d *> const 0)).
  apply progress_evstep.
  eapply progress_evstep_trans; [apply CA_EXIT |].
  finish_norm.
Qed.

Lemma C_REL_aux : forall p' a d,
  Ci (S p') a 0 (S (S d)) -->+ Ch0 p' (a + 3) d.
Proof.
  intros p' a d. unfold Ci, Ch0.
  start_progress.
  follow cr_NL_1_1.
  execute; finish_norm.
Qed.

Lemma C_REL : forall p' a d,
  Ci (S p') a 0 (S (S d)) -->+ Ci p' 3 (a + 3) d.
Proof.
  intros p' a d.
  eapply progress_evstep_trans; [apply C_REL_aux |].
  apply progress_evstep, CH0_CI.
Qed.

Lemma D_REL_aux : forall p' a,
  Ci (S (S p')) a 0 0 -->+ Ch0 p' 2 (a + 2).
Proof.
  intros p' a. unfold Ci, Ch0.
  start_progress.
  follow cr_EL_1_1.
  execute; finish_norm.
Qed.

Lemma D_REL : forall p' a,
  Ci (S (S p')) a 0 0 -->+ Ci p' 3 2 (a + 2).
Proof.
  intros p' a.
  eapply progress_evstep_trans; [apply D_REL_aux |].
  apply progress_evstep, CH0_CI.
Qed.

Lemma I_EVEN : forall p' k r,
  ([1]^^(2 * k + 1) *> [0; 1]^^(S p') *> const 0) {{I}}> (1 >> r) -->+
  Ch p' 1 ([1; 0]^^k *> 0 >> r).
Proof.
  intros p' k r. unfold Ch.
  rewrite lpow_add. cbn [lpow Str_app].
  rewrite (lpow_double [1] k). cbn [app].
  start_progress.
  follow cr_ML_11_10.
  execute; finish_norm.
Qed.

Lemma I_ODD : forall p' k r,
  ([1]^^(2 * k + 2) *> [0; 1]^^(S p') *> const 0) {{I}}> (1 >> r) -->+
  Ch p' 0 ([1; 0]^^(S k) *> 0 >> r).
Proof.
  intros p' k r. unfold Ch.
  replace (2 * k + 2)%nat with (2 * S k)%nat by lia.
  rewrite (lpow_double [1] (S k)). cbn [app].
  start_progress.
  follow cr_ML_11_10.
  execute; finish_norm.
Qed.

(** ** Halting step at d = 1 *)

Definition c_end (p a : nat) : Q * tape :=
  (0 >> 1 >> [1]^^(a + 1) *> [0; 1]^^p *> const 0) {{J}}> const 0.

Lemma HALT_step : forall p a,
  Ci p a 0 1 -->+ c_end p a.
Proof.
  intros p a. unfold Ci, c_end. simpl lpow.
  start_progress; finish_norm.
Qed.

Lemma c_end_halted : forall p a, halted tm (c_end p a).
Proof. intros. unfold c_end. simpl. reflexivity. Qed.

(** ** Exact hierarchy functions W, Kc, Kd_step *)

Local Open Scope nat_scope.

Fixpoint iter {X : Type} (n : nat) (g : X -> X) (x : X) : X :=
  match n with
  | O => x
  | S n' => g (iter n' g x)
  end.

Lemma iter_S' : forall {X : Type} n (g : X -> X) x, iter (S n) g x = iter n g (g x).
Proof. induction n; intros; simpl. - reflexivity. - rewrite <- IHn. reflexivity. Qed.

Lemma iter_add : forall {X : Type} a b (g : X -> X) x, iter (a + b) g x = iter a g (iter b g x).
Proof. induction a; intros; simpl. - reflexivity. - rewrite IHa. reflexivity. Qed.

Fixpoint W (j : nat) (b : nat) : nat :=
  match j with
  | O => b + 3
  | S j' => iter (S b) (W j') 2
  end.

Lemma W_0 : forall b, W 0 b = b + 3.
Proof. reflexivity. Qed.

Lemma W_S : forall j b, W (S j) b = iter (S b) (W j) 2.
Proof. reflexivity. Qed.

Lemma BLK_iter_aux : forall j,
  (forall b z, Ch j b z -->+ Ca j (W j b) z) ->
  forall a b z, Ca j b (blk a z) -->+ Ca (S j) (iter a (W j) b) z.
Proof.
  intros j HCh a. induction a as [| a IHa]; intros b z.
  - apply CA_SH.
  - eapply progress_evstep_trans; [apply CA_CH |].
    eapply evstep_trans; [apply progress_evstep, HCh |].
    rewrite iter_S'.
    apply progress_evstep, IHa.
Qed.

Lemma CH_CA : forall j b z,
  Ch j b z -->+ Ca j (W j b) z.
Proof.
  induction j as [| j IHj]; intros b z.
  - apply CH_0.
  - eapply progress_evstep_trans; [apply CH_S |].
    apply progress_evstep.
    apply (BLK_iter_aux j IHj (S b) 2 z).
Qed.

Lemma CI_EVEN : forall p' k c d,
  Ci (S p') (2 * k) (S c) d -->+ Ci (p' + k) (W p' 1 + 1) c d.
Proof.
  intros p' k c d. unfold Ci.
  cbn [lpow Str_app].
  eapply progress_evstep_trans; [apply I_EVEN |].
  eapply evstep_trans; [apply progress_evstep, CH_CA |].
  follow (CA_SH_iter k p' (W p' 1) (0 >> [1]^^c *> 0 >> [1]^^d *> const 0)%sym).
  eapply evstep_trans; [apply progress_evstep, CA_EXIT |].
  finish_norm.
Qed.

Lemma CI_ODD : forall p' k c d,
  Ci (S p') (2 * k + 1) (S c) d -->+ Ci (p' + S k) (W p' 0 + 1) c d.
Proof.
  intros p' k c d. unfold Ci.
  cbn [lpow Str_app].
  replace (2 * k + 1 + 1) with (2 * k + 2) by lia.
  eapply progress_evstep_trans; [apply I_ODD |].
  eapply evstep_trans; [apply progress_evstep, CH_CA |].
  follow (CA_SH_iter (S k) p' (W p' 0) (0 >> [1]^^c *> 0 >> [1]^^d *> const 0)%sym).
  eapply evstep_trans; [apply progress_evstep, CA_EXIT |].
  finish_norm.
Qed.

(** ** Initial 801 steps from blank tape *)

Lemma init_26 : c0 -->* Ca 1 1 (blk 2 (const 0)%sym).
Proof.
  unfold Ca, blk. simpl.
  do 26 step; finish_norm.
Qed.

Lemma init_578 : c0 -->* Ci 2 30 0 0.
Proof.
  follow init_26.
  eapply evstep_trans; [apply progress_evstep, (BLK_iter_aux 1 (CH_CA 1) 2 1 (const 0)%sym) |].
  change (iter 2 (W 1) 1) with 29.
  rewrite const_unfold at 1.
  eapply evstep_trans; [apply progress_evstep, CA_EXIT |].
  apply evstep_refl.
Qed.

Lemma init_720 : forall d, Ci 0 3 2 d -->* Ci 2 3 1 d.
Proof.
  intros d. unfold Ci.
  change (3 + 1) with 4.
  cbn [lpow Str_app].
  do 35 step.
  apply evstep_refl.
Qed.

Lemma init_801 : c0 -->* Ci 3 6 0 32.
Proof.
  follow init_578.
  eapply evstep_trans; [apply progress_evstep, (D_REL 0 30) |].
  change (30 + 2) with 32.
  follow (init_720 32).
  eapply evstep_trans; [apply progress_evstep, (CI_ODD 1 1 0 32) |].
  change (W 1 0 + 1) with 6.
  apply evstep_refl.
Qed.

(** ** Growth and parity invariants *)

Ltac absmod x k :=
  let q := fresh "q" in let r := fresh "r" in
  let H1 := fresh "Hdm" in let H2 := fresh "Hmb" in
  pose proof (Nat.div_mod_eq x k) as H1;
  assert (H2 : x mod k < k) by (apply Nat.mod_upper_bound; discriminate);
  set (q := x / k) in *; set (r := x mod k) in *; clearbody q r.
Ltac mods :=
  repeat match goal with
  | H : context[?x mod ?k] |- _ => absmod x k
  | |- context[?x mod ?k] => absmod x k
  | H : context[?x / ?k] |- _ => absmod x k
  | |- context[?x / ?k] => absmod x k
  end.

Lemma iter_lin3 : forall g, (forall a, a + 3 <= g a) -> forall n x, x + 3 * n <= iter n g x.
Proof.
  intros g Hg. induction n; intros; simpl. - lia.
  - specialize (IHn x). specialize (Hg (iter n g x)). lia.
Qed.

Lemma iter_par_nat : forall g, (forall y, g y mod 2 = (y + 1) mod 2) ->
  forall n x, iter n g x mod 2 = (x + n) mod 2.
Proof.
  intros g Hg. induction n; intros x; cbn [iter].
  - f_equal; lia.
  - rewrite Hg. pose proof (IHn x). mods; lia.
Qed.

Lemma W_grow : forall j b, b + 3 <= W j b.
Proof.
  induction j as [| j IHj]; intros b.
  - rewrite W_0. lia.
  - rewrite W_S.
    pose proof (iter_lin3 (W j) IHj (S b) 2). lia.
Qed.

Lemma W_par : forall j b, W j b mod 2 = (b + 1) mod 2.
Proof.
  induction j as [| j IHj]; intros b.
  - rewrite W_0. mods; lia.
  - rewrite W_S. rewrite (iter_par_nat (W j) IHj). mods; lia.
Qed.

Opaque W.

Definition Kc (pa : nat * nat) : nat * nat :=
  let '(p, a) := pa in
  (p - 1 + (a + 1) / 2, W (p - 1) (1 - a mod 2) + 1).

Lemma Kc_step : forall c d pa,
  1 <= fst pa ->
  Ci (fst pa) (snd pa) (S c) d -->+ Ci (fst (Kc pa)) (snd (Kc pa)) c d.
Proof.
  intros c d [p a] Hp. cbn [fst snd Kc] in *.
  destruct p as [| p']; [lia |].
  replace (S p' - 1) with p' by lia.
  assert (Ha : a mod 2 = 0 /\ a = 2 * (a / 2) \/ a mod 2 = 1 /\ a = 2 * (a / 2) + 1)
    by (mods; lia).
  destruct Ha as [[Hm Heq] | [Hm Heq]].
  - rewrite Hm. replace (1 - 0) with 1 by lia.
    replace ((a + 1) / 2) with (a / 2) by (mods; lia).
    rewrite Heq at 1. apply CI_EVEN.
  - rewrite Hm. replace (1 - 1) with 0 by lia.
    replace (p' + (a + 1) / 2) with (p' + S (a / 2)) by (mods; lia).
    rewrite Heq at 1. apply CI_ODD.
Qed.

Lemma Kc_props : forall pa,
  1 <= fst pa -> 3 <= snd pa ->
  fst pa + 1 <= fst (Kc pa) /\
  3 <= snd (Kc pa) /\
  snd (Kc pa) mod 2 = (snd pa + 1) mod 2.
Proof.
  intros [p a] Hp Ha. cbn [fst snd Kc] in *.
  pose proof (W_grow (p - 1) (1 - a mod 2)).
  pose proof (W_par (p - 1) (1 - a mod 2)).
  split; [| split]; mods; lia.
Qed.

Lemma Kc_loop : forall c d pa,
  1 <= fst pa -> 3 <= snd pa ->
  Ci (fst pa) (snd pa) c d -->* Ci (fst (iter c Kc pa)) (snd (iter c Kc pa)) 0 d /\
  fst pa + c <= fst (iter c Kc pa) /\
  3 <= snd (iter c Kc pa) /\
  snd (iter c Kc pa) mod 2 = (snd pa + c) mod 2.
Proof.
  induction c as [| c IHc]; intros d pa Hp Ha.
  - cbn [iter]. split; [finish | split; [lia | split; [lia | f_equal; lia]]].
  - rewrite iter_S'.
    destruct (Kc_props pa Hp Ha) as [Hp1 [Ha1 Hm1]].
    destruct (IHc d (Kc pa) ltac:(lia) Ha1) as [Hrun [Hp2 [Ha2 Hm2]]].
    split; [| split; [| split]].
    + eapply evstep_trans; [apply progress_evstep, (Kc_step c d pa Hp) | exact Hrun].
    + lia.
    + exact Ha2.
    + rewrite Hm2. mods; lia.
Qed.

Definition Kd_step (pa : nat * nat) : nat * nat :=
  let '(p, a) := pa in
  iter (a + 3) Kc (p - 1, 3).

Lemma Kd_step_all : forall d pa,
  2 <= fst pa -> 3 <= snd pa ->
  Ci (fst pa) (snd pa) 0 (S (S d)) -->+ Ci (fst (Kd_step pa)) (snd (Kd_step pa)) 0 d /\
  fst pa + 2 <= fst (Kd_step pa) /\
  3 <= snd (Kd_step pa) /\
  snd (Kd_step pa) mod 2 = snd pa mod 2.
Proof.
  intros d [p a] Hp Ha. cbn [fst snd Kd_step] in *.
  destruct p as [| p']; [lia |].
  replace (S p' - 1) with p' by lia.
  destruct (Kc_loop (a + 3) d (p', 3) ltac:(cbn; lia) ltac:(cbn; lia)) as [Hrun [Hp1 [Ha1 Hm1]]].
  cbn [fst snd] in *.
  split; [| split; [| split]].
  - eapply progress_evstep_trans; [apply C_REL | exact Hrun].
  - lia.
  - exact Ha1.
  - rewrite Hm1. mods; lia.
Qed.

Definition Kd_iter (m : nat) (pa : nat * nat) : nat * nat :=
  iter m Kd_step pa.

Lemma Kd_loop : forall m r pa,
  2 <= fst pa -> 3 <= snd pa ->
  Ci (fst pa) (snd pa) 0 (2 * m + r) -->* Ci (fst (Kd_iter m pa)) (snd (Kd_iter m pa)) 0 r /\
  fst pa + 2 * m <= fst (Kd_iter m pa) /\
  3 <= snd (Kd_iter m pa) /\
  snd (Kd_iter m pa) mod 2 = snd pa mod 2.
Proof.
  unfold Kd_iter.
  induction m as [| m IHm]; intros r pa Hp Ha.
  - cbn [iter]. replace (2 * 0 + r) with r by lia.
    split; [finish | split; [lia | split; [lia | reflexivity]]].
  - rewrite iter_S'.
    replace (2 * S m + r) with (S (S (2 * m + r))) by lia.
    destruct (Kd_step_all (2 * m + r) pa Hp Ha) as [Hstep [Hp1 [Ha1 Hm1]]].
    destruct (IHm r (Kd_step pa) ltac:(lia) Ha1) as [Hrun [Hp2 [Ha2 Hm2]]].
    split; [| split; [| split]].
    + eapply evstep_trans; [apply progress_evstep, Hstep | exact Hrun].
    + lia.
    + exact Ha2.
    + rewrite Hm2, Hm1. reflexivity.
Qed.

Definition D_reload (pa : nat * nat) : nat * nat :=
  let '(p, a) := pa in
  iter 2 Kc (p - 2, 3).

Lemma D_reload_all : forall pa,
  3 <= fst pa -> 3 <= snd pa ->
  Ci (fst pa) (snd pa) 0 0 -->+ Ci (fst (D_reload pa)) (snd (D_reload pa)) 0 (snd pa + 2) /\
  3 <= fst (D_reload pa) /\
  3 <= snd (D_reload pa) /\
  snd (D_reload pa) mod 2 = 1.
Proof.
  intros [p a] Hp Ha. cbn [fst snd D_reload] in *.
  destruct p as [| [| p']]; [lia | lia |].
  replace (S (S p') - 2) with p' by lia.
  destruct (Kc_loop 2 (a + 2) (p', 3) ltac:(cbn; lia) ltac:(cbn; lia)) as [Hrun [Hp1 [Ha1 Hm1]]].
  cbn [fst snd] in *.
  split; [| split; [| split]].
  - eapply progress_evstep_trans; [apply D_REL | exact Hrun].
  - lia.
  - exact Ha1.
  - rewrite Hm1. reflexivity.
Qed.

(** ** The full run of M14 *)

Definition pa1 : nat * nat := Kd_iter 16 (3, 6).
Definition pa2_0 : nat * nat := D_reload pa1.
Definition pa2 : nat * nat := Kd_iter (snd pa1 / 2 + 1) pa2_0.
Definition pa3_0 : nat * nat := D_reload pa2.
Definition pa3 : nat * nat := Kd_iter (snd pa2 / 2 + 1) pa3_0.

Lemma pa1_def : pa1 = Kd_iter 16 (3, 6). Proof. reflexivity. Qed.
Lemma pa2_0_def : pa2_0 = D_reload pa1. Proof. reflexivity. Qed.
Lemma pa2_def : pa2 = Kd_iter (snd pa1 / 2 + 1) pa2_0. Proof. reflexivity. Qed.
Lemma pa3_0_def : pa3_0 = D_reload pa2. Proof. reflexivity. Qed.
Lemma pa3_def : pa3 = Kd_iter (snd pa2 / 2 + 1) pa3_0. Proof. reflexivity. Qed.

Opaque Kc Kd_step Kd_iter D_reload pa1 pa2_0 pa2 pa3_0 pa3.

Lemma run_init_loop : forall m pa0,
  c0 -->* Ci (fst pa0) (snd pa0) 0 (2 * m) ->
  3 <= fst pa0 -> 3 <= snd pa0 -> snd pa0 mod 2 = 0 ->
  c0 -->* Ci (fst (Kd_iter m pa0)) (snd (Kd_iter m pa0)) 0 0 /\
  3 <= fst (Kd_iter m pa0) /\ 3 <= snd (Kd_iter m pa0) /\ snd (Kd_iter m pa0) mod 2 = 0.
Proof.
  intros m pa0 H0 Hp0 Ha0 Hm0.
  destruct (Kd_loop m 0 pa0 ltac:(lia) Ha0) as [Hrun [Hp [Ha Hm]]].
  replace (2 * m + 0) with (2 * m) in Hrun by lia.
  split; [| split; [lia | split; [lia | rewrite Hm; exact Hm0]]].
  follow H0. exact Hrun.
Qed.

Lemma run_round_even : forall pa,
  c0 -->* Ci (fst pa) (snd pa) 0 0 /\ 3 <= fst pa /\ 3 <= snd pa /\ snd pa mod 2 = 0 ->
  let pa' := Kd_iter (snd pa / 2 + 1) (D_reload pa) in
  c0 -->* Ci (fst pa') (snd pa') 0 0 /\
  3 <= fst pa' /\ 3 <= snd pa' /\ snd pa' mod 2 = 1.
Proof.
  intros pa [Hrun1 [Hp1 [Ha1 Hm1]]] pa'. subst pa'.
  destruct (D_reload_all pa Hp1 Ha1) as [Hrel2 [Hp2_0 [Ha2_0 Hm2_0]]].
  assert (Hd2 : snd pa + 2 = 2 * (snd pa / 2 + 1) + 0) by (mods; lia).
  destruct (Kd_loop (snd pa / 2 + 1) 0 (D_reload pa) ltac:(lia) Ha2_0) as [Hloop2 [Hp2 [Ha2 Hm2]]].
  split; [| split; [lia | split; [lia | rewrite Hm2; exact Hm2_0]]].
  follow Hrun1.
  eapply evstep_trans; [apply progress_evstep, Hrel2 |].
  rewrite Hd2. exact Hloop2.
Qed.

Lemma run_round_odd : forall pa,
  c0 -->* Ci (fst pa) (snd pa) 0 0 /\ 3 <= fst pa /\ 3 <= snd pa /\ snd pa mod 2 = 1 ->
  let pa' := Kd_iter (snd pa / 2 + 1) (D_reload pa) in
  c0 -->* c_end (fst pa') (snd pa').
Proof.
  intros pa [Hrun2 [Hp2 [Ha2 Hm2]]] pa'. subst pa'.
  destruct (D_reload_all pa Hp2 Ha2) as [Hrel3 [Hp3_0 [Ha3_0 Hm3_0]]].
  assert (Hd3 : snd pa + 2 = 2 * (snd pa / 2 + 1) + 1) by (mods; lia).
  destruct (Kd_loop (snd pa / 2 + 1) 1 (D_reload pa) ltac:(lia) Ha3_0) as [Hloop3 _].
  follow Hrun2.
  eapply evstep_trans; [apply progress_evstep, Hrel3 |].
  rewrite Hd3. follow Hloop3.
  apply progress_evstep, HALT_step.
Qed.

Lemma run_pa1 :
  c0 -->* Ci (fst pa1) (snd pa1) 0 0 /\
  3 <= fst pa1 /\ 3 <= snd pa1 /\ snd pa1 mod 2 = 0.
Proof.
  rewrite !pa1_def.
  apply (run_init_loop 16 (3, 6)); [exact init_801 | cbn; lia | cbn; lia | reflexivity].
Qed.

Lemma run_pa2 :
  c0 -->* Ci (fst pa2) (snd pa2) 0 0 /\
  3 <= fst pa2 /\ 3 <= snd pa2 /\ snd pa2 mod 2 = 1.
Proof.
  rewrite !pa2_def, !pa2_0_def.
  exact (run_round_even pa1 run_pa1).
Qed.

Lemma run_pa3 :
  c0 -->* c_end (fst pa3) (snd pa3).
Proof.
  rewrite !pa3_def, !pa3_0_def.
  exact (run_round_odd pa2 run_pa2).
Qed.

Theorem halt : halts tm c0.
Proof.
  destruct (with_counter run_pa3) as [n Hn].
  eapply halts_multistep; [| exact Hn].
  apply halted_halts. apply c_end_halted.
Qed.
