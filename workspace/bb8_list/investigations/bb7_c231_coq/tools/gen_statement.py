import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v2'))
head = r'''(** * Statement.v : what is proved about champ_231 and champ_232, in terms of Defs.v and busycoq's TM.v only (BB7/verify).

    champ_231 = 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB
    champ_232 = 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB

    To check the claims, read this file, Defs.v (the machines tm231 / tm232, the ones count, iter, U, W, arrow) and
    busycoq's verify/TM.v (commit bd2e36f: TM, tape, the step relation, c0 = (q0, tape0) with tape0 the all-blank
    tape, -[ tm ]->*, halted tm c := tm (q, s) = None, halts tm c).  Both machines halt on the undefined transition
    C1 = "---", where the head reads a 1, so their score is the number N of ones on the halted tape.

    Each theorem is proved in a line or two from C231_main.v / C232_main.v (the machine developments), Uniq.v
    (the halting configuration and its ones count are unique) and Bound.v / Bound3.v (arithmetic).
    probe231.v and probe232.v run Print Assumptions on each. *)
From BB7 Require Import Individual72.
From Coq Require Import Lia PeanoNat String Ascii.
From BB7 Require Import Defs Uniq.
From BB7 Require Bound Bound3 C231_run C232_run C231_main C232_main.
Local Open Scope nat_scope.

(** ** The tables, against the machine strings (standard format: 7 groups of 6 characters separated by "_"; the
    transition (state i, symbol j) is the three characters at 7 i + 3 j; "---" is undefined, i.e. None). *)
Definition p_sym (c : ascii) : option Sym :=
  if Ascii.eqb c "0"%char then Some S0 else if Ascii.eqb c "1"%char then Some S1 else None.
Definition p_dir (c : ascii) : option dir :=
  if Ascii.eqb c "L"%char then Some L else if Ascii.eqb c "R"%char then Some R else None.
Definition p_st (c : ascii) : option Q :=
  match c with
  | "A"%char => Some A | "B"%char => Some B | "C"%char => Some C | "D"%char => Some D | "E"%char => Some E
  | "F"%char => Some F | "G"%char => Some G | _ => None
  end.
Definition st_idx (q : Q) : nat :=
  match q with A => 0 | B => 1 | C => 2 | D => 3 | E => 4 | F => 5 | G => 6 end.
Definition sym_idx (s : Sym) : nat := match s with S0 => 0 | S1 => 1 end.

Definition parse_slot (str : string) (i j : nat) : option (Sym * dir * Q) :=
  let k := 7 * i + 3 * j in
  match String.get k str, String.get (k + 1) str, String.get (k + 2) str with
  | Some a, Some b, Some c =>
    match p_sym a, p_dir b, p_st c with
    | Some s, Some d, Some q => Some (s, d, q)
    | _, _, _ => None
    end
  | _, _, _ => None
  end.

Definition c231_string : string := "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB".
Definition c232_string : string := "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB".

'''
def sect(n):
    AND = '/' + chr(92)
    M = f'C{n}_main'
    return f'''(** ** champ_{n} *)
Theorem c{n}_table : String.length c{n}_string = 48 {AND}
  forall q s, tm{n} (q, s) = parse_slot c{n}_string (st_idx q) (sym_idx s).
Proof. split; [reflexivity |]. intros q s. destruct q, s; reflexivity. Qed.

Theorem c{n}_halts : halts tm{n} c0.
Proof. exact C{n}_run.c{n}_halts. Qed.

(** A halting configuration is reached from the blank tape, and it holds 2 * W 20 5 + 7 ones. *)
Theorem c{n}_halting_config : exists c, c0 -[ tm{n} ]->* c /\ halted tm{n} c /\ ones c (2 * W 20 5 + 7).
Proof. exact {M}.c{n}_score_exact. Qed.

(** The exact score: every halting configuration reached from the blank tape holds 2 * W 20 5 + 7 ones. *)
Theorem c{n}_score : forall c N, c0 -[ tm{n} ]->* c -> halted tm{n} c -> ones c N -> N = 2 * W 20 5 + 7.
Proof.
  destruct {M}.c{n}_score_exact as [c' [H1 [H2 H3]]]. exact (score_of tm{n} c' _ H1 H2 H3).
Qed.

(** 3 ↑^20 3 < N  (3 ↑^20 3 = 3 ↑^19 (3 ↑^19 3)). *)
Theorem c{n}_lower : forall c N, c0 -[ tm{n} ]->* c -> halted tm{n} c -> ones c N -> arrow 20 3 3 < N.
Proof. intros c N H1 H2 H3. exact (Bound3.N_lower3 N (c{n}_score c N H1 H2 H3)). Qed.

(** The BB(7) champion 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF has sigma = 3 * (2 ↑^13 3) + 22 (our
    analysis, see BB7/README.md) and the bbchallenge wiki's lower bound 2 ↑^11 (2 ↑^11 3); both are below N. *)
Theorem c{n}_beats_bb7_champion : forall c N, c0 -[ tm{n} ]->* c -> halted tm{n} c -> ones c N ->
  3 * arrow 13 2 3 + 22 < N /\ arrow 11 2 (arrow 11 2 3) < N.
Proof.
  intros c N H1 H2 H3.
  destruct (Bound.N_lower N (c{n}_score c N H1 H2 H3)) as [_ [_ [_ [L4 L5]]]]. split; assumption.
Qed.

'''
open('Statement.v', 'w', encoding='utf-8', newline='\n').write(head + sect(231) + sect(232))
for n in (231, 232):
    names = [f'c{n}_table', f'c{n}_halts', f'c{n}_halting_config', f'c{n}_score', f'c{n}_lower', f'c{n}_beats_bb7_champion']
    p = f'''(** probe{n}.v : the champ_{n} statements of Statement.v, their assumptions, and the definitions they use. *)
From BB7 Require Import Individual72 Defs Statement.

''' + ''.join(f'Print Assumptions {x}.\n' for x in names) + ''.join(f'Check {x}.\n' for x in names) + f'''Print tm{n}.
Print ones. Print count1. Print sym_val.
Print iter. Print UW. Print U. Print W. Print arrow.
Print c0. Print tape0.
Print c{n}_string. Print parse_slot.
'''
    open(f'probe{n}.v', 'w', encoding='utf-8', newline='\n').write(p)
