# Machine-checked score lower bound for the BB(9) champion

Machine: `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH` (9 states; the halting transition is E0 = 1RZ).
The bbchallenge wiki "Champions" table lists it as the BB(9) champion (Jacobzheng 2024), with the claim sigma > f_omega(f_9(2)).

## Verdict

**Proved (Coq, no axioms): sigma > f_omega(f_9(2)).** The claimed bound holds, with room to spare.
The file is `bb8_list/proofs/BB9_champion_bound.v` (659 lines). It imports `BB9_champion_1RB1RA.v` without changing it, and
`python check.py BB9_champion_1RB1RA.v` still passes. `Print Assumptions` prints "Closed under the global context" for each of the three
theorems below.

- **Record flag.** This is a 9-state result. It has no bearing on the BB(8) bar of 2↑¹¹2↑¹¹3. Before anyone cites it, an independent
  re-check would be good practice (see Reproduction).

```coq
Theorem sigma_lower_bound : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ f_omega (f 9 2) < N + 1.

Theorem sigma_lower_bound_strong : exists c N b, c0 -->* c /\ halted tm c /\ ones c N /\
  (256 * f 9 2 <= b)%nat /\ (2 ^ (b + 2) * f (b + 2) b < N + 1)%nat.        (* b = b1 *)

Theorem score_exact : exists c, c0 -->* c /\ halted tm c /\ ones c (b2 + 3).
```

## Definitions (at the top of the file)

- `iter n g x` = g^n(x), defined by `iter 0 g x = x` and `iter (S n) g x = g (iter n g x)`.
- The fast-growing hierarchy is `f 0 = S` and `f (S k) n = iter n (f k) n`, so f_{k+1}(n) = f_k^n(n). Also `f_omega n = f n n`.
- `ones c N` says that c = (q, (L *> const 0, s, R *> const 0)) for some lists L, R and head symbol s, with
  N = (#1s in L) + [s = 1] + (#1s in R). So N is the exact number of 1s on the tape of c. The machine is deterministic, so
  the halting configuration c is unique, and N is determined.
- `tm` is the imported table. A lemma `tm_table` in the file restates all 18 entries, with E0 = None.

## Score convention

busycoq stops before the halting transition, because E0 = 1RZ is `None`. In the halting configuration, `c_end m`, the machine is
in state E and the head reads a **0**. The standard score counts the 1 that the final 1RZ writes, so **score = N + 1**, and this is
the quantity the theorems bound. The exact values are N = b2 + 3 and **sigma = b2 + 4**.

- **Correction to the earlier report.** `bb9_champion_1RB1RA0LC0LF.md` gives "sigma = b_final + 3". That count leaves out the final
  write. `score_check.py` in this folder simulates the last phase literally for odd b = 1..21. It finds b+3 ones in the
  busycoq halting configuration and b+4 after the 1RZ write. Coq proves the same thing for all b (lemmas `KR4Ox`, `ones_c_end`).

## Exact clearing functions (stage b)

These functions replace the existential B' of `CH`/`CDP`/`BLK`/`PAIR`/`LAST`. Clearing one unit of a digit at depth j (that is,
with j zero digits above it) maps the counter b = x to `U j x`:

    U 0 x = 3x + 7                       (R2, then R1^(b+2))
    U (j+1) x = (U j)^(x - 2j) (X j)     (R3 at depth j+1: j twos above the refilled digit x-2j, then b = 7)
    X 0 = 7,  X (j+1) = U j (U j (X j))  (X j = clearing j twos at depths 0..j-1, starting from 7)

The machine lemma `CDPx_all` is an exact version of `CDP_all`: from `Kd (0^j ++ v :: Us) 0 B` with 2j <= B, the machine reaches
`Kd (0^(j+1) ++ Us) 0 ((U j)^v B)`. The proof uses the same strong induction, through `CHx` and `BLKx`. The invariant 2j <= b
needs only the growth facts `x + 2j + 5 <= U j x` and `4j + 7 <= X j`.

The pair clearings `PAIRSx` and `LASTx` follow. The run (`run1`, `run2_gen`) is:

    b1 = U 7 (U 7 (U 5 (U 3 (U 1 3)))),      U 1 3 = 280,  b1 = 0 (mod 4)
    b2 = U (b1+1) (U (b1+1) (Pv (b1/2) 0 3)),  where Pv m j B clears m pairs (0,1); the digits 1 sit at depths 1, 3, ..., b1 - 1
    halt from Kd (0^k) 0 b2 with b2 odd: c_end (b2/2), N = b2 + 3

The parity and mod-4 facts are now properties of U (lemmas `parity`, `mod4`): one unit flips the parity of b, and for j >= 1 the
residue b mod 4 after a unit depends only on the parity of b.

## The comparison with the hierarchy (stage c)

The key lemma is `bound`. It is a joint induction on j:

    (1)  for all n, z:  2^(j+1) * n <= z  ->  2^(j+1) * f (j+1) n <= U j z
    (2)  2^(j+2) * (j+1) <= X j

Proof idea for step (1). We have U (j+1) y = (U j)^m (X j) with m = y - 2j. Since X j >= 2^(j+1), iterating (1) from n0 = 1
gives (U j)^m (X j) >= 2^(j+1) * f_{j+1}^m (1). The hypothesis y >= 2^(j+2) n gives m >= 2n + 1. Then

    f_{j+1}^{2n+1}(1) = f_{j+1}(f_{j+1}^n(f_{j+1}^n(1))) >= 2 f_{j+1}^n(n+1) >= 2 f_{j+2}(n).

The first inequality uses f_k(w) >= 2w for k >= 1, together with f^n(1) >= n+1. The scaling factor doubles at each level. The
start from 1 matters, because f_k(0) = 0 for k >= 1. Part (2) follows from (1) applied twice.

Supporting facts about f: f_k(n) >= n; f_k is monotone; f_k(n) > n for n >= 1; f_k(n) <= f_{k+1}(n) for n >= 1, hence
f_k(n) <= f_{k'}(n) for k <= k'; f_1(n) = 2n; and f_k(n) >= 2n for k >= 1.

The chain:
- U 3 280 >= 280, so U 5 (U 3 280) >= 64 f_6(4) >= 512. Then U 7 (.) >= 256 f_8(2), and **b1 >= 256 f_8(f_8(2)) = 256 f_9(2)**
  (lemma `b1_big`).
- For the second clearing, U (b1+1) z >= X b1 >= 2^(b1+2) (b1+1). So b2 >= 2^(b1+2) f_{b1+2}(b1) (lemma `second_big`).
- With N0 = f_9(2) <= b1: f_omega(N0) = f_{N0}(N0) <= f_{b1+2}(N0) <= f_{b1+2}(b1) <= b2 < b2 + 4 = sigma.

## Comparison with the paper argument

The paper argument (earlier report) is sound in outline. The formal proof confirms both of its claims and makes them precise:
- "G_j at level j+2 of the Ackermann hierarchy" becomes level j+1 of the fast-growing hierarchy, with a scaling factor:
  U_j(z) >= 2^(j+1) f_{j+1}(z / 2^(j+1)). The paper's claim was loose, because Ackermann-style iterations start from a constant.
  For large arguments U_2(x) < f_3(x) (roughly a tower of height x-2 on 91, against a tower of height about x on x), so a bound
  of the form "U_j(x) >= f_{j+1}(x - c)" with a constant c is false. The argument has to be scaled, as in `bound`.
- "b1 comfortably >= f_9(2)" holds as b1 >= 256 f_9(2).
- "b2 >= f_{b1+1}(b1)" holds in the stronger form b2 >= 2^(b1+2) f_{b1+2}(b1).
- No off-by-one in the levels affects the claimed bound. The only correction is the score offset noted above (sigma = b2 + 4, not
  b2 + 3), and it does not affect the bound.

## Compile time and reproduction

- In `bb8_list\proofs`: `python build.py BB9_champion_bound.v` takes about 17 s (Coq 8.20.1); the `Qed`s are fast.
- In `bb8_list\investigations\bb9_champion_bound`: `coqc -Q ..\..\..\third_party\busycoq\verify BusyCoq -Q ..\..\proofs BB8 probe.v`
  prints the definitions of `f`, `f_omega` and `ones`, type-checks `sigma_lower_bound` against the exact statement, and prints
  "Closed under the global context" for all three theorems.
- `python check.py BB9_champion_1RB1RA.v` still gives PASS. The new file has no `halt`/`nonhalt` theorem, so check.py does not apply to it.
- `python score_check.py` runs the literal final-phase check (ones = b+3 before the final write, b+4 after it).

## Pitfalls (for later formalizations)

- `lia` hangs on closed terms such as `b1 / 2`, where b1 is a large closed expression. This happens even when b1 is `Opaque`.
  The fix is to state each arithmetic step for a variable b (`second_odd`, `run2_gen`, `second_big`, `omega_le`) and to instantiate
  with b1 afterwards.
- Never use `simpl` near `f k n` with numerals, or near `x mod k`: `simpl in *` tried to evaluate `f 6 4` (stack overflow), and
  `simpl` unfolds `mod`. Use `cbn [iter]`, `change`, and the `f_S` / `U_S` / `X_S` rewriting lemmas. `U` and `X` are made
  `Opaque` after their defining equations.
- `mods` (from the halting file) abstracts only `x mod k`. When a goal mentions `x / 2`, first add `Nat.div_mod_eq x 2` so that
  `x / 2` gets abstracted too.

## Open questions

- Exact step count (not attempted).
- Sharper bounds, for example a closed form of b1 in terms of f with explicit offsets. They are not needed for the claim.
