"""gen_ngcps_v.py CERT OUT.v [FUEL]: write a self-contained busycoq proof that the m7 machine never halts,
by a verified n-gram closed-position-set check (window sets LS/RS embedded as data, the local-configuration set
recomputed inside Coq by a breadth-first search and checked by [check], whose soundness is proved)."""
import sys
cert, out = sys.argv[1], sys.argv[2]
fuel = int(sys.argv[3]) if len(sys.argv) > 3 else 23
lines = open(cert).read().split('\n')
nL, nR = map(int, lines[0].split())
LS = [int(l.split()[1]) for l in lines[1:] if l.startswith('L ')]
RS = [int(l.split()[1]) for l in lines[1:] if l.startswith('R ')]
def keys(ws, n):  # Coq key of a window: enc (win n s) xH = 2^n + window bits (bit 0 = nearest cell)
    return [(1 << n) | w for w in ws]
def plist(ks):
    out, cur = [], ''
    for k in ks:
        s = str(k) + '; '
        if len(cur) + len(s) > 110: out.append(cur.rstrip()); cur = ''
        cur += s
    out.append(cur.rstrip().rstrip(';'))
    return '\n  '.join(out)

V = r'''(** * BB(8) m7-subtree machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE never halts *)

(** Formalization of [bb8_list/investigations/bb8_m7_1RB0RA_0RB0LC.md].

    The machine runs the BB(7) champion's digit-list recursion, rebuilds a degraded list when the champion
    would halt, and repeats this in an unbounded tower of epochs.  Its only undefined transition is H reading 0.
    Instead of following the epochs, this proof uses a closed set of local configurations (an n-gram closed
    position set, "NGramCPS"):

    - [LS] is a set of left windows (the [nL] = %(nL)d cells left of the head, nearest first) and [RS] a set of
      right windows (the [nR] = %(nR)d cells right of the head).  Both are embedded below as data.
    - [C] is a set of local configurations (state, scanned symbol, left window, right window).  It is computed
      inside Coq by a search from the blank tape ([bsearch]).
    - The invariant [Inv] of a configuration says: every length-[nL] window of the left side, at every offset,
      lies in [LS]; likewise every length-[nR] window of the right side lies in [RS]; and the local configuration
      lies in [C].
    - [check] verifies that [C] contains the blank start, that no member of [C] is halting, and that every
      member's successors (for both possible values of the cell that enters the far end of the window) are
      in [C] and add only windows in [LS]/[RS].  [inv_step] proves that a successful [check] makes [Inv]
      closed under steps of [tm]; [check_ok] runs [check] by [vm_compute].

    The window lengths %(nL)d/%(nR)d were found by a scan over lengths; shorter windows reach a halting local
    configuration (for example 10/13, 9/14, 14/10, and every symmetric length up to 13), while 10/14 closes with
    about 2.9 million local configurations. *)

From BB8 Require Import Individual82.
From Coq Require Import Lists.List Lists.Streams Bool PArith.
From Coq Require Import FSets.FMapPositive.
Import ListNotations.
Set Default Goal Selector "!".

(* machine: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, R, B)  | A, 1 => Some (0, R, A)
  | B, 0 => Some (1, L, C)  | B, 1 => Some (1, L, F)
  | C, 0 => Some (1, R, D)  | C, 1 => Some (0, L, B)
  | D, 0 => Some (1, R, A)  | D, 1 => Some (1, L, E)
  | E, 0 => Some (0, R, B)  | E, 1 => Some (0, L, C)
  | F, 0 => Some (1, R, G)  | F, 1 => Some (1, L, D)
  | G, 0 => Some (0, R, H)  | G, 1 => Some (0, R, F)
  | H, 0 => None            | H, 1 => Some (0, R, E)
  end.

Module PM := PositiveMap.

(** ** Windows and their encoding *)

(** The first [n] cells of a side, nearest to the head first. *)
Fixpoint win (n : nat) (s : Stream Sym) : list Sym :=
  match n with
  | O => []
  | S n' => hd s :: win n' (tl s)
  end.

(** A list of symbols as a positive number (first element = lowest bit) on top of [acc]. *)
Fixpoint enc (xs : list Sym) (acc : positive) : positive :=
  match xs with
  | [] => acc
  | S0 :: t => xO (enc t acc)
  | S1 :: t => xI (enc t acc)
  end.

Fixpoint dec (n : nat) (p : positive) : list Sym * positive :=
  match n with
  | O => ([], p)
  | S n' =>
    match p with
    | xO p' => let (t, r) := dec n' p' in (S0 :: t, r)
    | xI p' => let (t, r) := dec n' p' in (S1 :: t, r)
    | xH => ([], xH)
    end
  end.

Lemma dec_enc : forall xs acc, dec (length xs) (enc xs acc) = (xs, acc).
Proof.
  induction xs as [| x xs IH]; intros acc; [reflexivity |].
  destruct x; simpl; rewrite IH; reflexivity.
Qed.

Definition qbits (q : Q) : list Sym :=
  match q with
  | A => [0; 0; 0] | B => [1; 0; 0] | C => [0; 1; 0] | D => [1; 1; 0]
  | E => [0; 0; 1] | F => [1; 0; 1] | G => [0; 1; 1] | H => [1; 1; 1]
  end.

Definition qof (xs : list Sym) : Q :=
  match xs with
  | [0; 0; 0] => A | [1; 0; 0] => B | [0; 1; 0] => C | [1; 1; 0] => D
  | [0; 0; 1] => E | [1; 0; 1] => F | [0; 1; 1] => G | _ => H
  end.

Lemma qof_qbits : forall q, qof (qbits q) = q.
Proof. destruct q; reflexivity. Qed.

Definition tup : Type := Q * Sym * list Sym * list Sym.

Definition key (q : Q) (m : Sym) (lw rw : list Sym) : positive :=
  enc lw (enc rw (enc (m :: qbits q) xH)).

Definition keyt (t : tup) : positive :=
  match t with (q, m, lw, rw) => key q m lw rw end.

Definition memw (xs : list Sym) (S : PM.t unit) : bool := PM.mem (enc xs xH) S.

Section Check.

Variables nL' nR' : nat.
Let nL := S nL'.
Let nR := S nR'.

Definition decode (k : positive) : tup :=
  let (lw, k1) := dec nL k in
  let (rw, k2) := dec nR k1 in
  let (qm, _) := dec 4%%nat k2 in
  match qm with
  | m :: qb => (qof qb, m, lw, rw)
  | [] => (A, S0, lw, rw)
  end.

Lemma decode_key : forall q m lw rw,
  length lw = nL -> length rw = nR -> decode (key q m lw rw) = (q, m, lw, rw).
Proof.
  intros q m lw rw Hl Hr. unfold decode, key.
  rewrite <- Hl, dec_enc. cbv beta iota zeta.
  rewrite <- Hr, dec_enc. cbv beta iota zeta.
  assert (Hq : length (m :: qbits q) = 4%%nat) by (destruct q; reflexivity).
  rewrite <- Hq, dec_enc. cbv beta iota zeta.
  rewrite qof_qbits. reflexivity.
Qed.

(** The successors of a local configuration: for a right move the new right window gets one unknown cell
    [x] at its far end; only windows in [RS] can occur (symmetrically for left moves). *)
Definition succ_ok (LS RS C : PM.t unit) (q : Q) (m : Sym) (lw rw : list Sym) : bool :=
    match tm (q, m) with
    | None => false
    | Some (w, R, q') =>
      let nl := w :: removelast lw in
      memw nl LS &&
      match rw with
      | [] => false
      | nm :: rr => forallb (fun x => negb (memw (rr ++ [x]) RS) || PM.mem (key q' nm nl (rr ++ [x])) C) [0; 1]
      end
    | Some (w, L, q') =>
      let nr := w :: removelast rw in
      memw nr RS &&
      match lw with
      | [] => false
      | nm :: lr => forallb (fun x => negb (memw (lr ++ [x]) LS) || PM.mem (key q' nm (lr ++ [x]) nr) C) [0; 1]
      end
    end.

Definition check (LS RS C : PM.t unit) : bool :=
  memw (repeat 0 nL) LS && memw (repeat 0 nR) RS && PM.mem (key A 0 (repeat 0 nL) (repeat 0 nR)) C &&
  forallb (fun kv => let '(q, m, lw, rw) := decode (fst kv) in succ_ok LS RS C q m lw rw) (PM.elements C).

Definition Inv (LS RS C : PM.t unit) (c : Q * tape) : Prop :=
  match c with
  | (q, (l, m, r)) =>
    (forall i, memw (win nL (Str_nth_tl i l)) LS = true) /\
    (forall i, memw (win nR (Str_nth_tl i r)) RS = true) /\
    PM.mem (key q m (win nL l) (win nR r)) C = true
  end.

Lemma win_length : forall n s, length (win n s) = n.
Proof. induction n; intros s; simpl; [reflexivity | rewrite IHn; reflexivity]. Qed.

Lemma win_removelast : forall n s, win n s = removelast (win (S n) s).
Proof.
  induction n as [| n IH]; intros s; [reflexivity |].
  change (win (S n) s) with (hd s :: win n (tl s)).
  change (win (S (S n)) s) with (hd s :: win (S n) (tl s)).
  rewrite (IH (tl s)).
  change (win (S n) (tl s)) with (hd (tl s) :: win n (tl (tl s))).
  reflexivity.
Qed.

Lemma win_snoc : forall n s, win (S n) s = win n s ++ [Str_nth n s].
Proof.
  induction n as [| n IH]; intros s; [reflexivity |].
  change (win (S (S n)) s) with (hd s :: win (S n) (tl s)).
  rewrite IH. reflexivity.
Qed.

Lemma win_const : forall n, win n (const 0) = repeat 0 n.
Proof. induction n; [reflexivity | simpl; rewrite IHn; reflexivity]. Qed.

Lemma nth_tl_const : forall i, Str_nth_tl i (const 0) = const 0.
Proof. induction i; [reflexivity | simpl; exact IHi]. Qed.

Lemma pick : forall (P : Sym -> bool) x, forallb P [0; 1] = true -> P x = true.
Proof. intros P x H. simpl in H. destruct (P 0) eqn:E0, (P 1) eqn:E1; try discriminate. destruct x; assumption. Qed.

Lemma inv_step : forall LS RS C, check LS RS C = true ->
  forall c, Inv LS RS C c -> exists c', Inv LS RS C c' /\ c -[ tm ]->+ c'.
Proof.
  intros LS RS C Hc [q [[l m] r]] [HL [HR HC]].
  unfold check in Hc. rewrite !andb_true_iff in Hc. destruct Hc as [[[_ _] _] Hall].
  rewrite forallb_forall in Hall.
  assert (Hin : In (key q m (win nL l) (win nR r), tt) (PM.elements C)).
  { apply PM.elements_correct. rewrite PM.mem_find in HC.
    destruct (PM.find _ C) as [[] |]; [reflexivity | discriminate]. }
  pose proof (Hall _ Hin) as Hs.
  change ((let '(q0, m0, lw, rw) := decode (key q m (win nL l) (win nR r)) in succ_ok LS RS C q0 m0 lw rw) = true) in Hs.
  rewrite decode_key in Hs by apply win_length.
  change (succ_ok LS RS C q m (win nL l) (win nR r) = true) in Hs.
  unfold succ_ok in Hs.
  destruct (tm (q, m)) as [[[w d] q'] |] eqn:Etm; [| discriminate].
  destruct d; cbv beta iota zeta in Hs; rewrite andb_true_iff in Hs; destruct Hs as [Hw Hx].
  - (* left move: new configuration (tl l, hd l, w >> r) *)
    exists (q', (tl l, hd l, w >> r)). split.
    2: { apply progress_base. exact (@step_left tm q q' m w l r Etm). }
    split; [| split].
    + intros i. exact (HL (S i)).
    + intros [| i].
      * change (win nR (Str_nth_tl 0 (w >> r))) with (w :: win nR' r).
        rewrite (win_removelast nR' r). exact Hw.
      * exact (HR i).
    + change (win nL l) with (hd l :: win nL' (tl l)) in Hx. cbv beta iota in Hx.
      pose proof (pick _ (Str_nth nL' (tl l)) Hx) as Hp. cbv beta in Hp.
      rewrite <- win_snoc in Hp.
      assert (H1 : memw (win (S nL') (tl l)) LS = true) by exact (HL 1%%nat).
      rewrite H1 in Hp. cbn [negb orb] in Hp.
      change (win nR (w >> r)) with (w :: win nR' r). rewrite (win_removelast nR' r). exact Hp.
  - (* right move: new configuration (w >> l, hd r, tl r) *)
    exists (q', (w >> l, hd r, tl r)). split.
    2: { apply progress_base. exact (@step_right tm q q' m w l r Etm). }
    split; [| split].
    + intros [| i].
      * change (win nL (Str_nth_tl 0 (w >> l))) with (w :: win nL' l).
        rewrite (win_removelast nL' l). exact Hw.
      * exact (HL i).
    + intros i. exact (HR (S i)).
    + change (win nR r) with (hd r :: win nR' (tl r)) in Hx. cbv beta iota in Hx.
      pose proof (pick _ (Str_nth nR' (tl r)) Hx) as Hp. cbv beta in Hp.
      rewrite <- win_snoc in Hp.
      assert (H1 : memw (win (S nR') (tl r)) RS = true) by exact (HR 1%%nat).
      rewrite H1 in Hp. cbn [negb orb] in Hp.
      change (win nL (w >> l)) with (w :: win nL' l). rewrite (win_removelast nL' l). exact Hp.
Qed.

Lemma inv_init : forall LS RS C, check LS RS C = true -> Inv LS RS C c0.
Proof.
  intros LS RS C Hc. unfold check in Hc. rewrite !andb_true_iff in Hc.
  destruct Hc as [[[H0 H1] H2] _].
  change ((forall i, memw (win nL (Str_nth_tl i (const 0))) LS = true) /\
          (forall i, memw (win nR (Str_nth_tl i (const 0))) RS = true) /\
          PM.mem (key A 0 (win nL (const 0)) (win nR (const 0))) C = true).
  split; [| split].
  - intros i. rewrite nth_tl_const, win_const. exact H0.
  - intros i. rewrite nth_tl_const, win_const. exact H1.
  - rewrite !win_const. exact H2.
Qed.

Theorem nonhalt_of_check : forall LS RS C, check LS RS C = true -> ~ halts tm c0.
Proof.
  intros LS RS C Hc.
  apply progress_nonhalt with (P := Inv LS RS C).
  - apply inv_step, Hc.
  - apply inv_init, Hc.
Qed.

(** ** Computing the local-configuration set (untrusted: [check] verifies the result) *)

Definition succs (LS RS : PM.t unit) (t : tup) : list tup :=
  match t with
  | (q, m, lw, rw) =>
    match tm (q, m) with
    | None => []
    | Some (w, R, q') =>
      let nl := w :: removelast lw in
      match rw with
      | [] => []
      | nm :: rr => List.map (fun x => (q', nm, nl, rr ++ [x])) (List.filter (fun x => memw (rr ++ [x]) RS) [0; 1])
      end
    | Some (w, L, q') =>
      let nr := w :: removelast rw in
      match lw with
      | [] => []
      | nm :: lr => List.map (fun x => (q', nm, lr ++ [x], nr)) (List.filter (fun x => memw (lr ++ [x]) LS) [0; 1])
      end
    end
  end.

Definition bst : Type := (PM.t unit * list tup)%%type.

Definition bstep (LS RS : PM.t unit) (s : bst) : bst :=
  match s with
  | (Cm, []) => s
  | (Cm, t :: rest) =>
    fold_left (fun (acc : bst) t' => let (Cm', Qu) := acc in
                 if PM.mem (keyt t') Cm' then acc else (PM.add (keyt t') tt Cm', t' :: Qu))
              (succs LS RS t) (Cm, rest)
  end.

Fixpoint biter (n : nat) (LS RS : PM.t unit) (s : bst) : bst :=
  match n with
  | O => bstep LS RS s
  | S n' => biter n' LS RS (biter n' LS RS s)
  end.

Definition bsearch (fuel : nat) (LS RS : PM.t unit) : PM.t unit :=
  let t0 : tup := (A, S0, repeat 0 nL, repeat 0 nR) in
  fst (biter fuel LS RS (PM.add (keyt t0) tt (PM.empty unit), [t0])).

End Check.

(** ** The certificate: window sets *)

Definition of_keys (ks : list positive) : PM.t unit := fold_left (fun m k => PM.add k tt m) ks (PM.empty unit).

Definition LSkeys : list positive := [
  %(LS)s]%%positive.

Definition RSkeys : list positive := [
  %(RS)s]%%positive.

Definition LSm := of_keys LSkeys.
Definition RSm := of_keys RSkeys.

Lemma check_ok : check %(nL1)d %(nR1)d LSm RSm (bsearch %(nL1)d %(nR1)d %(fuel)d LSm RSm) = true.
Proof. vm_compute. reflexivity. Qed.

Theorem nonhalt : ~ halts tm c0.
Proof. exact (nonhalt_of_check _ _ _ _ _ check_ok). Qed.
''' % dict(nL=nL, nR=nR, nL1=nL - 1, nR1=nR - 1, fuel=fuel, LS=plist(keys(LS, nL)), RS=plist(keys(RS, nR)))
open(out, 'w', encoding='utf-8').write(V)
print('wrote', out, len(V), 'bytes')
