# The BB(9) champion `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH` halts

## Verdict

**HALTS. Confidence: proved (Coq PASS).** `proofs/BB9_champion_1RB1RA.v` passes `python check.py BB9_champion_1RB1RA.v`:
`PASS ... HALTS (machine-checked, no axioms)` (Theorem `halt : halts tm c0`, 9-state setup `Individual92`, ~35 s).

- **Record-claim flag.** This machine is the self-reported BB(9) record holder (Jacobzheng 2024, wiki "Champions", claimed
  sigma > f_omega(f_9(2))). The halting is now independently machine-checked. The sigma lower bound below is a paper
  argument only, NOT machine-checked, and should be re-verified before anyone relies on it. It is a 9-state machine, so it
  says nothing about the BB(8) bar.
- Exact score at the halt: **sigma = b_final + 3**, where b_final is the odd value of the counter b at the third restart
  attempt (exact for odd b = 1..21 by literal simulation; `sigma.py`). Steps in that last phase for b = 2m+1: 2m^2 + 15m + 21 (literal
  check b <= 21). The total step count is dominated by the clearings and is not computed.
- Structure of the run (proved): the machine does **exactly two restarts (rebuilds) and halts at the third attempt**.
  - restart 1 at b = 6 (blank list), clearing of a list with 3 pairs gives b_1 = 0 (mod 4);
  - restart 2 at b_1 (p = b_1/2 pairs, p even), the clearing ends with b_2 odd;
  - the third restart attempt with b_2 odd is the halt (E0 = 1RZ).

## Orientation and configuration family

Tools (kfam/kfit) were run on the mirror image `1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH` with shape
D,1. The Coq proof is for the champion as given (structure to the RIGHT of the head). With `Kd` below, mirror configs
`X {{D}}> const 0` become `const 0 <{{D}} X`.

    Kd ds a b = const 0 <{{D}} (1 >> [1]^^b *> 0 >> [1]^^a *> lft ds),   lft (d::t) = 0 >> [1]^^d *> lft t
    = 0^inf <D 1^(b+1) 0 1^a 0 1^d_1 0 1^d_2 0 ... 1^d_n 0^inf          (ds top digit first)

Zero digits are allowed (and essential here); the list is blank iff all digits are 0.

## Rules (all proved for ALL parameters in Coq; also literal-checked)

| rule | statement | notes |
| --- | --- | --- |
| R1 | Kd ds (S a) b -->+ Kd ds a (b+3) | one sweep |
| R2 | Kd (S y :: t) 0 b -->+ Kd (y :: t) (b+2) 1 | with R1^(b+2): b -> 3b+7 per unit of the top digit |
| R3 | Kd (0^(m+1) ++ S y :: t) 0 (2(m+1)+s) -->+ Kd (2^m ++ (s+2) :: y :: t) 2 1 | k = m+1 zero digits above y+1, needs 2k <= b; refill b+2-2k, k-1 twos |
| R4e | Kd (0^k) 0 (2m) -->+ Kd (Q m) 1 0, Q m = (0,1)^m (0,2) (top first) | blank list, b even: restart |
| R4o | Kd (0^k) 0 (2m+1) -->* halted configuration | blank list, b odd: halts (E0), 7 steps after the fill loop |

- **Halting cases (literal probes, not needed for the proof).** R3 halts exactly when 2k >= b+1 for b odd. For b
  even, 2k >= b+2 gives irregular rebuild-like outputs such as K(1,3,0,1,0;1;0). The proof never enters this region
  (lemma `CDP_all` keeps 2k <= b).
- Literal check of R1-R4 (`absm.py`): the abstract successor function was compared with the exact literal simulator on 6,912
  configurations (ds of length <= 4 with digits 0-3, a = 0..2, b = 1..9): 0 mismatches; the 36 unpredicted cases are the
  region 2k >= b+1 above. R3 raw tables: `r3scan.py`.
- Machine-level phases (planner9.py = planner8 with 9 states; `gen9.py` generates `phases.v`):
  R1, R2 in one script each; R3 = ENTRY + LOOP^(k+1) + FINAL (one crossing lemma `cr_FL_011_101` for the k-1 twos);
  R4 = ENTRY + LOOP^(m+1) + R4E (I-crossing `cr_IL_110_010`) or the 7-step halt.

## Parity bookkeeping (proved, lemma `CDP_all`)

Let "depth j" mean j zero digits above the digit v being cleared, with the invariant 2j <= b.
Clearing v at depth j (all of its units, with all refills) maps b to b' with
- b' >= b + v + 2j + 5 if v >= 1 (growth, keeps 2j <= b for the next digit), b' = b if v = 0;
- b' = b + v (mod 2);
- for j >= 1, v >= 1: b' = 3 (mod 4) if b+v is odd, b' = 0 (mod 4) if b+v is even.
At depth 0 each unit of v maps b to 3b+7 (lemma `CH`). Proof: strong induction on j; inside, induction on v; R3 produces the
block 2^(j-1) (s+2) which is cleared by the same lemma at smaller depths (`BLK`). The invariant `2*j <= b` is exactly what R3
needs, so the halting boundary 2k = b+1 is never met.

## The run from the blank tape (rule level)

1. blank tape --11 steps--> Kd [] 2 0, R1,R1 -> Kd [] 0 6, R4e (m = 3) -> Kd (Q 3) 1 0, R1 -> Kd (Q 3) 0 3.
2. Clearing Q 3 = (0,1)(0,1)(0,1)(0,2) from b = 3 (lemma `PAIR` three times, then `LAST`): the mod-4 values are
   b+1 = 4 even -> 0; 0+1 odd -> 3; 3+1 even -> 0; digit 2 at depth 7: 0+2 even -> 0. So b_1 = 0 (mod 4).
   Exact formula: b_1 = G_7(G_7(G_5(G_3(G_1(3))))) with G_j below (b after the first digit is 280 = f^3(7), checked
   against the abstract run: the first R3 at depth 3 refills 276).
3. R4e with b_1 even: Kd (Q p) 1 0 with p = b_1/2 even; R1 -> b = 3.
4. Clearing Q p from b = 3: parity 3 + p + 2 = odd. b_2 odd, blank list: R4o halts.

Cross-check (not used by the proof): `modeval.py` evaluates the exact clearing function modulo 2^k with stabilised towers;
it gives b_1 = 752 (mod 1024) (stable over its precision parameter), so b_1 = 0 mod 16 and 16 mod 32, consistent with the
Coq mod-4 statement. The exact clearing functions (derived from R1-R3): f(x) = 3x+7, G_0 = f, and for x >= 2j
G_j(x) = G_{j-1}^(x+2-2j)(X_{j-1}), X_0 = 7, X_{i+1} = G_i(G_i(X_i)).

## Score estimate (paper argument, NOT machine-checked)

- sigma = b_2 + 3, b_2 = G_{2p+1}(G_{2p+1}(G_{2p-1}( ... G_3(G_1(3))))), p = b_1/2, b_1 as above.
- Lemma (paper; induction using A(k,n) >= n + 2k): G_j(x) >= A(j+2, x-2j) for x >= 2j, A = Ackermann (A(k+1,n+1) = A(k,A(k+1,n))).
  So G_j is at level j+2 of the Ackermann/fast-growing hierarchy.
- Hence b_1 >= A(9, A(9, y - 14) - 14) with y >= A(7, ...), i.e. b_1 is f_8-level of a tower of f_6 values, comfortably >= f_9(2) = f_8^3(2).
  And b_2 >= A(b_1 + 3, w) with w >= b_1, so sigma >= f_{b_1+1}(b_1) > f_{b_1}(b_1) = f_omega(b_1) >= f_omega(f_9(2)).
- So the claimed bound sigma > f_omega(f_9(2)) is consistent with (and supported by) this argument. Open: a formal
  Coq statement of this lower bound (strengthen `CDP` with an Ackermann-type lower bound clause) was not attempted.

## Relation to the BB(8) machine 1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---

Same design (digit-list counter, R2/R3 with refill and a halting boundary on trailing zeros, restart on the blank list), but here
R1 is additive (b+3) and R2 sets a = b+2 (so b -> 3b+7 per unit), the refill of R3 is b+2-2k (not about 4b), the digits written by R3 are 2s,
and the restart list contains zero digits ((0,1)^m (0,2)). Halting is parity controlled (R4 halts iff b odd; R3 halts iff 2k >= b+1 for b odd)
and the restart size m = b/2 couples one level to the next: the machine halts because b_1 = 0 mod 4 makes the second restart
list have an even number of pairs.

## Reproduction

In `bb8_list\investigations\bb9_champion_1RB1RA0LC0LF` (python = `..\..\..\third_party\venv311\Scripts\python.exe`):
- `python trace.py 3000000` literal K-configuration trace from the blank tape (mirror, shape D,1).
- `python absm.py` rule grid check (6912 configs, 0 mismatches); `python r3scan.py`, `python r3scan2.py 7,5 2 4 7 8` R3 tables.
- `python gen9.py` regenerates the planner scripts `phases.v`; the Coq file is `title9.v head9.v phases.v glue1.v ... glue6.v` concatenated
  (`cat title9.v head9.v phases.v glue1.v glue2.v glue3.v glue4.v glue5.v glue6.v > ..\..\proofs\BB9_champion_1RB1RA.v`).
- `python modeval.py 32` cross-check of b_1 modulo 2^k; `python parity.py` parity-level model; `python sigma.py` sigma = b+3 for odd b.
In `bb8_list\proofs`: `python check.py BB9_champion_1RB1RA.v`.

## Pitfalls found (for later 9-state / digit-list proofs)

- `lia` in this Coq build does NOT understand `mod` or `/`: the tactic `mods` (abstract each `x mod k` with `Nat.div_mod_eq` and the bound) followed by `lia` works.
- With the busycoq import, a bare `0` or `1` in a comparison is parsed as `sym`; `Local Open Scope nat_scope` in the abstract part fixes it.
- `rewrite (align_lpow 1 [] _ n)` with an explicit counter n can fail; use `_` for the counter (coqgen_util.py patched in this folder).
- Strong induction needs `From Coq Require Import Wf_nat` for `lt_wf_ind`.

## Open questions

- Formalize the sigma lower bound (Ackermann-type clause in `CDP`) and the exact step count; not needed for the halting verdict.
