# Machine-checked score lower bound for the 35-digit BB(8) champion-rule machine

Machine: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF` (8 states; E0 is undefined and is the halt).
Halting proof: `bb8_list/proofs/BB8_champ35_1RB0RA.v` (`Theorem halt : halts tm c0`; `python check.py` PASS, re-run in this session).

## Verdict

**Proved (Coq, no axioms): the score exceeds 2 ↑^35 (2 ↑^35 3), and hence exceeds the BB(7) champion's 2 ↑^11 (2 ↑^11 3).**

> **RECORD CLAIM FLAG.** This is a BB(8) score bound above the current bar 2↑¹¹(2↑¹¹3). It is machine-checked here, but
> the brief asks for independent re-verification of any record claim. See "Reproduction".

The file is `bb8_list/proofs/BB8_champ35_bound.v` (419 lines, compiles in about 20 s). It imports the halting file without
changing it. All theorems print "Closed under the global context".

```coq
Theorem sigma_lower_bound :
  exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ arrow 11 2 (arrow 11 2 3) < N.
Theorem sigma_lower_bound_strong :
  exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ arrow 35 2 (arrow 35 2 3) < N.
Theorem sigma_gt_arrow36 :
  exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ arrow 36 2 3 < N.
Theorem score_exact :
  exists c, c0 -->* c /\ halted tm c /\ ones c (24 * bf + 106).      (* bf = U 34 (U 34 0) *)
Lemma bf_big : arrow 35 2 (arrow 35 2 3) <= bf + 2.
```

## Definitions (self-contained, at the top of the file's stage sections)

- `arrow k a b` is Knuth's up-arrow. It is a `Fixpoint` on k: arrow 0 a b = a * b, and arrow (S k) a b = (arrow k a)^b (1) using
  the standard library's `Nat.iter`. Lemma `arrow_eqns` proves the three requested equations verbatim:
  arrow 1 a b = a ^ b, arrow (S k) a 0 = 1, arrow (S k) a (S b) = arrow k a (arrow (S k) a b).
- `ones c N` is copied from `BB9_champion_bound.v`. It says c = (q, (L *> const 0, s, R *> const 0)) for lists L, R and head
  symbol s, with N = (#1s in L) + [s = 1] + (#1s in R). So N is the exact number of ones on the tape of c.
- `tm` is the imported table. Lemma `tm_table` restates all 16 entries, with E0 = None.

## Score convention

busycoq stops before the halting transition, because E0 is `None`. The halting configuration has the head in state E on a **0**.
N counts the ones on that tape. The standard score treats the undefined transition as 1RZ, so **score = N + 1 = 24 bf + 107**.

- **Small correction to the earlier report.** It gives "sigma = 24 b_f + 106". That is N, the count before the final write. The
  standard score is 24 b_f + 107. This does not affect any bound.

## Stage (a): the halt and its ones count

- The halting file's `R4` and `FIN` are existential. I replayed the identical tactic script with the final configuration made
  explicit (`FINx`, `R4x`):

      c_end J t = 0^inf 1 0 1 0 1 1 0 1 1 0 1 1 (011)^t 0 <E| 1 1 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 0 (101)^J 1 0 1 0^inf

  with the head on the 0 marked `<E|`. Here `Kc (0^(M+1)) 0 b -->* c_end M (12 b + 9)`.
- `ones_c_end` proves ones (c_end J t) (2t + 2J + 20). Lemma `halt_count` combines them: from an all-zero list of M+1 digits
  with counter b, the halt has exactly **24 b + 2M + 38** ones. For 35 digits that is 24 b + 106.
- Independent literal check (`ones_check.py`, plain Python simulation from the Kc tape): 18 cases, L = 1..3 digits and
  b = 0..5, all give 24 b + 2L + 36 ones with the head on 0. The chained case Kc [1] 0 0 (R2, R1, R1, then halt with b = 6) gives
  182 = 24*6 + 2 + 36 ones after 20052 steps.

## Stage (b): exact clearing functions

U j x is the counter b after clearing one unit of a digit at depth j (j zero digits nearer the counters), starting from b = x:

    U 0 x     = dbl (2x+2) 0 = 2^(2x+3) - 2      (R2 sets a = 2x+2, then R1 a times, b -> 2b+2)
    U (j+1) x = (U j)^(2x+2) (0)                 (R3 at depth j+1 writes digit 2x+2 at depth j with b = 0; clear it)

- `CH` and `CDP` prove, for all j, v, Us, B:
  Kc (0^j ++ v :: Us) 0 B -->* Kc (0^(j+1) ++ Us) 0 ((U j)^v B).
  The proof is induction on j, then on v, using only the imported R1ITER, R2, R3. Unlike the BB(9) champion, no side condition
  is needed, because R3 has none.
- `run_to_zero`: init_reach gives Kc (0^34 ++ [2]) 0 0, and CDP 34 with v = 2 gives Kc (0^35) 0 bf with **bf = U 34 (U 34 0)**.
  The start list in the halting file is nearest-first `repeat 0 34 ++ [2]`: the digit 2 is the farthest one, at depth 34.

## Stage (c): comparison with up-arrows

- Key lemma `U_bound`: **U j x + 2 >= 2 ↑^(j+1) (2x+3)** for all j, x.
  - Base: U 0 x + 2 = 2^(2x+3), by `dbl_closed` (dbl a b + 2 = 2^a (b+2)).
  - Step: let h = 2 ↑^(j+1). By induction on n, h^n(2) <= (U j)^n(0) + 2, because
    h(y+2) <= h(2y+3) <= U j y + 2. Then 2 ↑^(j+2) (2x+3) = h^(2x+3)(1) = h^(2x+2)(2), since h(1) = 2.
- Facts used about base-2 arrows: monotone in b; x + 1 <= 2↑^k x for x >= 1; monotone in k (`arrow_level`); 2↑^k 1 = 2; 2↑^k 2 = 4.
- `bf_big`: U 34 0 + 2 >= 2↑^35 3, and bf + 2 >= 2↑^35 (2 U 34 0 + 3) >= 2↑^35 (2↑^35 3).
- N = 24 bf + 106 > bf + 2, which gives `sigma_lower_bound_strong`. Monotonicity in k and b gives the 11-arrow form, and
  2↑^36 3 = 2↑^35 4 <= 2↑^35 (2↑^35 3) gives `sigma_gt_arrow36`.

## Comparison with the paper argument

The earlier report's paper bound is confirmed.
- Its A_n(D) is (U n)^D (0) here. Its psi(beta) = 2^(2 beta - 1) with beta = b + 2 matches U 0. Its recursion
  g_n(b) = A_(n-1)(2b+2) matches U (n+1).
- Its claim A_n(2) + 2 >= 2↑^(n+1)(2↑^(n+1) 3) is exactly `bf_big` for n = 34.
- Its ones formula 24 b + 2L + 36 is now proved for all b and L. Only the score offset differs, as noted above.

## Probe output

`investigations/bb8_champ35_bound/probe.v` imports both files. It prints the definitions, re-checks each theorem against its
literal statement with `Check`, and runs `Print Assumptions`. Full output:

```
tm =
fun pat : Q * Sym =>
match pat with
| (A, 0) => Some (1, R, B)
| (A, 1) => Some (0, R, A)
| (C, 0) => Some (1, R, D)
| (C, 1) => Some (0, L, B)
| (D, 0) => Some (1, R, A)
| (D, 1) => Some (1, L, E)
| (E, 0) => None
| (E, 1) => Some (0, L, C)
| (F, 1) => Some (1, L, D)
| (B, 0) | (G, 0) => Some (1, L, C)
| (G, 1) => Some (0, R, H)
| (F, 0) | (H, 0) => Some (1, R, G)
| _ => Some (1, L, F)
end
     : TM
arrow =
fix arrow (k a b : nat) {struct k} : nat :=
  match k with
  | 0 => a * b
  | S k' => Nat.iter b (arrow k' a) 1
  end
     : nat -> nat -> nat -> nat

Arguments arrow (k a b)%nat_scope
ones =
fun (c : Q * tape) (N : nat) =>
exists (q : Q) (L R : list Sym) (s : Sym),
  c = (q, (L *> const 0, s, R *> const 0)) /\
  N = count1 L + sym_val s + count1 R
     : Q * tape -> nat -> Prop

Arguments ones c N%nat_scope
count1 =
fix count1 (xs : list Sym) : nat :=
  match xs with
  | []%list => 0
  | (x :: t)%list => sym_val x + count1 t
  end
     : list Sym -> nat

Arguments count1 xs%list_scope
sym_val = fun s : Sym => match s with
                         | 0 => 0
                         | 1 => 1
                         end
     : Sym -> nat

Arguments sym_val s%sym_scope
bf = U 34 (U 34 0)
     : nat
U =
fix U (j : nat) : nat -> nat :=
  match j with
  | 0 => fun x : nat => dbl (2 * x + 2) 0
  | S i => fun x : nat => iter (2 * x + 2) (U i) 0
  end
     : nat -> nat -> nat

Arguments U (j _)%nat_scope
arrow_eqns
:
forall a b k : nat,
arrow 1 a b = a ^ b /\
arrow (S k) a 0 = 1 /\ arrow (S k) a (S b) = arrow k a (arrow (S k) a b)
     : forall a b k : nat,
       arrow 1 a b = a ^ b /\
       arrow (S k) a 0 = 1 /\
       arrow (S k) a (S b) = arrow k a (arrow (S k) a b)
sigma_lower_bound
:
exists (c : Q * tape) (N : nat),
  c0 -->* c /\ halted tm c /\ ones c N /\ arrow 11 2 (arrow 11 2 3) < N
     : exists (c : Q * tape) (N : nat),
         c0 -->* c /\
         halted tm c /\ ones c N /\ arrow 11 2 (arrow 11 2 3) < N
sigma_lower_bound_strong
:
exists (c : Q * tape) (N : nat),
  c0 -->* c /\ halted tm c /\ ones c N /\ arrow 35 2 (arrow 35 2 3) < N
     : exists (c : Q * tape) (N : nat),
         c0 -->* c /\
         halted tm c /\ ones c N /\ arrow 35 2 (arrow 35 2 3) < N
sigma_gt_arrow36
:
exists (c : Q * tape) (N : nat),
  c0 -->* c /\ halted tm c /\ ones c N /\ arrow 36 2 3 < N
     : exists (c : Q * tape) (N : nat),
         c0 -->* c /\ halted tm c /\ ones c N /\ arrow 36 2 3 < N
score_exact
:
exists c : Q * tape, c0 -->* c /\ halted tm c /\ ones c (24 * bf + 106)
     : exists c : Q * tape,
         c0 -->* c /\ halted tm c /\ ones c (24 * bf + 106)
bf_big : arrow 35 2 (arrow 35 2 3) <= bf + 2
     : arrow 35 2 (arrow 35 2 3) <= bf + 2
U_bound : forall j x : nat, arrow (S j) 2 (2 * x + 3) <= U j x + 2
     : forall j x : nat, arrow (S j) 2 (2 * x + 3) <= U j x + 2
Closed under the global context
Closed under the global context
Closed under the global context
Closed under the global context
Closed under the global context
```

The final "Closed under the global context" line is for the imported `halt` theorem.

## Reproduction

- In `bb8_list\proofs`: `python build.py BB8_champ35_bound.v`. About 20 s, because the halting file's `.vo` is reused. A fresh
  build of the halting file takes about 8 minutes.
- In `bb8_list\proofs`: `python check.py BB8_champ35_1RB0RA.v` gives PASS for the imported halting proof.
- In `bb8_list\investigations\bb8_champ35_bound`:

      coqc -Q ..\..\..\third_party\busycoq\verify BusyCoq -Q ..\..\proofs BB8 probe.v

- `python ones_check.py` in the same folder runs the literal ones-count check.

## Pitfalls (for later formalizations)

- `Opaque` only delays unfolding. `repeat split; try assumption` on a goal `arrow 11 2 (arrow 11 2 3) < N` made `assumption`
  try to unify it with the hypothesis `arrow 35 2 (arrow 35 2 3) < N`, and Coq started computing the numbers. Close the
  conjuncts with explicit `exact` instead.
- `rewrite !arrow_0` rewrote only one instance in a goal with two. Give the arguments explicitly.
- To use `R4`-style existential lemmas for counting, replay the script with an explicit target. The final `apply` needs `exact`
  with explicit arguments, so that the power `[1;0;1]^^(S (S ...))` is unfolded by conversion.

## Open questions

- Exact step count (not attempted).
- `_CoqProject` has only the `-Q` lines and no file list, so no change was needed there. build.py finds the dependency from the
  `Require` line, as for `BB9_champion_bound.v`.
