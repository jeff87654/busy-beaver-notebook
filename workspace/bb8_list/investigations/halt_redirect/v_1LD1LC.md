# G/H twin 1LD1LC: independent verification (fable-1LD1LC, 2026-10-08)

Machine (10 states, I0 undefined = halt):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_1LD1LC

= the G/H-swap sibling of the BB(8) record with E0 := 1LI, I = (halt, 0LJ), J = (1LD, 1LC).  The record-base twin
`..._1RG1LD_1LC0RH_1RG1LF_---0LJ_1LD1LC` is owned by inv-bb10-fw1-verify (bb10_m3j_verify.md); my std/big/shrink runs
and one whole real-class chain of it are token-for-token identical to the G/H twin (only step counts differ).
Tools and logs: `halt_redirect/v1LD1LC/`.

## Verdict

**HALTS in state I reading 0 after 11 jumps (6 macro clearings).  Omega-level 1, NOT omega-level 2.  Not a BB(10)
record candidate: it is below M3 by about 3.2B arrows.**

- Every jump clears one token at the NEAR end of the list, at depth m + c with c in {0,...,6}, m = (24B+191)/5
  (= 1075 mod 2520, = 0 mod 5), and is stopped by a D0 blocker.  Literal zero counts: 67..71 at u = 16 (b = 6), and
  1075..1079 at u = 520 (the real class mod 2520), under every representative policy.
- The "list length proportional to an accumulator" in the screening is three PARKED pair lists, (0 3)^((R2-5)/2),
  (1 0)^(R4-11) and (0 3)^((R6+1)/2), which sit behind D0 blockers.  No borrow ever crosses them (a D0 blocks the
  borrow), and the only literal stage that touches them is stage 8, which consumes 3 pairs.  A long list is not a deep
  clearing; the depth that decides the omega level is the zero run next to the a-slot, and that stays m + O(1).
- The M3 trap (an unpack paid for by a smaller, later accumulator) does not occur: the unpack stages (4 and 6) and the
  halting stage are affine in BOTH the parked token and the current accumulator, with both size orders checked,
  and whole chains with the real size order, the reversed order and all-equal representatives halt identically.
- Score: `2^(m+6) 5 < sigma < 2^(m+6) 6` in arrows, m + 6 = (24B+221)/5 ~ 2.4 * (2^(37) 3) + 44.  One f_omega-scale
  application, roughly f_omega(f_38(3)).
- Ranking (paper level, each step conditional on the other machine's chain):
  M3 (> 2^(8B+56) 4) > F/H three-cycle sibling (~ m+43 arrows) > **1LD1LC twins** > 0LH D9-counter (< ~2^(m+4) 3)
  > 0LA (< 2^(m+3) 4) > peer 0LJ0LC > BB(10) champion (< 2^(N')(2N'), N' < 2^(25) 49).
- Confidence: high for halting and the level (three independent followers, literal stage grids, whole chains with
  four size orders at the real class mod 2520, and the peer's independent chain agree); the size class is exact given
  the record's Coq clearing lemma.  No Coq.

## 1. Conventions

Tokens D(k) = (10)^k 1, listed farthest first, then `| a | r` (a-token, accumulator token); the head is on the blank
right of the tail `1010` in state G (family GH of mf35g, offset e = 1).  Ligocki units: r = 3b+1, digit d = D(3d+1),
D1 = zero.  Champion rules (e = 1): R1 a >= 4: a -= 3, r -> 2r+5; R2/R3: borrow one unit from the nearest token >= 3
(any residue), refill 2r+5 next to it (or as the a-token), r := 1.  D0 and D2 block a borrow (-> E0 -> I/J: a literal
stage); D3 is borrowed to D0 like an ordinary R3 step.
Record clearing functions (Coq U_closed): a unit at depth d maps b -> V_(d-1)(b), 2 V_j(x) + 4 = 2^(j+1)(2x+4); a digit v
at depth d from b leaves V_(d-1)^v(b).  Hence V_j^n(0) satisfies 2 V_j^n(0) + 4 = 2^(j+2)(n+2).
Real residues (numres): every accumulator r == 19 (mod 2520), R = r-1 = 49612750485498 (mod 54305848396800);
u = (12B+8)/5 == 520 (mod 2520), m = 2u+35 == 1075 (mod 2520).  Representatives: r = 19 + 2520k.

## 2. Macro dynamics (literal stage -> jump), u = number of D9, m = 2u+35

| # | K-moment (literal stage output) | jump: what is cleared, depth, new accumulator |
|---|---|---|
| S0 | X(b,35) -> [9^u 11 1^(m+1) \| 1 \| 2] | J0: 11->8 (r=2, refill 9 at depth m+1), 9->6->3: b1 = V_m^2(0); event at D3 |
| S1 | [9^u 8 3 1^m \| 1 \| R1] -> [9^u 8 0 (2R1+5) 1^(m-1) \| 1 \| 1] (R3 from D3) | J1: digit 2R1+5 at depth m: b2 = V_m(b1) = V_m^3(0); D0 blocks |
| S2 | [9^u 8 0 1^m \| 1 \| R2] -> [9^(u-1) 5 3 0 3 (2R2+3) 1^(m+2) \| 1 \| 2] | J2: (2R2+3)->2R2 (refill 9 at m+2), 9->6->3: b3 = V_(m+1)^2(0) |
| S3 | [.. (2R2) 3 1^(m+1) \| 1 \| R3] -> [.. (2R2) 0 (2R3+5) 1^m \| 1 \| 1] | J3: 2R3+5 at depth m+1: b4 = V_(m+1)^3(0); D0 blocks |
| S4 | [9^(u-1) 5 3 0 3 (2R2) 0 1^(m+1) \| 1 \| R4] -> [9^(u-1) 2 7 0 0 3 3 (0 3)^((R2-5)/2) 0 (2R4+3) 1^(m+3) \| 1 \| 2] | J4: (2R4+3)->2R4, 9->6->3 at m+3: b5 = V_(m+2)^2(0) |
| S5 | [.. (2R4) 3 1^(m+2) \| 1 \| R5] -> [.. (2R4) 0 (2R5+5) 1^(m+1) \| 1 \| 1] | J5: 2R5+5 at depth m+2: b6 = V_(m+2)^3(0); D0 blocks |
| S6 | [.. (0 3)^k 0 (2R4) 0 1^(m+2) \| 1 \| R6] -> [.. (0 3)^(k-2) 0 0 5 (1 0)^(R4-11) 0 1 1 7 1 1 0 3 3 (0 3)^((R6+1)/2) 0 7 1^(m+5) \| 1 \| 2] | J6: 7->4 (refill 9 at m+5), 9->6->3: b7 = V_(m+4)^2(0) |
| S7 | [.. 0 4 3 1^(m+4) \| 1 \| R7] -> [.. 0 4 0 (2R7+5) 1^(m+3) \| 1 \| 1] | J7: 2R7+5 at depth m+4: **b8 = V_(m+4)^3(0)**; D0 blocks |
| S8 | [.. (0 3)^j 0 4 0 1^(m+4) \| 1 \| R8] -> [.. (0 3)^(j-3) 0 2 1 1 **(2R8+5)** 1^4 0 0 9 1^(m+1) \| 1 \| 1] | J8: 9->6->3 at depth m+2: b9 = V_(m+1)^2(0) |
| S9 | [.. 0 0 3 1^(m+1) \| 1 \| R9] -> [.. 0 0 0 (2R9+5) 1^m \| 1 \| 1] | J9: 2R9+5 at depth m+1: b10 = V_(m+1)^3(0) = b4 |
| S10 | [.. (2R8+5) 1^4 0 0 0 1^(m+1) \| 1 \| R10] -> [.. (2R8+5) 1 0 1 (2R10+3) 1^(m+2) \| 1 \| 1] | J10: (2R10+3) borrowed to D2, (2b10+1) units at depth m+3: b11 = V_(m+2)^(2b10+1)(0); D2 blocks |
| S11 | [.. (2R8+5) 1 0 1 2 1^(m+2) \| 1 \| R11] -> **HALT, I reading 0** | |

(The model's jump() stops at the D3 after 9->6->3; the literal stage then does the third unit 3->0 as an R3 step.
"S1/S3/S5/S7/S9" are therefore ordinary R3 steps, not new routines.)

**Exact sizes** (from the V closed form; j-th accumulator R_j = 3 b_j + 1):

    2b2+4 = 2^(m+2) 5,  2b4+4 = 2b10+4 = 2^(m+3) 5,  2b6+4 = 2^(m+4) 5,  2b8+4 = 2^(m+6) 5,
    2b11+4 = 2^(m+4)(2b10+3) = 2^(m+4)(2^(m+3) 5 - 1)  (so 2^(m+5) 3 < 2b11+4 < 2^(m+5) 5),
    and b1, b3, b5, b7, b9 are the two-unit resets V_d^2(0), 2V_d^2(0)+4 = 2^(d+2) 4.

**Real size order:** R1 < R2 < R3 < R4 < R5 < R6 < R7 < R8, then R9 = R3-size (same construction, same depth),
R10 = R4 (identical), R11 between R6 and R8.  So at stages 10 and 11 the PARKED token D(2R8+5) is much larger than the
current accumulator (R10, R11), the opposite of the shrink policy; at stages 4 and 6 the parked token (2R2, 2R4) is
smaller than the current accumulator (R4, R6), as in shrink.  Both orders were checked for every stage that reads a
parked token (section 3).

**Where an accumulator could pay for a token (the M3 question):** nowhere.  S4 unpacks the parked 2R2 into
(0 3)^((R2-5)/2) and converts the current R4 into a token 2R4+3; S6 unpacks the parked 2R4 into (1 0)^(R4-11) and
spreads the current R6 into (0 3)^((R6+1)/2); S8 converts R8 into the parked token 2R8+5; S10 converts R10 into
2R10+3; S11 unwinds R11 into a (10)-tail and then rewrites the near end (the D(2R8+5) token and a bounded number of
pairs) into junk and halts.  No stage subtracts one accumulator from another; the only counters are the small tokens
(11, 9, 7, 4, 3) consumed by the jumps.

## 3. Literal checks (all with the stage server stage35g.exe at Idle priority; every mismatch is printed and fatal)

| check | file | cases | result |
|---|---|---|---|
| stage 0 from the GH base's E0 configuration after K(0^35;0;b), b = 1 mod 5, b = 1..196 and 846 | `stage0.py` (`e0cfg.exe`), log `stage0_grid.log` | 41 | all exactly [9^u 11 1^(m+1) \| 1 \| 2], u = (12b+8)/5, m = 2u+35 |
| S1 (R3 from D3): u in {1,2,16}, z in {1075, 3595, 20..40}, r in {19, 2539, 5059} | `stages.py S1` | 207 | 0 mismatches |
| S2: u in {1,2,3,16,520}, same z and r | `stages.py S2` | 345 | 0 mismatches |
| S3, S4, S6, S8, S10 templates | `stages.py` (grids written; the broad run was stopped at the 1-process CPU cap) | spot checks only (section 3b) | |
| halting stage S11: z = 60..75 and 1075, 1077, 1080; (P, r) in {(19,19), (2539,19), (19,2539)} | `s11probe.py` | 57 | all HALT I0 |
| whole chain, real class u = 520 (m = 1075), representatives in the REAL size order (ranks 1..8, 3, 4, 6) | `chain.py`, `chain_u520_real.log` | 1 | HALT I0 after 11 jumps, ones 123247 |
| whole chain, u = 520, reversed order (8..1, 1, 1, 1) | `chain_u520_rev.log` | 1 | HALT, same structure, ones 113167 |
| whole chain, u = 520, all representatives 19 | `chain_u520_std.log` | 1 | HALT, same structure, ones 7327 |
| whole chain, u = 16, real order | `chain_u16_real.log` | 1 | HALT, same structure, ones 151716 |
| ord_run std / big / shrink at b0 = 6 | `std_b6.log`, `big_b6.log`, `shrink_b6.log` | 3 | HALT after 11 jumps; zeros 67..71 in every jump |
| R1/R2/R3 in the run's contexts (reach2.exe): 11 contexts, a or d in {3..12, 38, 41, 43, 44, 45, 5081, 5083}, z in {1,2,3,5,10,67,1075}, r in {1,2,3,4,5,7,19,40,2539} | `rules.py`, `rules_jobs.txt` | 13,893 | all 13,893 REACHED (0 failures) |

3b. Spot checks of the other templates in the whole-chain runs (which run every stage literally at u = 16 and
u = 520): S4 gave (0 3)^2525 from 2R2 = 2*5059 (= (R2-5)/2) and 2R4+3 = 20201; S6 gave (1 0)^10088 = R4 - 11 and
(0 3)^7570 = (R6+1)/2 with R6 = 15139; S8 gave (0 3)^7567 and the parked 2R8+5 = 40363; S10 gave 2R10+3 = 20201;
and the same formulas hold with reversed and all-equal representatives (so the counts really are the stated affine
functions of the stated tokens, with the other tokens irrelevant).  The literal S4 at (R2, R4) = (19, 7579) and
(7579, 19) gave the same template (`lit1.py` runs in the transcript).

**The halting stage S11** (`s11probe.py`, `etrace.exe` trace): it first unwinds the accumulator D(r) into a (10)^(2r+2)
tail (K-moments in G with r, r-1, ..., 0), then rewrites the near end into a non-token junk pattern, eating leftwards
through the D(2R8+5) token and at most a few pairs of the (0 3) list, and halts in I reading 0.  Its ones count
depends on z mod 5 (z = the zero run = m+2):

    z = 0, 2 (mod 5):  ones = P + r + 9z/5 + c0     (the parked token D(2P+5) contributes P, not 2P+6)
    z = 1, 4 (mod 5):  ones = 2P + 2r + 9z/5 + c1
    z = 3 (mod 5):     ones = 2P + 2r + 6z/5 + c3

with c0 = 208 at u = 2, k = 5, A = 19, j = 7 (e.g. P = r = 19: z = 60 -> 316, 65 -> 325, 1075 -> 2143, 1080 -> 2152;
P = 2539: + 2520; r = 2539: + 2520).  The REAL class is z = m+2 == 2 (mod 5) (m == 0 mod 5 since B == 16 mod 25), the
first line.  Halting is independent of the class and of the order of P and r in all 57 probes and in all whole
chains.  The peer's formula for the record-base twin, ones = Y/2 + A/2 + 9w/5 + c, is the same statement in their
raw units.  The step count of S11 is about (P + r) * z * 10 (6e8 steps at u = 520 with P = 40363, r = 15139), i.e. the
routine's work is linear in the parked token and the accumulator; it does not scan the parked lists.

## 4. Score

Halting configuration (real class): the tape holds 9^(u-1), the junk head, the parked lists (0 3)^((R2-9)/2),
(1 0)^(R4-11), (0 3)^((R6-5)/2), the rewritten D(2R8+5) region and the unwound R11.  With the real-class ones formula,

    sigma = R8 + R11 + (5/2) R2 + 3 R4 + (5/2) R6 + 9m/5 + O(u)   (+1 if the undefined transition is counted as writing a 1),

dominated by R8 = 3 b8 + 1 with 2 b8 + 4 = 2^(m+6) 5 EXACTLY (section 2).  Hence

    sigma > R8 > (3/2) 2^(m+6) 5 - 5 > 2^(m+6) 5,        sigma < 6 * 2^(m+6) 5 < 2^(m+6) 6,
    m + 6 = (24B + 221)/5,  2B + 4 = 2^(37) 3,  i.e.  m + 6 = (12 * 2^(37) 3 + 173)/5.

FGH: one f_omega-scale application with index ~ 4.8B + 44 ~ 2.4 * 2^(37) 3, roughly f_omega(f_38(3)); level 1.

Comparisons (arrow counts; `2^(n) x` = n Knuth arrows):
- BB(10) champion: sigma_10 < 2^(N')(2N'), N' < 2^(25) 49 (score_comparison.md section 6).  Since m+6 > N'+2,
  sigma > 2^(m+6) 5 > 2^(N'+2) 3 = 2^(N')(2^(N') 4) > 2^(N')(2N') > sigma_10.  The twins beat the champion.
- M3: sigma_M3 > 2^(8B+56) 4 (bb10_fw1_verify.md) and 8B+56 > m+7, so sigma_M3 > 2^(m+7) 3 > 2^(m+6) 6 > sigma.
  **M3 stays the best BB(10) candidate**; the twins are about 3.2B arrows below it.
- F/H three-cycle sibling (9 states, `..._1LC1RH_0LH0RF_---0LA`): its third clearing is at depth ~ m+42
  (list D4^(m+40)), giving ~ 2^(m+43)(..) > sigma.  Above the twins, if its chain holds.
- 0LH D9-counter (9 states, gh0LH_fable.md): sigma_0LH < f_(m+3)(9B) ~ 2^(m+3)(9B+c) < 2^(m+4) 3 < sigma.  The twins
  are above it by about two arrows (conditional on that upper bound).
- 0LA: sigma_0LA < 2^(k+4) 4 = 2^(m+3) 4 < sigma.
- The peer's bound for the record-base twin, sigma > 2^(z+2)(2^(z) 3) with z = m+2, is a valid lower bound but their
  size order "F4 << F6" is reversed: their F4 (my R8, three units at depth z+3) is the largest accumulator, their F6
  (my R11) is below it by about two arrows.  Correcting this strengthens the bound to 2^(m+6) 5 = 2^(z+4) 5.

## 5. Cycle count and halting event

- Omega-level-1 full cycles: 11 jumps (each clears a token across the m + O(1) zero run); of these, J1, J3, J5, J7, J9
  clear a huge digit (2R+5, (2R+4)/3 units), J10 clears a huge residue-2 token to D2 ((2R10+1)/3 units), and J0, J2,
  J4, J6, J8 are three-unit resets (one unit from a small token 11/41/41/7/9, then 9->6->3 and the R3 step 3->0).
  Macro clearings (reset + full digit): 6.
- Omega-level-2 cycles: 0.
- Final event: in S11, after the champion process is blocked by the D2 that J10 leaves, the machine reads E0 -> I ->
  J, unwinds R11, rewrites the near end and halts in **I reading 0**.

## 6. Agreement with the other sources

- The lead's follow2 run (`f_gh_1LD1LC.log`): 11 full cycles, level 1, HALT (I, 0), ones = R11 + 5/2 R2 + 3 R4 +
  5/2 R6 + R8 + (816 b + 2419)/25 in its units: the same formula shape as section 4.
- The lead's ord_run std/big/shrink: 11 jumps, zeros 67..71, HALT I0 (reproduced).
- inv-bb10-fw1-verify on the record-base twin (bb10_m3j_verify.md, read after my verdict): halts at I0, level 1,
  parked lists behind D0 blockers, no size-order dependence, ones = Y/2 + A/2 + 9w/5 + c in the real class.  Full
  agreement on the chain and the halt; the one correction is the size order of F4 vs F6 (section 4).
- Why the screening said "level 2": it read the total list length (parked pairs, proportional to R2, R4, R6) as a
  cleared length.  follow2's own level bookkeeping (zero count of the event configuration) never said level 2.

## 7. Gaps for a Coq proof

1. The GH base machine itself: that `..._0RG1LD_1RH1LG_1LC0RG` reaches the exhaustion K(0^35; 0; B) at its first E0
   read, with the same B as the record (the record has this in Coq; the G/H sibling needs its own copy of the
   machine-level part).
2. Stage 0 for general b (literal for 41 values of b up to 846; a parametric lemma in b is needed, as for 0LA).
3. R1-R3 on lists containing the non-digit tokens 9, 8, 7, 5, 4, 3, 2, 0, 2R+3 and the pair lists (the record's Coq
   covers standard contexts; here they are literal-checked only).
4. The literal stages S2, S4, S6, S8, S10 as parametric lemmas (affine in r, in the parked token, in the zero run and
   in u), plus S1-type R3 from D3.  Residue hypotheses: r == 19 (mod 2520) was used throughout; which residues each
   stage actually needs (parity of R2 and R6 for the pair counts, probably r mod 4 or mod 8 for the unpacks, m mod 5
   for the halting stage) is not isolated (`rsweep.py` was written for this but not run under the CPU cap).
5. The halting stage S11 for astronomically large P, r, z: literal for P, r <= 40363 and z <= 3597 with the real
   class z == 2 (mod 5); its uniformity in the class is the same extrapolation as M3's exhausted-transit regime.
6. The jump model: the abstract champion process with blockers and the fixed-point residues (numres); the sizes use
   only the record's U_closed and the depths read off the literal K-moments.

## 8. Reproduction (`halt_redirect/v1LD1LC/`)

- `python idle.py vrun.py --policy {std,big,shrink} --log X.log` (ord_run policies; `blk.py X.log` compresses lists);
- `python idle.py chain.py --u 520 --ranks 1,2,3,4,5,6,7,8,3,4,6 --log X.log` (whole chain, explicit size order);
- `python idle.py stage0.py grid`, `python idle.py stage0.py 846`;
- `python idle.py stages.py S1 --quick` etc. (`--full` for the 7-residue grids, `rsweep.py` for residue sweeps);
- `python idle.py s11probe.py`; `python idle.py rules.py` (reach2.exe rule checks);
- `python idle.py lit1.py "9^15 5 3 0 3 38 0 1^68" 1 19` (one literal stage).
