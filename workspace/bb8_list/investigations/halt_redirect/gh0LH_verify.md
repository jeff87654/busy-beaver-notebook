# Independent verification of `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH` (agent inv-gh0LH-verify, 2026-10-08)

## Verdict
**HALTS** (state I reading 0), at strong-evidence level, in a single round after **T(B) = (77B+413)/5 champion clears**.
The "D9 counter" is not the mechanism. The run is phase 1, then phase 2, then phase 3, each an affine period, and then a fixed end game.
All jump counts are explicit affine functions of B.
- The real class is b = 6 (mod 10). B = 16537583495166 (mod 18101949465600) gives B = 6 (mod 40) and B = 3366 (mod 4200).
- The real-class representatives b = 16, 26, 36, 46, 86 and 3366 all halt along the same path.
- The jump counts are T = 329, 483, 637, 791, 1407 and 51919. With b = 7566 (next in the B mod 4200 class) added, T = 116599. All seven match (77b+413)/5 exactly.
- **Score: about f_(m0+1)(f_m0(.)) with m0 = (24B+191)/5, that is about 4.8B Knuth arrows.**
  This is far above our BB(9) record and above the two-cycle 0LA machine.
- **It is most likely BELOW the three-cycle F/H sibling.** That machine's third cycle runs over D4^(m0+40), about f_(m0+40).
- The mini-follower's "about 21 stages per b" and its rebuilds come from small representatives, from b = 1 (mod 10) and from small b.
  They do not describe the real run.

## Tools (all new, in halt_redirect/ghv/; independent of follow2 / hyb10 / stage35g / numres)
- `kst.cpp` / `kst3.cpp`: literal runner to the next G-frame K-moment.
  A K-moment is state G, the tail (10)^4 left of the head, all blank right of the head, and the word to the left parsed into tokens D(m) = (10)^m 1 and gaps 0^k (k >= 2).
- `ksim6.cpp`: the same protocol on a block-6 macro tape with the chain rule. It also reports the leftmost head cell, for the locality check.
  It matched kst3 on 400 random configurations and on every test file, including step counts and halts.
  `ksim.cpp` / ksim2 is an independent block-2 variant, used by the verifiers.
- `hv2.py`: values for huge numbers. The 2-adic part is exact: a tower 6*2^N-6 is -6 mod 2^N. The odd part is a residue modulo MO = 3^20 5^12 7^8 11 13 17 19, which is lambda-closed.
  The attracting accumulator residue is **U = 49612750485498 mod 2^10 3^8 5^2 7 11 13 17 19**. I recomputed it from scratch and it equals the lead's numres value.
- `ghf8.py`: the follower. It works on run-length configurations with block groups `(pat)^c`, where c may be huge.
  - Champion clears are abstract (R1-R3), with a shortcut for long countdowns.
  - Every event is run literally on a right window of the configuration, with a locality check.
  - Huge values get representatives CRT(s2 mod 8, odd mod 315) + 2520k, and one +360 shift run per huge symbol, so outputs are read off as rational-affine functions.
  - Affine periods are skipped over 2 periods, including huge N.
  - It fails loudly on anything else.
  - Logs: ghv/s*.log, plus stage dumps ghv/f*.jsonl.
- Checkers:
  - `rulecheck.py`, `rulecheck3.py`: the champion rules.
  - `verify_stages.py`: re-runs every recorded stage with fresh or deeper representatives, using ksim2 or kst3.
  - `grid_check.py`: varies every long run count of every recorded stage.
  - Stage-0 reach jobs: `jobs_s0.txt`.

## 1. Macro structure (G-frame K-moments; config [tokens | a | r] followed by (10)^4)
**Champion rules.** These are the BB(8) record's R1-R3 in D-token form:
- R1 [a+3 | r] -> [a | 2r+6], for any a and any r.
- R2 [X+3 | 1 | r] -> [X | 2r+7 | 0].
- R3 [Y+3, 1^k | 1 | r] -> [Y, 2r+7, 1^(k-1) | 1 | 0].

Each holds literally as the next K-moment in every left context tested: random tokens, an empty context, 0^k gaps, and a gap right next to the active token (2 x 1200 checks, 0 failures).

A clear stops at an **event**:
- a in {0, 2} (an a-block);
- the borrow reaches a token 0 or 2 (a block);
- the borrow reaches a gap or the left end.

A long clear ends with accumulator R = U (mod M) and R = -6 (2-adically).

**Stage 0** (lead's result, re-checked):
K(0^35;0;b) = [D1^35 | 1 | 3b] -> [9^x, 11, 1^((24b+196)/5) | 1 | 1], with x = (12b+8)/5.
Equivalently -> [9^x 8 6 4^((24b+186)/5) 1 | 37 | 18].
- My follower reaches it literally for b = 1, 6, 11, 16, 21, 26, 31, 36, 46, 86.
- reach2.exe confirms it for b = 3366 (2.6e10 steps).
- Inside stage 0, the D9 region is built one D9 per K-moment, with period 1, 5 zeros spent and 2 gained. This is skipped by acceleration.

**Phase 1** (zero list; block building).
The first jump clears D4^((24b+186)/5). Then each stage is one event, and one full champion cycle runs over the current zero list.

The 7-stage period in steady state:
```
(A = 2R+7 huge; m = zeros right of the failing D0; R = accumulator at the event.
 The next jump clears 1^m behind a huge leading counter, then stops at the D0/D2 shown.)
[.., A, 0, 0 | 1^m | 1 | R]          -> [.., A-4, 2, 0, 2R+6, 1^(m-1) | 1 | 0]
[.., A, 2, 0, 0 | 1^m | 1 | R]       -> [.., A-3, 2, 1, 0, 2R+6, 1^(m-1) | 1 | 0]
[.., A, 2, 1, 0, 0 | 1^m | 1 | R]    -> [.., A-4, 4, 0, 0, 1, 2R+6, 1^(m-1) | 1 | 0]
[.., A, 4, 0, 0, 1, 0 | 1^m | 1 | R] -> [.., A, 1, 3, 0, 0, 2R+7, 1^(m-2) | 1 | 0]
[.., A, 1, 3, 0, 0 | 1^m | 1 | R]    -> [.., A-3, 4, 0, 1, 2R+5, 1^m | 1 | 0]
[.., A, 4, 0, 1, 2 | 1^m | 1 | R]    -> [.., A-4, 6, 0, 0, 2R+8, 1^m | 1 | 1]
[.., A, 6, 0, 0, A', 0 | 1^m | 1 | R] -> [.., A-8, 10, 0, 0, A'+2, 0, 0, 2R+7, 1^(m-2) | 1 | 0]   (A' = 2R'+5)
```
Over one period, A drops by 26, so each finished block is [2R-19, 10, 0, 0]. One period uses 6 zeros and appends one block.
- Number of periods: N1 = (4b-34)/5. For b = 3366 that is 2686.
- Total phase-1 stages: 75 + 7*N1, about 5.6b.
- Each stage is a full omega-level cycle at level m, the current zero count. m falls from (24b+196)/5 to about 15, by 6 every 7 stages.

**Phase 2** (blocks consumed).
- The period is 14 jumps (33 events) and consumes 2 blocks.
- Typical maps:
  - `[.., 2R-19, 10, 0, 0, 2 | 1 | 1 | R] -> [.., 6, 2, 0, 2R+7, 1, 1, 1 | ..]`
  - halving stages such as the a-block `[.., S1, S2, 0 | 0 | 42] -> [.., S2-1, S0 + S1/2 - 3/2, S1+88, 1 | 0]`
  - a stage whose output is `2 S0 + 7/4 S1 + 7/4 S2 + 45/4`, combining three huge tokens. Exact forms are in the X lines of ghv/s3366.log.
- Number of periods: N2 = (2b-37)/5. For b = 3366 that is 1339.
- All lists here are short (at most about 6 positions), but the leading counters are huge.

**Phase 3** (D9 region).
- After a transient of about 20 D9s, the period is 14 jumps (35 events) and consumes 8 D9s.
- The maps are `[9^x 8 0 | 1 | R]`, then `[9^x 5 10 0 0, 2R+7]`, ..., then `[9^(x-4), 8, 12, 1, 2R+35, 1 1 1]`, with halvings again.
- Number of periods: N3 = (3b-78)/10. For b = 3366 that is 1002.

**End game** (b-independent; identical for all six real-class b):
```
J342  [8, 0 | 1 | R342]      -> [2R342+12, 1^8, 0, 2, 3, 0, 0 | 1 | 1] -> [2R342+9, 8, 1^3, 0, 1, 3, 0, 5, 1^2 | 1 | 0]
J343  clear (short list)     -> event [A = 2R342+9, 8, 1^3, 0, 1, 3, 0, 2, 1^2 | 1 | R343]
      literal                -> [A, 7, 2, 0^2, D0, 0^4, D1, B = 2R343+7, 1, 0, 1, 1 | 1 | 1]
      literal                -> HALT in state I reading 0, ones = A + B + 36 = 2 R342 + 2 R343 + 52
```
- The ones formula is fitted on 6 representative pairs (exact).
- It was re-run with representatives matched mod 2^12 * 315: same halt, same formula.

**Count.**
T(b) = 343 explicit jumps + 7*N1 + 14*N2 + 14*N3 = **(77b+413)/5**.
- For B this is integral, since B = 6 mod 10.
- About 5.6B of these are full cycles over a long list (the zero list).
- The rest run over lists of at most about 6 positions, with huge counters.

**Why the real B takes this path.** All per-period remainders are fixed by b mod 10:
- x = (12b+8)/5 = 24k+16, which is 0 mod 8, so phase 3 ends at `[9^0 8 0 1 1 R]`;
- m0 = 48k+67 is 1 mod 6 and 7 mod 12, which fixes how phase 1 and phase 2 end.

The accumulators are U-class in every period. B = 6 mod 10, so B takes the same path as b = 16, 26, 36, 46, 86 and 3366.
- For b = 1 (mod 10), x = 4 (mod 8). Phase 3 then ends at a different left end, `[0 1^k | 1 | R]`, which **rebuilds** a list of length about cR. That gives a second round from K(0^n'; 0; b') with n' and b' huge.
  - b = 1 went through round 2 and halted.
  - b = 11, 21 and 31 stop in round 2 with an honest FAIL: a stage's structure depends on the order of magnitude of R against a huge count, which residues cannot decide.
  - None of this concerns the real B.
- b = 6 also rebuilds, because its 13 D9s end inside the phase-3 transient. It is a small-b effect.
- The other session's mini-follower (r = 19 representatives, b0 = 6 and 46) therefore saw rebuilds and different stage counts.

## 2. Literal verification
- Champion rules R1-R3: 2 x 1200 random literal checks, 0 failures (`rulecheck.py`, `rulecheck3.py`). Contexts included gaps and the empty context.
- Stage 0: literal, as listed above.
- Every event stage of the real-class runs is literal on configurations the run actually reaches:
  - each with 2 or more representative sets (base plus one +360 shift per huge symbol);
  - structural mismatch, non-affine dependence or a locality breach fails loudly;
  - none occurred for b = 16..3366.
- Re-verification:
  - `verify_stages.py`, fresh representatives (2520j), ksim2 and kst3, b=1 dump: 33/33.
  - Real-class dump f3366 (454 stages), fresh representatives: **454/454 pass**.
  - Deeper 2-adic matching: mod 2^5 * 315, sample of 60: **60/60 pass**. Mod 2^7 * 315, sample of 40: **11/11 completed pass**; 29 exceeded a 3e10-step budget.
  - Count grids (every long run count c -> c+0, 3, 6, 9, 30; all outputs affine), b=86 dump (463 stages): **327 grids, 0 failures**.
- Residue dependence. Stages depend on huge values only through their residue mod 8 and mod 315 (the +360 shift test). Some phase-2 and phase-3 stages halve huge tokens, with coefficients 1/2, 3/2 and 7/4. So the 2-adic digits matter.
  - The follower tracks them exactly: towers are -6 mod 2^(huge).
  - The final stages were re-run matched mod 2^12.
  - Representatives mod 2520 alone are faithful only mod 8. That suffices here, but it is not true in general.
- In-class repetition: b = 7566 (= B mod 4200, next representative) **halts on the same path with T = 116599 = (77*7566+413)/5**.
- Independent plain simulator: kst3.exe re-ran a sample of 60 stages from the b=86 dump with fresh representatives. 59/59 completed pass; 1 exceeded the step budget.

## 2b. Size ordering of accumulators (added on the lead's request)
**The halting path survives realistic size ordering.**

Values in the follower:
- Accumulators from short clears stay exact while below 2^60 (for example 18, 42, 98298 = 6*2^14-6 and 196601).
- Every larger value is a symbol with exact residues.
- Literal stages then use small, arbitrarily ordered representatives. This is the representation that misled M3, so every stage was re-tested under realistic orderings with `ghv/order_check.py`.

What the test does:
- Every huge representative is forced above 2 * (largest exact token or count in the window) + 2520. Real huge values exceed 2^60, which exceeds every exact value in the run.
- The huge symbols are put in several size orders: the follower's order, reversed, accumulator smallest, accumulator largest, and two random orders. Successive representatives differ by a factor of 3.
- The literal output must equal the follower's affine forms.

Results:

| Real-class dump | Ordered runs | Failures | Over budget |
|---|---|---|---|
| b = 16 (all 372 stages with huge symbols) | 1264 | 0 | 174 at a 2e10-step budget |
| b = 16, the 68 over-budget stages again at 1e13 steps | 326 | 0 | 0 |
| b = 86 (all 454 such stages), 1e13 steps | 1463 | 0 | 0 |

The over-budget cases were pure budget effects: the same stages, with a larger budget, finished with the predicted output.

Where an accumulator meets a token built from another value:
- Two exact-against-huge stages sit in the phase-3 transient:
  - `[.., 6, H, 2 | 1 | 98298] -> [.., 6, H-3, 196604 | 1 | 1]`;
  - `[.., 6, H, 196601 | 0 | 42] -> [.., 5, (H+393199)/2, H+88 | 1 | 0]`.
  - Both were re-run with H on either side of the exact value, from 2.5e3 to 1.0e6. The output is the same affine form each time.
- About 70 stages per run combine 2 or more huge values (for example `S0 + S1/2 - 3/2` and `2 S0 + 7/4 S1 + 7/4 S2 + 45/4`).
- Across all 1677 symbolic outputs of the real-class runs, **no coefficient on a huge value is negative**. No stage subtracts one huge value from another, so no accumulator "pays for" an earlier token in this machine.
- The abstract champion clears never compare magnitudes.

## 3. Score
Let m0 = (24B+191)/5, about 4.8B.
- The stage-0 jump gives about f_m0(18).
- Phase-1 stage k clears a list of m0-k zero positions behind a huge leading counter (about 2R). That is about f_(m0-k+1)(R).
  - The composition f_1 o ... o f_(m0+1)(f_m0(18)) lies between f_(m0+1)(f_m0(18)) and f_(m0+2)(f_m0(18)).
- Phases 2 and 3 apply only short-list clears, which are f_c with c at most about 7, about 10B times. That adds at most one f_8 application.
- The end game gives sigma = 2 R342 + 2 R343 + 52, where R342 is about 2^^(about X), a tower over the last huge token.

**So sigma is about f_(m0+1+eps), roughly 2 ↑^((24B+186)/5) (2 ↑^((24B+181)/5) ...).** That is about 4.8B arrows.

Comparisons:
- **BB(9) record**: sigma about 3*(2 ↑^(12B9-9) 8), with 2B9+4 = 2^^13 3. Our arrow count, about 4.8B with 2B+4 = 2^^37 3, is incomparably larger. This candidate wins by far.
- **0LA (two cycles)**: about f_m0(f_m0(.)). This candidate is larger: it adds about 5.6B more cycles, the first at level m0+1 with a huge argument.
- **F/H three-cycle sibling** (`..._1LC1RH_0LH0RF_---0LA`): per the lead's verified stage 2, its third cycle clears D4^(m0+40) from a small accumulator, about f_(m0+40)(c), roughly 2 ↑^(m0+39) c.
  - f_(m0+40)(c) >= f_(m0+3)(f_(m0+3)(.)), which exceeds anything this machine reaches.
  - Many cycles at levels up to m0+1 do not beat one cycle 39 levels higher.
  - **Expect the sibling to be larger. I did not verify the sibling myself.**

## 4. Evidence level and open gaps
Evidence: **strong**. This is an independent follower with exact 2-adic and residue values and literal stages on reached configurations. The periodic structure is identical across six real-class b over three orders of magnitude, and T matches a closed formula. Gaps a Coq proof must close:
1. **Champion rules for all contexts and parameters.** Literal sampling only, with gaps and empty contexts included. The record's Coq proof covers R1-R3, but in the base machine's frame. Contexts with 0^k gaps and a-blocks (a in {0, 2}) need the general statement.
2. **Event stages as parametric lemmas.** About 40 distinct event shapes appear in the periodic regimes, plus the transients and the end game. The halving stages need 2-adic case splits (value mod 8 and mod 4).
3. **Accumulator facts.**
   - Every long clear ends with R = -6 (mod 2^K, K large) and R = U (mod the odd part).
   - The countdowns involved are deep enough: towers of height at least 300, against a stabilisation depth of about 18.
   - Exact small accumulators also appear (for example 98298 = 6*2^14-6). The follower handles them exactly, but a proof must too.
4. **Affine-period induction** for stage 0 and phases 1-3 (four inductions with explicit counts N1, N2, N3), plus the phase-3 transient of about 20 D9s.
5. **Window locality.** The follower checks that literal stages never enter the first window item. A proof needs the matching locality lemma.
6. **Score.** Only the class f_(m0+O(1)) is established. The exact ones count is 2 R342 + 2 R343 + 52, but R342 is defined through the whole run.
