# n1: independent check (inv-bb10-fw1-verify, 2026-10-08)

Machine n1 (10 states; J0 undefined = halt):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC

- **Base.** Rows A–H are the GH 35-digit machine `..._---0LC_0RG1LD_1RH1LG_1LC0RG`, with E0 = 1LI, I = 0LJ0LI,
  J = ---0LC.
- **Tools.** My own, in `bb8_list/investigations/bb10_n1_verify/`: sim.exe with a relaxed B-form stop `BgH`;
  `n1sim.py`, a hybrid follower with a far region; `rules_n1.py`; `endg*.py`.
- **Independence.** I read bb8-ab's selector.md §6b for orientation only. I did not read its Fable verifier report.

## Verdict

**HALTS, in state J reading 0. σ is f_(ω+1)-class. Strong evidence, no Coq.**
- **Steps.** There are N = (12B+5)/7 growth steps, where 2B+4 = 2↑^37 3. Each step is at least an f_ω-step on the
  current depth: n ↦ n' ≥ 2↑^(n+1) 3.
- **Bound.** σ > G^N(33), with G(x) = 2↑^(x+1) 3 and N ≈ 1.71·B.
- **The M3 trap does not occur.**
  - The two growth events unpack a parked token that is much larger than the transit, and the unpack is free: the
    transit survives whatever the sizes.
  - Every rule was checked literally in both size orders.
- **Endgame.** The counter runs out in the class B ≡ 6 (mod 7), which is the real class. The final stage halts for
  every tested size, with an exact ones formula.
- **Ranking.** If the chain holds, n1 is far above M3 (f_ω at index ≈ 4·2↑^37 3), M3J, the 0LA machines and the
  BB(10) champion (f_ω^2(25)).

## 1. Notation and base

**B-form.** [L | A] = tape D(L1)..D(Ln) D0 D(A), with the head on the blank to its right in state **H** (GH family).
The record family uses state G; the tape is the same.
- The GH base reaches [D7 D1^35 | 4] at step 6447 and [D4^36 | 16] at step 48159. These are the record's B(1; [0]^35, 2)
  and B(5; [1]^36).
- R1, R2 and H hold for n1: 40 random literal checks each, 0 mismatches.
- A **far region** is any bit string ending in a 00 run, left of the active list. The relaxed stop `BgH` accepts it.
  R1/R2 act only right of it.

## 2. The chain (`n1sim.py`; whole runs for b = 6 and b = 20 halt)

**Stage 0** (literal for B = 6, 13, 20, 27, 34, 41, 366). Starting from H's output:

    [2, 1^(12B+12), 0, 1^35 | 6]  ->  [2, 5, 1^(12B+7), 0,0,0, 9, 1^33 | 4]

Then:
- CLR(9) at depth 33.
- P4 with Q = 0: m → 12B+5, zero block 34.
- CLR.
- The period begins.

**Period** (k = D2 count, m = counter, n or w = zero block). All rules are literal-checked on 72 random instances each
(`rules_n1.py`), in BOTH size orders, with 0 mismatches.

| step | rule |
|---|---|
| P1 | [2^k, 5, 1^m, 0,0,2, 1^n \| A] → [2^(k+2), 5, 1^(m−6), 0,0,0, 1, A+3, 1^n \| 6] |
| R2, CLR(9) | deposit 9 next to D(A+3), consumed at depth n−1 → [.., 0^3, 1, **P = A**, 0, 1^(n−1) \| R], with R a 3-unit clearing from a reset |
| P2 (growth) | [2^k, 5, 1^m, 0^3, 1, P, 0, 1^w \| R] → **Far(k,m)** + [2, R+1, 1^(w + (2P+4)/3 − 1) \| 4], for any R ≷ P |
| CLR(R+1) | about R/3 units at the new depth → D2; the accumulator becomes A' (big) |
| P3 | Far(k,m) + [2, 2, 1^w \| A'] → [2^(k+2), 5, 1^(m−6), 0,0, A'+5, 1^w \| 6] |
| R2, CLR(9) | → [.., 0,0, **Q = A'+2**, 0, 1^(w−1) \| R'], with R' small |
| P4 (growth) | [2^k, 5, 1^m, 0,0, Q, 0, 1^w \| R'] → [2^k, 5, 1^(m−2), 0,0, R'+1, 1^(w + 2Q/3 + 1) \| 4], for any R' ≷ Q |
| CLR(R'+1) | → D2; the accumulator becomes the next period's A (big); back to P1 |

**Per period.** k increases by 4 and m decreases by 14. The zero block grows twice: by (2P+4)/3 at P2 and by 2Q/3 + 1 at
P4.

**Residues used.**
- P ≡ 1 (mod 3) and Q ≡ 0 (mod 3), so the zero counts are integers.
- R+1 ≡ 2 (mod 3), so the token is cleared to D2.
- At the end R+2 ≡ 0 (mod 3), so the token is cleared to D0.
- All of these hold because the deep accumulators are ≡ 1 (mod 3). The tests used deep values ≡ 40 (mod 120), the real
  class.

## 3. The four questions

**(1) The far region.** Far(k, m) is exactly the token list [2^(k+2), 5, 1^(m−6), 0,0,0] followed by "00" (checked
for many (k, m)).
- It does not depend on P, R or w.
- P2 writes it and P3 merges it back. It is the counter part of the list, with the same form every period.
- At real sizes it has k up to about 3.4B and m up to 12B.
- At the endgame the far region is D2^(k−6) plus a fixed 39-bit tail `D1 D6 z2 D0 z5 D1 D0^3 (z2 D0)^4 z2`. This is
  checked for k = 10, 23 and 57; bb8-ab's "~130 bits" is this at k = 23. The halt uses only the fixed tail.

**(2) Growth and payment in the real order.**
- At P2 the parked token is P = A, the output of clearing D(R''+1) (about R''/3 units) at the current depth.
- The transit R is a 3-unit CLR(9) from a reset at the same depth.
- So **P ≫ R in the real run**, and likewise Q ≫ R' at P4.
- Both unpacks complete with the transit intact. P2 was tested literally with P = 1480 against R = 40 and P = 4840
  against R = 400, plus 72 random instances in both orders.
- Nothing is paid, so every growth is affordable.

**(3) Zeros crossed per jump** (literal; b = 6, fakes):

    33 34 33 380 379 888 887 1554 1553 2382 2381 3368 3367 4516 4515 5822 5821 7290 7289 8916 8915 10704 10703 12650

- Each step between consecutive pairs is a growth of 2P/3 or 2Q/3.
- With real values, P and Q are clearings at the current depth n with at least one unit, so P + 3 ≥ 2↑^n 4. Hence
  n' ≥ 2↑^(n+1) 3.

**(4) Endgame and residues.**
- m: 12B+7 → 12B+5 (first P4) → −14 per period (P1 −6, P3 −6, P4 −2).
- The last P1 meets m = 7 → 1 exactly when 12B+5 ≡ 7 (mod 14), i.e. B ≡ 6 (mod 7). The real B ≡ 6 (mod 7).
- Then:
  - P2 with m = 1: [2^k, 5, 1, 0^3, 1, P, 0, 1^w | R] → far'' + [R+2, 1^w2 | 4], with w2 = w + (2P+4)/3 − 1;
  - CLR(R+2 → D0);
  - far'' + [0, 1^w2 | F] → **HALT in J0**, with ones = 2·w2 + F + 3k + 4.
- `endg2.py`: 60 random cases, k 6..200, w 1..300, P, R, F random ≡ 40 (mod 120). All give the exact P2 rule, a HALT in
  J0 and the exact ones formula.
- `endg.py` grids (k = 10..57, w2 covering all residues mod 5, three values of F) agree.
- The whole hybrid chains for b = 6 and b = 20 (the real class mod 14) halt in J0 after 11 and 35 growth events.
- No dependence on residues of P, R, F or w was found beyond mod 3 (mod 8/16/5 classes and w mod 5 were varied).
- B enters only through B mod 7. B's parity is irrelevant to this chain; b ≡ 13 (mod 14) was not run, and the real B is
  even anyway.


## 3b. The two extra items (lead / bb8-ab, 2026-10-08)

### b = 2526 itself (B ≡ 6 mod 2520; `b2526.py`, log `tmp/b2526.txt`)

1. **Stage-0 special, literal at B = 2526.**

       [2, 1^30324, 0, 1^35 | 6]  ->  [2, 5, 1^30319, 0,0,0, 9, 1^33 | 4]

   Exact, 2,549,700 steps; m0 = 12·2526 + 7.
2. **The first 3½ periods from the record end** (hybrid: literal specials, fake clearing outputs ≡ 40 mod 120).
   - The rules are followed exactly: k += 4 and m −= 14 per period, with growth 2P/3 at P2 and 2Q/3 at P4.
   - The far region is the counter, ~90,956 bits, re-merged by P3.
3. **The last three periods and the endgame**, started from the rule-composed configuration
   [2^8649, 5, 1^49, 0,0,2, 1^300 | 1000] (k = 1+4j and m = 12B+5−14j for j = 2162).
   - The last P1 meets m = 7 → 1 with k = 8663 = 3 + 4(6B−1)/7, as predicted.
   - P2 with m = 1 gives far (43,329 bits) + [D162 D1^2248 | 4].
   - CLR(162 → D0), then **HALT in J0**. The head reads the fixed tail; the D2 run left of it is D2^8657 = k − 6.

### Exactness of the 2R+3 jump (my D(R+1) after P2, and D(R'+1) after P4)

**R2 rule.**
- The token T ≡ 2 (mod 3) is borrowed (T−2)/3 times by R2, each with t → t−3.
- The R2 rule was checked for every residue of t (40 random checks for n1; 230 for the record family).
- After that the token is D2 and the zero block is unchanged.
- The scan then meets D2 D2, or D2 with the far gap behind it. That is P3 (or the end-game), checked literally.

**Fully literal end-to-end (no macro anywhere).**
- **Jump + P3:** Far(k, m) + [2, 5, 1 | 4] (one unit at depth 1) → P3 output [2^(k+2), 5, 1^(m−6), 0,0, A'+5, 1 | 6].
  This is exactly the rule, with the far region re-merged. 7 cases, k = 2..40, m = 7..60.
- **CLR(9) + P2:** [2^k, 5, 1^m, 0^3, 1, P, 9 | 4] → Far(k, m) + [2, 89, 1^((2P+4)/3 − 1) | 4]. This is exactly the
  rule. 4 cases, P = 40..1480.

**Limit.** Deeper jumps are astronomically long, so at depth ≥ 2 the jump is the composition of the checked R1/R2 moves
(the record's clearing). This is the same evidence level as for every other clearing in this family.

### Cross-check of bb8-ab's far-region form (selector.md §6b)

**Tail.** My endgame far region D2^(k−6) + `D1 D6 z2 D0 z5 D1 D0^3 (z2 D0)^4 z2` is, bit for bit,
(10101)^(k−6) followed by `10110101010101010010000010111100100100100100`. That is exactly bb8-ab's 44-bit tail; my 39
bits plus the final 00 run make 44.

**Ones formula.** bb8-ab's ones = 2R + 2n + 3k + 26 equals my 2·w2 + F + 3k' + 4 under the conversion:
- their k = my k' − 6;
- their n = my w2 − 1, since their a-slot D1 is my first zero;
- their R satisfies my F = 2R + 2, the same conversion as for M3.

## 4. Size

**Counts.**
- k_end = 3 + 4(6B−1)/7, the D2 count at the final P2.
- N = (6B+6)/7 + (6B−1)/7 = (12B+5)/7 growth events. This is 11 at b = 6, matching the run.
- The initial depth is 33.

**Bound.** With G(x) = 2↑^(x+1) 3, about an f_ω step:
- n_final ≥ G^N(33);
- σ_ones = 2·w2 + F_final + 3·k_end + 4 > n_final ≥ G^N(33), with N ≈ 1.71B ≈ 0.86·(2↑^37 3).

FGH reading: f_(ω+1)(≈ 1.7B). bb8-ab's "f_(ω+1)(0.86B)" counts periods instead of growth events; that is the same
class.

**Comparisons.**
- All earlier candidates are a single f_ω-scale application: M3 at index ≈ 4·2↑^37 3; M3J and 0LA at ≈ 2.4·2↑^37 3;
  the BB(10) champion at f_ω^2(25).
- n1 iterates f_ω about 1.7B times, so it is far above all of them.

## 5. Caveats

- **Clearings.** They rely on the record's R1/R2, checked here only literally for n1, though the GH base is one of the
  four 35-digit machines.
- **Specials.** Every special is a uniform-in-size rule, checked up to a few thousand in every parameter. That they
  stay uniform at astronomical sizes is not proved.
- **Fakes.** The hybrid chains use fake clearing outputs in the real class mod 120. The rules themselves were checked
  in both size orders.
- **Coq.** None.

## 6. Reproduction (`bb10_n1_verify/`)

**Build.** `g++ -O2 -static -o sim.exe sim.cpp`.

**Commands.**
- `python startup.py` (base start-up);
- `python rules.py 40 3 R1,R2,H`;
- `python rules_n1.py 60 7`;
- `python n1sim.py 6 F1,F2,...` (whole chain);
- `python endg.py "[23,31,57]" "list(range(1,26,3))" "[520,1000]"`;
- `python endg2.py 3 60`.

**Logs** are in `tmp/`:
- `n1_b6_inc.txt`, `n1_b20.txt`;
- `rules_n1.txt`, `endg2.txt`.
