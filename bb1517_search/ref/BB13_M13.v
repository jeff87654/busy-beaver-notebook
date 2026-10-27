(** * The 13-state machine M13 halts, with score (ones on the halted tape + 1) above f_(omega+2)(f_omega 20) (proved in BB13_M13_bound.v) *)

From BB8 Require Import Individual132.
From Coq Require Import Lia PeanoNat List Wf_nat.
Import ListNotations.
Set Default Goal Selector "!".

(* machine: 1LB1LA_1RC0LA_1RD1RC_1RE1RK_1RF0LJ_0LG1RI_1RE0RH_1LF0RC_1RM0LE_1LA1LE_0LL1LB_0RM1LL_1RZ1RH *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, TM.L, B)  | A, 1 => Some (1, TM.L, A)
  | B, 0 => Some (1, TM.R, C)  | B, 1 => Some (0, TM.L, A)
  | C, 0 => Some (1, TM.R, D)  | C, 1 => Some (1, TM.R, C)
  | D, 0 => Some (1, TM.R, E)  | D, 1 => Some (1, TM.R, K)
  | E, 0 => Some (1, TM.R, F)  | E, 1 => Some (0, TM.L, J)
  | F, 0 => Some (0, TM.L, G)  | F, 1 => Some (1, TM.R, I)
  | G, 0 => Some (1, TM.R, E)  | G, 1 => Some (0, TM.R, H)
  | H, 0 => Some (1, TM.L, F)  | H, 1 => Some (0, TM.R, C)
  | I, 0 => Some (1, TM.R, M)  | I, 1 => Some (0, TM.L, E)
  | J, 0 => Some (1, TM.L, A)  | J, 1 => Some (1, TM.L, E)
  | K, 0 => Some (0, TM.L, L)  | K, 1 => Some (1, TM.L, B)
  | L, 0 => Some (0, TM.R, M)  | L, 1 => Some (1, TM.L, L)
  | M, 0 => None               | M, 1 => Some (1, TM.R, H)
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

Lemma cr_CR_1_1 : forall n l r, l {{C}}> [1]^^n *> r -->* [1]^^n *> l {{C}}> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_LL_1_1 : forall n l r, [1]^^n *> l <{{L}} r -->* l <{{L}} [1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_AL_1_1 : forall n l r, [1]^^n *> l <{{A}} r -->* l <{{A}} [1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_AL_01_01 : forall n l r, [0; 1]^^n *> l <{{A}} r -->* l <{{A}} [0; 1]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_EL_11_10 : forall n l r, [1; 1]^^n *> l <{{E}} r -->* l <{{E}} [1; 0]^^n *> r.
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

Lemma cr_GL_1_1 : forall n l r, [1]^^n *> l <{{G}} (0 >> r) -->* l <{{G}} (0 >> [1]^^n *> r).
Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.

(** ** Configurations and inner cascade rules *)

Definition Ca (j b : nat) (z : side) : Q * tape :=
  ([1]^^b *> [0; 1]^^j *> const 0) {{C}}> (0 >> z).

Definition Ch (j b : nat) (z : side) : Q * tape :=
  ([0; 1]^^j *> const 0) <{{A}} (1 >> [1]^^b *> 0 >> z).

Definition Ce (p a c d : nat) : Q * tape :=
  ([1]^^(a + 2) *> [0; 1]^^p *> const 0) {{E}}> ([1; 0]^^c *> 0 >> [1]^^d *> const 0).

Definition blk (a : nat) (z : side) : side :=
  1 >> [1]^^a *> 0 >> z.

Lemma CA_SH : forall j b z,
  Ca j b (1 >> 0 >> z) -->+ Ca (S j) b z.
Proof.
  intros j b z. unfold Ca.
  start_progress.
  follow cr_LL_1_1.
  align_tape.
  execute.
  follow cr_CR_1_1.
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
  Ca j b (0 >> z) -->+ ([1]^^(b + 2) *> [0; 1]^^j *> const 0) {{E}}> z.
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
  follow cr_AL_1_1.
  finish_norm.
Qed.

Lemma CH_0 : forall b z,
  Ch 0 b z -->+ Ca 0 (b + 3) z.
Proof.
  intros b z. unfold Ch, Ca. simpl lpow.
  start_progress.
  follow cr_CR_1_1.
  finish_norm.
Qed.

Lemma CH_S_aux : forall j b z,
  Ch (S j) b z -->+ Ca 0 2 ([1; 0]^^j *> blk (S b) z).
Proof.
  intros j b z. unfold Ch, Ca, blk.
  start_progress.
  follow cr_AL_01_01.
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

Lemma E_EVEN : forall p' k r,
  ([1]^^(2 * k + 2) *> [0; 1]^^(S p') *> const 0) {{E}}> (1 >> 0 >> r) -->+
  Ch p' 1 ([1; 0]^^(S k) *> 0 >> r).
Proof.
  intros p' k r. unfold Ch.
  replace (2 * k + 2)%nat with (1 + (2 * k + 1))%nat by lia.
  rewrite !lpow_add. cbn [lpow Str_app].
  rewrite (lpow_double [1] k). cbn [app].
  start_progress.
  follow cr_EL_11_10.
  execute; finish_norm.
Qed.

Lemma C_REL : forall p' k d,
  Ce (S p') (2 * k) 0 (S (S d)) -->+ Ce p' 2 (k + 1) d.
Proof.
  intros p' k d. unfold Ce.
  rewrite lpow_add. cbn [lpow Str_app].
  rewrite (lpow_double [1] k). cbn [app].
  start_progress.
  follow cr_EL_11_10.
  align_tape.
  execute; finish_norm.
Qed.

Lemma D_REL : forall p' a,
  Ce (S (S p')) a 0 0 -->+ Ce p' 2 1 (a + 1).
Proof.
  intros p' a. unfold Ce.
  start_progress.
  follow cr_GL_1_1.
  align_tape.
  execute; finish_norm.
Qed.

(** ** Halting step at d = 1 *)

Definition c_end (p a : nat) : Q * tape :=
  ([1]^^(a + 5) *> [0; 1]^^p *> const 0) {{M}}> const 0.

Lemma HALT_step : forall p a,
  Ce p a 0 1 -->+ c_end p a.
Proof.
  intros p a. unfold Ce, c_end. simpl lpow.
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

Lemma CE_EVEN : forall p' k c d,
  Ce (S p') (2 * k) (S c) d -->+ Ce (p' + S k) (W p' 1) c d.
Proof.
  intros p' k c d. unfold Ce.
  cbn [lpow Str_app].
  eapply progress_evstep_trans; [apply E_EVEN |].
  eapply evstep_trans; [apply progress_evstep, CH_CA |].
  follow (CA_SH_iter (S k) p' (W p' 1) (0 >> [1; 0]^^c *> 0 >> [1]^^d *> const 0)%sym).
  eapply evstep_trans; [apply progress_evstep, CA_EXIT |].
  finish_norm.
Qed.

(** ** Initial 306 steps from blank tape *)

Lemma init_116 : c0 -->* Ce 1 2 2 2.
Proof.
  unfold Ce. cbn [lpow Str_app].
  do 116 step. finish_norm.
Qed.

Lemma init_306 : c0 -->* Ce 4 8 0 2.
Proof.
  follow init_116.
  eapply evstep_trans; [apply progress_evstep, (CE_EVEN 0 1 1 2) |].
  change (0 + S 1) with 2. change (W 0 1) with 4.
  eapply evstep_trans; [apply progress_evstep, (CE_EVEN 1 2 0 2) |].
  change (1 + S 2) with 4. change (W 1 1) with 8.
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
  (p + a / 2, W (p - 1) 1).

Lemma Kc_step : forall c d pa,
  1 <= fst pa -> snd pa mod 2 = 0 ->
  Ce (fst pa) (snd pa) (S c) d -->+ Ce (fst (Kc pa)) (snd (Kc pa)) c d.
Proof.
  intros c d [p a] Hp Hev. cbn [fst snd Kc] in *.
  destruct p as [| p']; [lia |].
  replace (S p' - 1) with p' by lia.
  assert (Ha : a = 2 * (a / 2)) by (mods; lia).
  replace (S p' + a / 2) with (p' + S (a / 2)) by lia.
  rewrite Ha at 1.
  apply CE_EVEN.
Qed.

Lemma Kc_props : forall pa,
  1 <= fst pa -> 2 <= snd pa -> snd pa mod 2 = 0 ->
  fst pa + 1 <= fst (Kc pa) /\
  2 <= snd (Kc pa) /\
  snd (Kc pa) mod 2 = 0.
Proof.
  intros [p a] Hp Ha Hev. cbn [fst snd Kc] in *.
  pose proof (W_grow (p - 1) 1).
  pose proof (W_par (p - 1) 1).
  split; [| split]; mods; lia.
Qed.

Lemma Kc_loop : forall c d pa,
  1 <= fst pa -> 2 <= snd pa -> snd pa mod 2 = 0 ->
  Ce (fst pa) (snd pa) c d -->* Ce (fst (iter c Kc pa)) (snd (iter c Kc pa)) 0 d /\
  fst pa + c <= fst (iter c Kc pa) /\
  2 <= snd (iter c Kc pa) /\
  snd (iter c Kc pa) mod 2 = 0.
Proof.
  induction c as [| c IHc]; intros d pa Hp Ha Hev.
  - cbn [iter]. split; [finish | split; [lia | split; [lia | exact Hev]]].
  - rewrite iter_S'.
    destruct (Kc_props pa Hp Ha Hev) as [Hp1 [Ha1 Hm1]].
    destruct (IHc d (Kc pa) ltac:(lia) Ha1 Hm1) as [Hrun [Hp2 [Ha2 Hm2]]].
    split; [| split; [| split]].
    + eapply evstep_trans; [apply progress_evstep, (Kc_step c d pa Hp Hev) | exact Hrun].
    + lia.
    + exact Ha2.
    + exact Hm2.
Qed.

Definition Kd_step (pa : nat * nat) : nat * nat :=
  let '(p, a) := pa in
  iter (a / 2 + 1) Kc (p - 1, 2).

Lemma Kd_step_all : forall d pa,
  2 <= fst pa -> 2 <= snd pa -> snd pa mod 2 = 0 ->
  Ce (fst pa) (snd pa) 0 (S (S d)) -->+ Ce (fst (Kd_step pa)) (snd (Kd_step pa)) 0 d /\
  fst pa + 1 <= fst (Kd_step pa) /\
  2 <= snd (Kd_step pa) /\
  snd (Kd_step pa) mod 2 = 0.
Proof.
  intros d [p a] Hp Ha Hev. cbn [fst snd Kd_step] in *.
  destruct p as [| p']; [lia |].
  replace (S p' - 1) with p' by lia.
  assert (Ha_eq : a = 2 * (a / 2)) by (mods; lia).
  assert (Ha_ge : 1 <= a / 2) by (mods; lia).
  destruct (Kc_loop (a / 2 + 1) d (p', 2) ltac:(cbn; lia) ltac:(cbn; lia) eq_refl) as [Hrun [Hp1 [Ha1 Hm1]]].
  cbn [fst snd] in *.
  split; [| split; [| split]].
  - rewrite Ha_eq at 1.
    eapply progress_evstep_trans; [apply C_REL | exact Hrun].
  - lia.
  - exact Ha1.
  - exact Hm1.
Qed.

Definition Kd_iter (m : nat) (pa : nat * nat) : nat * nat :=
  iter m Kd_step pa.

Lemma Kd_loop : forall m r pa,
  2 <= fst pa -> 2 <= snd pa -> snd pa mod 2 = 0 ->
  Ce (fst pa) (snd pa) 0 (2 * m + r) -->* Ce (fst (Kd_iter m pa)) (snd (Kd_iter m pa)) 0 r /\
  fst pa + m <= fst (Kd_iter m pa) /\
  2 <= snd (Kd_iter m pa) /\
  snd (Kd_iter m pa) mod 2 = 0.
Proof.
  unfold Kd_iter.
  induction m as [| m IHm]; intros r pa Hp Ha Hev.
  - cbn [iter]. replace (2 * 0 + r) with r by lia.
    split; [finish | split; [lia | split; [lia | exact Hev]]].
  - rewrite iter_S'.
    replace (2 * S m + r) with (S (S (2 * m + r))) by lia.
    destruct (Kd_step_all (2 * m + r) pa Hp Ha Hev) as [Hstep [Hp1 [Ha1 Hm1]]].
    destruct (IHm r (Kd_step pa) ltac:(lia) Ha1 Hm1) as [Hrun [Hp2 [Ha2 Hm2]]].
    split; [| split; [| split]].
    + eapply evstep_trans; [apply progress_evstep, Hstep | exact Hrun].
    + lia.
    + exact Ha2.
    + exact Hm2.
Qed.

Definition D_reload (pa : nat * nat) : nat * nat :=
  let '(p, a) := pa in
  Kc (p - 2, 2).

Lemma D_reload_all : forall pa,
  3 <= fst pa -> 2 <= snd pa -> snd pa mod 2 = 0 ->
  Ce (fst pa) (snd pa) 0 0 -->+ Ce (fst (D_reload pa)) (snd (D_reload pa)) 0 (snd pa + 1) /\
  2 <= fst (D_reload pa) /\
  2 <= snd (D_reload pa) /\
  snd (D_reload pa) mod 2 = 0.
Proof.
  intros [p a] Hp Ha Hev. cbn [fst snd D_reload] in *.
  destruct p as [| [| p']]; [lia | lia |].
  replace (S (S p') - 2) with p' by lia.
  destruct (Kc_props (p', 2) ltac:(cbn; lia) ltac:(cbn; lia) eq_refl) as [Hp1 [Ha1 Hm1]].
  cbn [fst snd] in *.
  split; [| split; [| split]].
  - eapply progress_evstep_trans; [apply D_REL |].
    apply progress_evstep.
    exact (Kc_step 0 (a + 1) (p', 2) ltac:(cbn; lia) eq_refl).
  - lia.
  - exact Ha1.
  - exact Hm1.
Qed.

(** ** The full run of M13 *)

Definition pa1 : nat * nat := Kd_step (4, 8).
Definition pa2_0 : nat * nat := D_reload pa1.
Definition pa2 : nat * nat := Kd_iter (snd pa1 / 2) pa2_0.

Lemma pa1_def : pa1 = Kd_step (4, 8). Proof. reflexivity. Qed.
Lemma pa2_0_def : pa2_0 = D_reload pa1. Proof. reflexivity. Qed.
Lemma pa2_def : pa2 = Kd_iter (snd pa1 / 2) pa2_0. Proof. reflexivity. Qed.

Opaque Kc Kd_step Kd_iter D_reload pa1 pa2_0 pa2.

Lemma run_pa1 :
  c0 -->* Ce (fst pa1) (snd pa1) 0 0 /\
  3 <= fst pa1 /\ 2 <= snd pa1 /\ snd pa1 mod 2 = 0.
Proof.
  rewrite pa1_def.
  destruct (Kd_step_all 0 (4, 8) ltac:(cbn; lia) ltac:(cbn; lia) eq_refl) as [Hstep [Hp [Ha Hm]]].
  cbn [fst snd] in *.
  split; [| split; [lia | split; [exact Ha | exact Hm]]].
  follow init_306.
  apply progress_evstep, Hstep.
Qed.

Lemma run_round2 : forall pa,
  c0 -->* Ce (fst pa) (snd pa) 0 0 /\
  3 <= fst pa /\ 2 <= snd pa /\ snd pa mod 2 = 0 ->
  c0 -->* c_end (fst (Kd_iter (snd pa / 2) (D_reload pa))) (snd (Kd_iter (snd pa / 2) (D_reload pa))).
Proof.
  intros pa [Hrun1 [Hp1 [Ha1 Hm1]]].
  destruct (D_reload_all pa Hp1 Ha1 Hm1) as [Hrel2 [Hp2_0 [Ha2_0 Hm2_0]]].
  assert (Hd2 : snd pa + 1 = 2 * (snd pa / 2) + 1) by (mods; lia).
  destruct (Kd_loop (snd pa / 2) 1 (D_reload pa) Hp2_0 Ha2_0 Hm2_0) as [Hloop2 _].
  follow Hrun1.
  eapply evstep_trans; [apply progress_evstep, Hrel2 |].
  rewrite Hd2.
  follow Hloop2.
  apply progress_evstep, HALT_step.
Qed.

Lemma run_pa2 :
  c0 -->* c_end (fst pa2) (snd pa2).
Proof.
  rewrite !pa2_def, !pa2_0_def.
  exact (run_round2 pa1 run_pa1).
Qed.

Theorem halt : halts tm c0.
Proof.
  destruct (with_counter run_pa2) as [n Hn].
  eapply halts_multistep; [| exact Hn].
  apply halted_halts. apply c_end_halted.
Qed.
