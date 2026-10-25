# Independent verification of c1 (Opus investigator, 2026-10-08)

Machine c1 (10 states, I0 undefined = the halt):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---1LJ_0RJ0RF

It is the G/H sibling of the BB(8) record with E0 = 1LI, I = ---1LJ, J = 0RJ0RF. Premise taken from the lead: the base
machine reaches K(0^35; 0; B) at its first E0 read, with 2B+4 = 2↑^37 3.

All tools and logs are in `halt_redirect/c1v/`. I wrote my own simulator (`c1sim.cpp`), driver (`c1lib.py`), follower
(`myfol.py`), rule checker (`rules.py`), stage grids (`stages.py`, `t0halt.py`) and residue code (`tower.py`). I did not
use stage35g, mf35g, follow2 or ord_run. Every check matches an exact target K-moment, so a parser slip shows up as a
TIMEOUT, never as a silent pass. CPU use was one process at a time, at Idle priority.

## Verdict

**c1 halts in the real class, at the end of its first round.** This holds because B ≡ 0 (mod 3).

- **Period count.** There are (4B−3)/3 full periods, i.e. growth stages, each using 3 D6. The last J1/J2 pair then hits the exhaustion stage `[6 0 1^z | 1 | R]`, where the machine halts in I reading 0.
- **Final depth.** The final zero count is z_end = (76B+135)/3, which matches the selector's n_end.
- **Ones.** σ = 2·R_end + 2·z_end + 21 exactly. This is the literal formula over 879 cases; z counts zero digits excluding the a-token.
- **Score class.** σ is ω-level 1 with Knuth-arrow index N = (76B+141)/3 ≈ 25.3B:

      2↑^N 5  <  σ  <  2↑^N (16B/3 + 23),    N = (76B+141)/3 = (38·(2↑^37 3) − 11)/3.

  This is about 3.2 times M3's arrow count (8B+56) and about 5.3 times the three-cycle sibling's (≈ 4.8B+42). c1 ranks
  above both. Each comparison assumes the other machine's own stage chain.
- **Confidence.** About 90% for halting and the counts, and about 90% for the class.
  - The halting argument has only one mod-3 condition. B ≡ 0 (mod 3) follows from B = 2^(odd) − 2 alone.
  - All stage maps are uniform in R ≡ 1 (mod 3). No literal stage ever holds two huge quantities.
  - Everything rests on grid-checked rules and stages, not on Coq.

**Correction to the claim.** "Halts for b0 = 6..26 under std/big/shrink" is correct only for b ≡ 0 (mod 3). For
b0 = 11, 16 and 26 the first round does not halt.
- b ≡ 1 (mod 3) ends in a left event at `[4 (2R−7) 1^z]`.
- b ≡ 2 (mod 3) ends in an m = 0 growth `[0 1^z | R] → [7 1^(4R+z+4)]`, an unpack of R into about 4R zeros.

Both start a new round whose size depends on R. With the follower's fixed representative R = 19, that round is the same
as b0 = 6 and halts; `fol_b16_19_fixed.log` reproduces this. That halt is a representative artefact. In reality these
classes would be much larger or would not halt. This does not affect c1, because the real B is ≡ 0 (mod 3).

## 1. Notation

- **D-tokens.** A K-moment is `0^∞ D(t1) … D(tn) D(a) D(r) 1010 G> 0^∞`, with D(m) = (10)^m 1. It is written
  `[t1 … tn | a | r]`, farthest token first.
- **Digits.** D1 is a zero digit and D4 is a one.
- **Blocks.** `1^z` means z zero digits, never counting the a-token.
- **u-units.** Let u = 2(r+5)/3. Accumulators always have r ≡ 1 (mod 3), so u is an integer.

## 2. Champion rules (literal, `rules.py`)

| rule | statement |
|---|---|
| R1 | [L \| a \| r] → [L \| a−3 \| 2r+5], a ≥ 4 |
| R2 | [L, d \| 1 \| r] → [L, d−3 \| 2r+5 \| 1], d ≥ 3 |
| R3 | [L, d, 1^k \| 1 \| r] → [L, d−3, 2r+5, 1^(k−1) \| 1 \| 1], d ≥ 3, k ≥ 1 |

**Checks.**
- There were 615 random checks in 11 left contexts that occur in the run, with 0 failures:
  - a in 4..60;
  - d in 3..200;
  - k up to 400;
  - r up to 7579, including the real-class values 2539 and 7579.
- **Head confinement.** The head never moves left of the leftmost pattern token. Its final 1 is the only cell of L it reads, so each rule holds for every nonempty L.
- **Slots read.** Only base slots are read. E0, I and J are never touched, so these are the base machine's rules.
- **D3 is not a blocker.** R2 and R3 also hold for d = 3. The "PARK" stage and the transient's D3 stages are exactly R3 with d = 3.

**Closed form** (proved by induction; `closed.py` checks k = 0 and 1). In u-units, one borrow at depth k (k zero tokens
nearer than the borrowed token), followed by full clearing of the deposit, maps u ↦ 2↑^(k+1) u.
- Depth 0 gives C_0(u) = 2^u.
- Depth k gives C_k(u) = C_(k−1)^(u−2)(4), since the deposit 2r+5 is borrowed u−2 times starting from r = 1, i.e. u = 4.
- Then C_k(u) = (2↑^k)^(u−2)(2↑^(k+1) 2) = 2↑^(k+1) u.

**Jumps.** A jump applies only R1-R3, and r stays ≡ 1 (mod 3).
- Every deposit 2r+5 is ≡ 1 (mod 3). So the jump clears every token ≡ 1 (mod 3) nearer than the first token that is not ≡ 1 (mod 3).
- It ends with that token at its floor: 0, 2 or 3 (D3 is kept as the stopping point, by convention).
- If there is no such token, the jump ends at the left end.
- The output structure therefore follows from residues mod 3 alone. The new accumulator comes from a deep clearing, so it carries the universal residue.

**Residues** (`tower.py`, own Carmichael tower code).
- r* − 1 ≡ 49612750485498 (mod 54305848396800), and B ≡ 16537583495166 (mod 18101949465600). Both match the lead's values.
- Small real representatives: r* ≡ 2539 (mod 5040), 7579 (mod 10080) and 17659 (mod 80640).
- B ≡ 366 (mod 3600) and B ≡ 2526 (mod 5040).
- **B ≡ 0 (mod 3) directly.** 2B+4 = 2↑^37 3 = 2^T with T a tower of 2s, so B = 2^(T−1) − 2. T−1 is odd, so 2^(T−1) ≡ 2 (mod 3).

## 3. The chain (literal stages: `stages.py`, `t0halt.py`)

Every literal stage input has the form [small structure, 1^z | 1 | R] with exactly **one** huge quantity, the current
accumulator R. There are no parked huge tokens, so the M3 trap (a short-clearing accumulator paying for a long-clearing
token) cannot arise. The size-order checks below confirm that the stages do not compare R with z or m.

Let u0 = 4b+3 and w = 8b+47. Literal stages are marked "lit"; jumps are marked "J" and listed with the depth of their deepest borrow.

| stage | map |
|---|---|
| T0 (lit) | K(0^35;0;b) → [6^u0 2 0 9 1^w \| 1 \| 1] |
| J | 9→3 (two borrows at depth w) → [6^u0 2 0 3 1^w \| R] |
| T1 = R3(d=3), J | → [6^u0 2 0 0 1^w \| R] |
| T2 (lit) | [6^m 2 0 0 1^z \| R] → [6^(m−1) 3 2 1 0 (2R+4) 1^(z−1)]; J → [.. 0 3 1^(z−1)] |
| T3 = R3(d=3), J | → [6^(u0−1) 3 2 1 0 0 1^(w−1) \| R] |
| T4 (lit) | [6^m 3 2 1 0 0 1^z \| R] → [6^m 0 3 1 (2R+2) 1^(z+1)]; J → [6^m 0 3 1^(z+3)] |
| T5 = R3(d=3), J | → [6^(u0−1) 0 0 1^(w+2) \| R] |
| T6 (lit) | [6^m 0 0 1^z \| R] → [6^(m−1) 2 2 0 (2R+4) 1^(z−1)]; J → [.. 0 3 ..] |
| T7 = R3(d=3), J | → [6^(u0−2) 2 2 0 0 1^(w+1) \| R] |
| T8 (lit) | [6^m 2 2 0 0 1^z \| R] → [6^(m−1) 3 3 1 1 (2R+3) 1^z]; J (2R+3 → 2) → [.. 1 1 2 1^z] |
| T9 (lit) | [6^m 3 3 1 1 2 1^z \| R] → [6^m 3 0 (2R+5) 7 1^(z+1)]; J → [6^m 3 0 1^(z+3)] |
| T10 (lit) | [6^m 3 0 1^z \| R] → [6^(m−1) 4 (2R−1) 1^(z+5)] |

**Period start.** After T10 the configuration is [6^p0 4 X0 1^n0 | 1 | 1], with p0 = 4b−1, n0 = 8b+56 and X0 = 2R−1.

**Period** (with p = p_j, n = n_j):

    J1   [6^p 4 X 1^n | 1 | 1]   X -> 1 (depth n), 4 -> 1 (depth n+1), 6 -> 3 (depth n+2)  ->  [6^(p-1) 3 1^(n+2) | 1 | R]
    PARK = R3(d=3)               ->  [6^(p-1) 0 (2R+5) 1^(n+1) | 1 | 1]
    J2   (2R+5 cleared at depth n+1, blocked by D0)                                  ->  [6^(p-1) 0 1^(n+2) | 1 | R']
    GROW [6^m 0 1^z | 1 | R'] -> [6^(m-2) 4 (2R'-7) 1^(z+11) | 1 | 1]      (m >= 2)
    HALT [6 0 1^z | 1 | R']   -> HALT in I reading 0, ones = 2R' + 2z + 21

The period's effect is p → p−3, n → n+13, i.e. 3 D6 used and 13 zeros added, as the selector claimed.

**Grid results.**
- **T0.** Checked for b = 0..60, b = 366 (≡ B mod 3600), b = 846 and b = 2526 (≡ B mod 5040). That is 64/64 exact; b = 2526 took 2.3·10^10 steps.
- **T2, T4, T6, T8, T9, T10, PARK, GROW.** Each was checked on two grids, 0 failures in all 16:
  - **Dense grid.** m from m_min to m_min+3, plus 12 and 40; every z in 2..40, plus 77 and 160; R in {19, 22, 25, 43, 97, 100}. That is 1476 checks per stage.
  - **Real-class and size-order grid.** m in {m_min+1, 30}; z in {50, 113, 301, 1000}; R in {2539, 7579, 17659}, so R ≫ z, m. That is 24 checks per stage.
- **Head confinement.** For m ≥ 3 the head never reaches the farthest D6 tokens. T2, T6, T8 and T10 touch only the last one; GROW touches only the last two; T4, T9 and PARK touch none. So each map holds for every larger m.
- **HALT.** 879/879 cases halt in I reading 0, with ones = 2R + 2z + 21 exactly. The grid was z = 1..120, 200, 301, 1000 with R ≤ 7579.
- **GROW holds for m = 2.** With m ≥ 2 the HALT configuration does not halt: it is GROW.

**Follower runs** (`myfol.py`, own literal stages and jumps).

| b | representative | outcome | halting config | ones |
|---|---|---|---|---|
| 6 | 2539 (≡ r* mod 5040) | HALT after 26 stages | [6 0 1^197 \| 1 \| 2539] | 5493 = 2·2539+2·197+21 |
| 9 | 2539 | HALT | [6 0 1^273 \| 1 \| 2539] | 5645 |
| 12 | 2539 | HALT | [6 0 1^349 \| 1 \| 2539] | 5797 |
| 15 | 2539 | HALT | [6 0 1^425 \| 1 \| 2539] | 5949 |
| 366 (≡ B mod 3600) | 19 | HALT after 986 stages | [6 0 1^9317 \| 1 \| 19] | 18693 |

- **b = 6.** The token sequence agrees stage for stage with the selector's `c1_big_b6.log`, which is independent code.
- **b = 9, 12, 15.** All end in [6 0 1^((76b+135)/3)] and HALT with ones = 2·2539 + 2z + 21.
- **b = 366 with representative 19.** It ran 488 J1/J2 pairs with no left event. The final zero count is 9317 = (76·366+135)/3, and the ones are exactly 2·19 + 2·9317 + 21 = 18693.
  - Representative 19 is uniform with the real classes by the stage grids.
- **b = 366 with representative 2539.** The run was stopped at stage 47 for cost (`fol_b366_2539_partial.log`). It matched the period up to there.

## 4. Counting (real run)

- B ≡ 0 (mod 3), so p0 = 4B−1 ≡ 2 (mod 3).
- J1 sees p_j = 4B−1−3j and n_j = 8B+56+13j. GROW applies while p_j−1 ≥ 2.
- The run halts at the first j with p_j = 2, which is j* = (4B−3)/3.
  - Growth stages (full periods): (4B−3)/3.
  - J1/J2 pairs: 4B/3. These are the 8B/3 accumulator-sized ("full") clearings. They are each at depth n_j or n_j+1, from 8B+56 up to (76B+132)/3.
  - Final zeros: z_end = n_(j*) + 2 = (76B+135)/3.
  - Total jumps: 10 (transient) + 8B/3.
  - Total literal stages: 11 + 8B/3, including the halting stage.
- **The other residues.** If p0 ≡ 0 (b ≡ 1 mod 3) the first round ends at [4 (2R−7) 1^z], a left event. If p0 ≡ 1 (b ≡ 2 mod 3) it ends at an m = 0 growth, the unpack [0 1^z | R] → [7 1^(4R+z+4)]. Both start an R-sized second round. Neither applies to the real B.

## 5. Score

**One period in u-units.** Write U_j for the u-value of the accumulator whose token X_j = 2R−7 starts period j
(X_0 = 2R−1, which gives U_0 − 2 in place of U_0 − 4 below). The X-borrows are (2↑^(n+1))^(U−6)(4) = 2↑^(n+2)(U−4). So:

    U_(j+1) = 2↑^(n_j+3)( 2↑^(n_j+3)( 2↑^(n_j+2)( 2↑^(n_j+2)(U_j − 4) ) ) )
              [ 6->3 (J1) and D3->D0 (PARK+J2) at depth n_j+2;  4->1 at depth n_j+1;  X at depth n_j ]

**Final value.** With k = n_(j*)+3 = z_end+1, the final value is U_end = 2↑^k(2↑^k(Y)), where Y = 2↑^(k−1)(2↑^(k−1)(U−4)).
Then σ = 2R_end + 2z_end + 21 = 3·U_end + 2·z_end + 11.

**Lower bound.**
- U−4 ≥ 4 gives Y ≥ 2↑^(k−1)(2↑^(k−1) 4) = 2↑^k 4 = 2↑^(k+1) 3.
- Hence U_end ≥ 2↑^k(2↑^k(2↑^(k+1) 3)) = 2↑^(k+1) 5.

**Upper bound.**
- Every application has index ≤ k.
- There are at most 4·(4B/3) + 20 applications, starting from u = 4.
- So U_end ≤ (2↑^k)^(16B/3+20)(4) = 2↑^(k+1)(16B/3+22).

**Result.**

    2↑^N 5  <  σ  <  2↑^N (16B/3 + 23),     N = k+1 = (76B+141)/3 = (38·(2↑^37 3) − 11)/3 ≈ 25.3 B.

In FGH terms, σ ≈ f_(N+O(1))(O(B)): ω-level 1, index ≈ (76/3)B. The selector's "f_(n_end+2)^2" is the same thing: the
last two applications are 2↑^(z_end+1).

**Comparisons.** Each assumes the other machine's own analysis.

| machine | arrow index | σ |
|---|---|---|
| c1 | ≈ 25.3B | 2↑^N 5 < σ |
| M3 (`../bb10_fw1_verify.md`) | 8B+56 = 4·(2↑^37 3)+40 | σ_M3 > 2↑^(8B+56) 4; σ_M3 < 2↑^(8B+60)(small) |
| three-cycle F/H sibling | ≈ 4.8B+42 (K = (24B+191)/5) | ~ f_(K+42)(small) |
| D9 machine | | < f_(4.8B+3)(9B) |

- **M3.** Its upper bound holds because it is a handful of nested clearings at depth ≤ 8B+56, and each is one application of index ≤ 8B+58 by the closed form.
- **c1 vs M3.** N − (8B+60) = (52B−39)/3 ≈ 17.3B extra arrows, so c1 > M3.
- **c1 vs the others.** c1 beats the three-cycle sibling and the D9 machine by about 20.5B arrows.

    c1  >  M3  >  three-cycle sibling (padded)  >  0LA (padded)

## 6. Gaps

1. **Premise.** The base reaching K(0^35;0;B) at its first E0 read is the lead's premise. I did not re-check it.
2. **Grid checks, not proofs.** R1-R3 and the ten literal stage maps are grid-checked with head confinement, not proved. The real z (about 8B to 25B) and R (towers) are extrapolations from z ≤ 1000 and R ≤ 17659. The m-direction is rigorous, by confinement.
3. **T0 for general b.** It is checked on 64 values of b, including two real-class representatives. It is not proved; it needs a transfer-loop induction.
4. **No Coq.** A proof would need T0, the T2-T10 maps, GROW, PARK (= R3), the HALT stage, and the period as an induction on j.

Logs: `c1v/rules_s1.out`, `stages.out`, `t0.out`, `t0big.out`, `t0_2526.out`, `halt.out`, `fol_b*_*.log`. The two `*_BUGGY_leftevent.log` files come from a follower version whose left-event jump was wrong; it was fixed before `fol_b16_19_fixed.log`. Left events never occur in the real class.

## 7. The lead's two extra checks (`c1v/check2.py`, `check2.out`): 190/190 pass

The checks used five (p, n) cases: (20, 117), (8, 169) and (2, 195) from the b = 6 chain, (5, 1003) as an extra
large-depth case, and (1408, 3220) from the b = 366 chain. Each borrow was run literally to an exact target.

**(1) Per-period payment: no size-order dependence.**
- **The parked digits are paid only by borrows.** The digits D(2R-7) (made by GROW) and D(2R'+5) (made by PARK) are consumed one borrow at a time, by the next jump's R3 steps.
  - J1 starts with r = 1 (the GROW output is `| 1 | 1`), so no accumulator is compared with the parked digit.
  - Each borrow costs one full cycle in time.
  - No literal stage ever reads a parked digit together with an accumulator.
- **Both size orders were tested.** I ran the first borrow from the parked digit for every combination below. The result is always the exact R3 output, so it does not depend on which value is larger.
  - J1: X in {31, 5071, 35317}, crossed with r in {1, 19, 2539, 17659}.
  - J2: D in {43, 5083, 35329}, crossed with the same r values.
  - This covers the real start r = 1, r much smaller than the digit, and r much larger than the digit.
- **The last borrows also hold.** These are the borrow when the digit is down to 4, the 4 -> 1 borrow and the 6 -> 3 borrow, each for r in {19, 2539, 17659}.
- **Contrast with M3.** M3 breaks where an unpack stage compares a short-clearing accumulator with a long-clearing token. c1 has no such stage.

**(2) Final depth by crossed zeros.** I mapped the literal head excursion of each borrow to the token it reached. Then I counted the tokens strictly between that token and the a-token, and checked that all of them are D1.

| borrow | zero digits crossed |
|---|---|
| J1, X | n |
| J1, X's last unit | n |
| J1, 4 -> 1 | n+1 |
| J1, 6 -> 3 | n+2 |
| PARK, D3 -> D0 | n+2 |
| J2, D(2R'+5) | n+1 |
| J2, the digit's last unit | n+1 |

- **All exact.** All 190 cases matched these counts.
- **Depth growth.** The next J1 sees n+13: 2 zeros come from J1 (the X and 4 positions become D1), and 11 come from GROW (exact token match in the GROW grid).
- **Nothing inflates the depth.** The only structure beyond the D0/D3 blockers is the D6 run, and its tokens are never crossed: the head-confinement data show at most the last two D6 are touched. No parked list sits behind a blocker.
- So the depth sequence n_j = 8B+56+13j, the deepest borrow per period at n_j+2, and the final z_end = (76B+135)/3 are counts of crossed zeros.
