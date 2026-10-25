# gen_coq.py CERT OUT.v [fuel] : write the busycoq proof file for an ngann certificate (ANN=2, GON=1).
# Only the learned state sets S_L and S_R are embedded; Coq recomputes predecessor lists and the configuration set.
import sys
cert, out = sys.argv[1], sys.argv[2]
fuel = int(sys.argv[3]) if len(sys.argv) > 3 else 17
L = open(cert).read().split('\n')
kL, kR, ann, gon = map(int, L[0].split()[1:])
assert ann == 2 and gon == 1
SL, SR, nC = [], [], 0
for l in L[1:]:
    p = l.split()
    if not p:
        continue
    if p[0] == 'S':
        (SL if p[1] == '0' else SR).append(int(p[2]))
    elif p[0] == 'C':
        nC += 1
assert (1 << fuel) >= nC, 'fuel too small'

def nlist(name, xs):
    lines, cur = [], []
    for x in xs:
        cur.append(str(x))
        if len(cur) == 8:
            lines.append('  ' + '; '.join(cur) + ';')
            cur = []
    if cur:
        lines.append('  ' + '; '.join(cur))
    body = '\n'.join(lines).rstrip(';')
    return f'Definition {name} : list N := [\n{body}]%N.\n'

head = r'''(** * BB(8) m7-subtree machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE never halts *)

(** Formalization of [bb8_list/investigations/bb8_m7_1RB0RA_1RG0LC.md] (Opus continuation).

    The machine (E0 = 1RG) runs the BB(7) champion's digit-list recursion like its siblings E0 = 0RB and E0 = 1LG,
    but a plain n-gram closed position set cannot close it: the n-gram abstraction forgets which barrier (a run of
    two or more 1s) separates the head from a tape end, and the "G0 H1 E0" sweep then reaches the end and halts.
    This proof uses a closed set of local configurations over an enriched tape alphabet:

    - **Writer annotations (ghost).**  Every cell carries, besides its symbol, the state that last wrote it (or
      "never written").  A cell is coded as [c = bit + 2 * a], with [a = 0] for "never written" and [a = 1 + i]
      for the i-th state [A..H]; [CODES] lists the 18 codes.  The annotations are existentially quantified in the
      invariant, so they need not be tracked by the real machine.
    - **Side automata.**  A half-tape (nearest cell first) is abstracted by an automaton state, a number [N]:
      its first [kL] = 8 (left) or [kR] = 6 (right) annotated cells, 5 bits each.  The right state also carries
      [g], the set of states whose right-moving run from the first cell of that side halts before turning
      ([gstep]); this is what remembers whether a G/F/H/E sweep would run off the end of the tape.
      [foldL] / [foldR] push one coded cell onto the near end of a side (deterministic).
    - **[run fold S s r]**: side [r] has state [s] if there are states [f i] and codes [cs i] with [f 0 = s] and,
      for every [i], [f (S i)] in the learned set [S], [cs i] a code whose bit is [Str_nth i r], and
      [fold (f (S i)) (cs i) = f i].
    - **The invariant [Inv]** of a configuration [(q, (l, m, r))]: there are side states [a], [b] with
      [(q, m, a, b)] in the set [C] of local configurations, [run foldL SL a l] and [run foldR SR b r].
    - [check] verifies: predecessor lists are complete for the learned sets ([preds_complete]); the blank start is
      in [C]; and every member of [C] has a defined transition, folds only learned states, and steps into [C] for
      every learned predecessor of the side it moves into.  [inv_step] proves that a successful [check] makes
      [Inv] closed under steps of [tm]; [check_ok] runs [check] by [vm_compute].

    The learned sets [SL] (__NSL__ states) and [SR] (__NSR__ states) are embedded as data; the predecessor lists and
    [C] (__NC__ local configurations, computed by [bsearch] from the blank tape) are recomputed inside Coq.
    The certificate was found by [investigations/bb8_m7_1RB0RA_1RG0LC/opus/ngann.cpp] (arguments 8 6 2 1).
    Without [g] (any window up to 8/8), or without annotations (n-gram windows up to 16/16), the search reaches a
    halting local configuration. *)

From BB8 Require Import Individual82.
From Coq Require Import Lists.List Lists.Streams Bool PArith NArith.
From Coq Require Import FSets.FMapPositive.
Import ListNotations.
Set Default Goal Selector "!".

(* machine: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, R, B)  | A, 1 => Some (0, R, A)
  | B, 0 => Some (1, L, C)  | B, 1 => Some (1, L, F)
  | C, 0 => Some (1, R, D)  | C, 1 => Some (0, L, B)
  | D, 0 => Some (1, R, A)  | D, 1 => Some (1, L, E)
  | E, 0 => Some (1, R, G)  | E, 1 => Some (0, L, C)
  | F, 0 => Some (1, R, G)  | F, 1 => Some (1, L, D)
  | G, 0 => Some (0, R, H)  | G, 1 => Some (0, R, F)
  | H, 0 => None            | H, 1 => Some (0, R, E)
  end.

Module PM := PositiveMap.

(** ** Cell codes *)

Definition qidx (q : Q) : N :=
  match q with A => 0 | B => 1 | C => 2 | D => 3 | E => 4 | F => 5 | G => 6 | H => 7 end%N.

Definition symN (s : Sym) : N := match s with S0 => 0%N | S1 => 1%N end.

Definition cbit (c : N) : Sym := if N.odd c then S1 else S0.

(** The code of a cell written with symbol [w] by state [q]. *)
Definition wcode (w : Sym) (q : Q) : N := (symN w + 2 * (1 + qidx q))%N.

Definition CODES : list N := [0; 1; 2; 3; 4; 5; 6; 7; 8; 9; 10; 11; 12; 13; 14; 15; 16; 17]%N.

Lemma wcode_in : forall w q, In (wcode w q) CODES.
Proof. intros [] []; cbn; tauto. Qed.

Lemma cbit_wcode : forall w q, cbit (wcode w q) = w.
Proof. intros [] []; reflexivity. Qed.

Lemma cbit_0 : cbit 0%N = S0.
Proof. reflexivity. Qed.

(** ** Side automata (generic part) *)

Lemma pred_succ_pos : forall n, Pos.pred_N (N.succ_pos n) = n.
Proof. intros [| p]; [reflexivity | apply Pos.pred_N_succ]. Qed.

Lemma Str_nth_const : forall i (x : Sym), Str_nth i (const x) = x.
Proof.
  intros i x. unfold Str_nth.
  assert (Ht : forall j, Str_nth_tl j (const x) = const x) by (induction j; [reflexivity | exact IHj]).
  rewrite Ht. reflexivity.
Qed.

Section Automaton.

Variable fold : N -> N -> N.
Variable SM : PM.t unit.
Variable PR : PM.t (list (N * N)).

Definition smem (s : N) : bool := PM.mem (N.succ_pos s) SM.

Definition preds (s : N) : list (N * N) :=
  match PM.find (N.succ_pos s) PR with Some l => l | None => [] end.

Definition run (s : N) (r : Stream Sym) : Prop :=
  exists (f : nat -> N) (cs : nat -> N), f O = s /\
    forall i, smem (f (S i)) = true /\ In (cs i) CODES /\ cbit (cs i) = Str_nth i r /\ fold (f (S i)) (cs i) = f i.

(** Every learned state [s] and code [c] is recorded as a predecessor of [fold s c]. *)
Definition preds_complete : bool :=
  forallb (fun kv => let s := Pos.pred_N (fst kv) in
    forallb (fun c => existsb (fun pc => N.eqb (fst pc) c && N.eqb (snd pc) s) (preds (fold s c))) CODES)
    (PM.elements SM).

Lemma run_unfold : preds_complete = true -> forall s r, run s r ->
  exists c s', In (c, s') (preds s) /\ cbit c = hd r /\ run s' (tl r).
Proof.
  intros Hpc s r [f [cs [Hf0 Hf]]].
  destruct (Hf O) as [Hm [Hc [Hb Hfo]]].
  exists (cs O), (f 1%nat). split; [| split].
  - unfold smem in Hm. rewrite PM.mem_find in Hm.
    destruct (PM.find (N.succ_pos (f 1%nat)) SM) as [u |] eqn:Efind; [| discriminate].
    apply PM.elements_correct in Efind.
    unfold preds_complete in Hpc. rewrite forallb_forall in Hpc.
    specialize (Hpc _ Efind). cbv beta zeta in Hpc. cbn [fst] in Hpc. rewrite pred_succ_pos in Hpc.
    rewrite forallb_forall in Hpc. specialize (Hpc _ Hc).
    rewrite existsb_exists in Hpc. destruct Hpc as [[c' s'] [Hin Heq]].
    cbn [fst snd] in Heq. rewrite andb_true_iff, !N.eqb_eq in Heq. destruct Heq as [-> ->].
    rewrite Hfo, Hf0 in Hin. exact Hin.
  - rewrite Hb. reflexivity.
  - exists (fun i => f (S i)), (fun i => cs (S i)). split; [reflexivity |].
    intros i. exact (Hf (S i)).
Qed.

Lemma run_fold : forall s r c, smem s = true -> In c CODES -> run s r -> run (fold s c) (cbit c >> r).
Proof.
  intros s r c Hs Hc [f [cs [Hf0 Hf]]].
  exists (fun i => match i with O => fold s c | S j => f j end),
         (fun i => match i with O => c | S j => cs j end).
  split; [reflexivity |].
  intros [| i].
  - cbn. rewrite Hf0. split; [exact Hs | split; [exact Hc | split; reflexivity]].
  - exact (Hf i).
Qed.

Lemma run_const : forall z, smem z = true -> fold z 0%N = z -> run z (const S0).
Proof.
  intros z Hz Hfz. exists (fun _ : nat => z), (fun _ : nat => 0%N). split; [reflexivity |].
  intros i. rewrite Str_nth_const. repeat split; [assumption | cbn; tauto | assumption].
Qed.

End Automaton.

Definition mkset (ss : list N) : PM.t unit :=
  fold_left (fun m s => PM.add (N.succ_pos s) tt m) ss (PM.empty unit).

Definition mkpreds (fold : N -> N -> N) (ss : list N) : PM.t (list (N * N)) :=
  fold_left (fun m s => fold_left (fun m c =>
      let k := N.succ_pos (fold s c) in
      PM.add k ((c, s) :: match PM.find k m with Some l => l | None => [] end) m) CODES m)
    ss (PM.empty _).

(** ** The two side automata *)

Definition kL : N := __KL__%N.
Definition kR : N := __KR__%N.
Definition wL : N := (N.shiftl 1 (5 * kL) - 1)%N.
Definition wR : N := (N.shiftl 1 (5 * kR) - 1)%N.

(** [gstep g x]: the states whose right-moving run halts before turning, on a side whose first cell is [x] and
    whose remaining cells give the set [g]. *)
Definition gstep (g : N) (x : Sym) : N :=
  fold_left (fun acc X =>
    if match tm (X, x) with
       | None => true
       | Some (_, R, Y) => N.testbit g (qidx Y)
       | Some (_, L, _) => false
       end
    then N.lor acc (N.shiftl 1 (qidx X)) else acc) [A; B; C; D; E; F; G; H] 0%N.

Definition foldL (s c : N) : N := N.land (N.lor (N.shiftl (N.land s wL) 5) c) wL.
Definition foldR (s c : N) : N :=
  N.lor (N.land (N.lor (N.shiftl (N.land s wR) 5) c) wR)
        (N.shiftl (gstep (N.land (N.shiftr s 55) 255) (cbit c)) 55).

Definition gblank : N := Nat.iter 9 (fun g => gstep g S0) 0%N.
Definition zL : N := 0%N.
Definition zR : N := N.shiftl gblank 55.

(** ** Local configurations *)

Definition tup : Type := (Q * Sym * N * N)%type.

Definition keyt (t : tup) : positive :=
  match t with (q, m, a, b) => N.succ_pos (2 * qidx q + symN m + 16 * (b + N.shiftl a 64))%N end.

Definition tup_eqb (t1 t2 : tup) : bool :=
  match t1, t2 with
  | (q1, m1, a1, b1), (q2, m2, a2, b2) =>
    N.eqb (qidx q1) (qidx q2) && N.eqb (symN m1) (symN m2) && N.eqb a1 a2 && N.eqb b1 b2
  end.

Lemma tup_eqb_eq : forall t1 t2, tup_eqb t1 t2 = true -> t1 = t2.
Proof.
  intros [[[q1 m1] a1] b1] [[[q2 m2] a2] b2] Hq. cbn in Hq.
  rewrite !andb_true_iff, !N.eqb_eq in Hq. destruct Hq as [[[Hq Hm] Ha] Hb]. subst.
  destruct q1, q2; try discriminate; destruct m1, m2; try discriminate; reflexivity.
Qed.

Definition cmem (Cm : PM.t tup) (t : tup) : bool :=
  match PM.find (keyt t) Cm with Some t' => tup_eqb t' t | None => false end.

Lemma cmem_find : forall Cm t, cmem Cm t = true -> PM.find (keyt t) Cm = Some t.
Proof.
  intros Cm t Ht. unfold cmem in Ht.
  destruct (PM.find (keyt t) Cm) as [t' |] eqn:E; [| discriminate].
  apply tup_eqb_eq in Ht. subst. reflexivity.
Qed.

Section Check.

Variables SL SR : PM.t unit.
Variables PL PR : PM.t (list (N * N)).

Definition succ_ok (Cm : PM.t tup) (t : tup) : bool :=
  match t with
  | (q, m, a, b) =>
    match tm (q, m) with
    | None => false
    | Some (w, R, q') =>
      smem SL a && forallb (fun cs => cmem Cm (q', cbit (fst cs), foldL a (wcode w q), snd cs)) (preds PR b)
    | Some (w, L, q') =>
      smem SR b && forallb (fun cs => cmem Cm (q', cbit (fst cs), snd cs, foldR b (wcode w q))) (preds PL a)
    end
  end.

Definition check (Cm : PM.t tup) : bool :=
  preds_complete foldL SL PL && preds_complete foldR SR PR &&
  smem SL zL && smem SR zR && N.eqb (foldL zL 0%N) zL && N.eqb (foldR zR 0%N) zR &&
  cmem Cm (A, S0, zL, zR) &&
  forallb (fun kv => succ_ok Cm (snd kv)) (PM.elements Cm).

Definition Inv (Cm : PM.t tup) (c : Q * tape) : Prop :=
  match c with
  | (q, (l, m, r)) => exists a b, cmem Cm (q, m, a, b) = true /\ run foldL SL a l /\ run foldR SR b r
  end.

Lemma inv_step : forall Cm, check Cm = true ->
  forall c, Inv Cm c -> exists c', Inv Cm c' /\ c -[ tm ]->+ c'.
Proof.
  intros Cm Hc [q [[l m] r]] [a [b [HC [HL HR]]]].
  unfold check in Hc. rewrite !andb_true_iff in Hc.
  destruct Hc as [[[[[[[HpL HpR] _] _] _] _] _] Hall].
  rewrite forallb_forall in Hall.
  assert (Hok : succ_ok Cm (q, m, a, b) = true).
  { apply cmem_find in HC. apply PM.elements_correct in HC. exact (Hall _ HC). }
  cbv beta iota zeta delta [succ_ok] in Hok.
  destruct (tm (q, m)) as [[[w d] q'] |] eqn:Etm; [| discriminate].
  destruct d; cbv beta iota zeta in Hok; rewrite andb_true_iff in Hok; destruct Hok as [Hs Hfa];
    rewrite forallb_forall in Hfa.
  - (* left move: new configuration (tl l, hd l, w >> r) *)
    destruct (run_unfold _ _ _ HpL _ _ HL) as [c' [s' [Hin [Hbit Hrun]]]].
    exists (q', (tl l, hd l, w >> r)). split.
    2: { apply progress_base. exact (@step_left tm q q' m w l r Etm). }
    exists s', (foldR b (wcode w q)). split; [| split].
    + specialize (Hfa _ Hin). cbn [fst snd] in Hfa. rewrite Hbit in Hfa. exact Hfa.
    + exact Hrun.
    + replace (w >> r) with (cbit (wcode w q) >> r) by (rewrite cbit_wcode; reflexivity).
      apply run_fold; [exact Hs | apply wcode_in | exact HR].
  - (* right move: new configuration (w >> l, hd r, tl r) *)
    destruct (run_unfold _ _ _ HpR _ _ HR) as [c' [s' [Hin [Hbit Hrun]]]].
    exists (q', (w >> l, hd r, tl r)). split.
    2: { apply progress_base. exact (@step_right tm q q' m w l r Etm). }
    exists (foldL a (wcode w q)), s'. split; [| split].
    + specialize (Hfa _ Hin). cbn [fst snd] in Hfa. rewrite Hbit in Hfa. exact Hfa.
    + replace (w >> l) with (cbit (wcode w q) >> l) by (rewrite cbit_wcode; reflexivity).
      apply run_fold; [exact Hs | apply wcode_in | exact HL].
    + exact Hrun.
Qed.

Lemma inv_init : forall Cm, check Cm = true -> Inv Cm c0.
Proof.
  intros Cm Hc. unfold check in Hc. rewrite !andb_true_iff in Hc.
  destruct Hc as [[[[[[[_ _] HzL] HzR] HfL] HfR] H0] _].
  rewrite N.eqb_eq in HfL, HfR.
  change (exists a b, cmem Cm (A, S0, a, b) = true /\ run foldL SL a (const S0) /\ run foldR SR b (const S0)).
  exists zL, zR. split; [exact H0 | split; apply run_const; assumption].
Qed.

Theorem nonhalt_of_check : forall Cm, check Cm = true -> ~ halts tm c0.
Proof.
  intros Cm Hc.
  apply progress_nonhalt with (P := Inv Cm).
  - apply inv_step, Hc.
  - apply inv_init, Hc.
Qed.

(** ** Computing the local-configuration set (untrusted: [check] verifies the result) *)

Definition succs (t : tup) : list tup :=
  match t with
  | (q, m, a, b) =>
    match tm (q, m) with
    | None => []
    | Some (w, R, q') => List.map (fun cs => (q', cbit (fst cs), foldL a (wcode w q), snd cs)) (preds PR b)
    | Some (w, L, q') => List.map (fun cs => (q', cbit (fst cs), snd cs, foldR b (wcode w q))) (preds PL a)
    end
  end.

Definition bst : Type := (PM.t tup * list tup)%type.

Definition bstep (s : bst) : bst :=
  match s with
  | (Cm, []) => s
  | (Cm, t :: rest) =>
    fold_left (fun (acc : bst) t' => let (Cm', Qu) := acc in
                 if cmem Cm' t' then acc else (PM.add (keyt t') t' Cm', t' :: Qu))
              (succs t) (Cm, rest)
  end.

Fixpoint biter (n : nat) (s : bst) : bst :=
  match n with
  | O => bstep s
  | S n' => biter n' (biter n' s)
  end.

Definition bsearch (fuel : nat) : PM.t tup :=
  let t0 : tup := (A, S0, zL, zR) in
  fst (biter fuel (PM.add (keyt t0) t0 (PM.empty tup), [t0])).

End Check.

(** ** The certificate: learned side states *)

'''

tail = r'''
Definition SLm := mkset SLlist.
Definition SRm := mkset SRlist.
Definition PLm := mkpreds foldL SLlist.
Definition PRm := mkpreds foldR SRlist.

Lemma check_ok : check SLm SRm PLm PRm (bsearch PLm PRm __FUEL__) = true.
Proof. vm_compute. reflexivity. Qed.

Theorem nonhalt : ~ halts tm c0.
Proof. exact (nonhalt_of_check _ _ _ _ _ check_ok). Qed.
'''

text = head.replace('__NSL__', str(len(SL))).replace('__NSR__', str(len(SR))).replace('__NC__', f'{nC:,}')
text = text.replace('__KL__', str(kL)).replace('__KR__', str(kR))
text += nlist('SLlist', SL) + '\n' + nlist('SRlist', SR) + tail.replace('__FUEL__', str(fuel))
open(out, 'w', newline='\n').write(text)
print('wrote', out, len(text), 'bytes; |SL| =', len(SL), '|SR| =', len(SR), 'C =', nC, 'fuel =', fuel)
