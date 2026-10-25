# Independent check of the M3 f_(ω+1) claim (inv-bb10-fw1-verify, 2026-10-08)

Machine M3: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA`.
It is the BB(8) record with E0 = 1LI, I = ---0LJ (I0 halts) and J = 0LD0RA.
Tools and logs: `bb8_list/investigations/bb10_fw1_verify/`. Everything below was derived with my own simulator and parser.
I read the originating agent's files only at step 5.

## Verdict

**The f_(ω+1) claim is false. M3 halts at the end of its FIRST period**, i.e. at the second D0-blocked unpack.
- This is the same place as the originating agent's corrected "S2 of period 2" (after 7 jumps; section 6 maps the
  names).
- The machine halts in state I reading 0. The counter C has been used once (C −= 11); the refill and the second
  counter are never reached.

**Size.** σ is ω-level 1: a few nested clearings at depth ≈ 8B + 56, where 2B + 4 = 2↑^37 3.
- σ_ones = 3/2·A'' + A1 + 3/5·A''' + (212B + 563)/5 (+1 if the halting transition writes a 1);
- σ > 2↑^(8B+57)(2↑^(8B+54)(2↑^(8B+52) 3)) > 2↑^(8B+56) 4, with 8B + 57 = 4·(2↑^37 3) + 41.

**Ranking.** Each comparison assumes the other machine's own stage chain (section 5b):

    M3 > bb8-ab's 3-cycle sibling (padded) > 0LA (padded) > 0LJ0LC > BB(10) champion

M3 beats both 0LA-type machines by about 3.2B arrows in the arrow count.

**Status: strong evidence, no Coq.** It rests on:
- every stage being a parametric rule checked literally on random instances, with 0 mismatches;
- the clearings using only the record's R1/R2;
- the period-internal order (S6 → R2 → D9 → unpack) checked literally with realistic size order;
- the final halting regime: 170 literal runs in the real residue classes, all halting with an exact ones formula
  (section 4). It is not proved.

The originating agent retracted the claim after my first message, and its revised report agrees with this chain
(section 6).

## 1. Notation and tools

**B-form** `[t1 .. tn | A]` = tape 0^∞ D(t1) … D(tn) D0 D(A) G> 0^∞, with D(m) = (10)^m 1.
- The list is written farthest token first. t_n is the first digit, and A is the accumulator.
- A standard digit d is D(3d+1), so D1 = zero. In Ligocki's units, a = (A−1)/3.
- This is exactly Ligocki's B(a; d1..dn) for the record, and R1/R2 below are his rules:
  - B(a; b+1, …) → B(2a+3; b, …);
  - B(a; [0]^k, 0, n+1, …) → B(1; [0]^k, a+1, n, …).
- Clearing (record, closed form): B(a; [0]^k, n, …) → B(g_k^n(a); [0]^k, 0, …), with g_k(x) = 2↑^k(x+3) − 3. Here
  k is the number of zeros nearer than the digit.
- Map to the c35 agent's r-token: A = 2r + 2. Map to the record's Kc counter b: A = 6b + 4.

**Tools.**
- `sim.exe`: literal simulator. It can report events (state, symbol, optionally at the tape edge), stop at the next
  B-form, and run as a stdin server.
- `fw.py`: tokenizer, B-form parser, server wrapper.
- `rules.py`: parametric rules with random literal checks.
- `hs.py`, `esim2.py`: hybrid followers (discovery only).
- `chain.py`: the real run composed from the checked rules.
- `realshape.py`, `seg5.py`, `seg5b.py`: literal checks in the real classes.
- `grid_ex*.py`, `sweepmap.py`, `rounds.py`: the exhausted-transit regime.
- `res.py`: tower residues.
- All runs at Idle priority, at most 3 processes.

## 2. Rules (each checked against the literal machine, next B-form)

| rule | statement | random checks |
|---|---|---|
| R1 | [L, t \| A] → [L, t−3 \| 2A+8], any t ≥ 3, any A | 230, 0 mismatch |
| R2 | [L, t, 1^k \| A] → [L, t−3, A+3, 1^(k−1) \| 4], any t ≥ 3, any A | 230, 0 |
| H (record's halt preparation) | [1^k \| A] → [2, 1^(2A+4), 0, 1^(k−1) \| 6], A ≡ 1 (3) | 230, 0 |
| TL (transfer) | [Q, 1^m, 0, 1^z \| 6] → [Q', 1^(m−3), 0, 1^(z+2) \| 6], Q = [2] → [9], Q = [6^j, 9] → [6^(j+1), 9] | 230, 0 |
| ED0 (D0-blocked borrow, unpack) | [P, Y, T, 0, 1^w \| A] → [P, Y−4, 2, 0, V, 1^(w+T−2) \| 4], V = A+1−(T−5)/2, T ≡ 1 (4), **valid iff V ≥ 2** | 223 + 200 (corrected generator), 0 (+7 early cases at V = 1, outside the precondition) |
| S1 | [6^N, 2, 2, 0, 2, 1^z \| A] → [6^(N−1), 3, A+6, 1, 1, 0, 1^z \| 6] | 230, 0 |
| S2 | [P, 3, X, 1, 1, 0, 1^z \| 6] → [P, 3, X−3, 8, 1^(z+2) \| 6] | 230, 0 |
| S4 | [P, 3, Y, 2, 0, 2, 1^v \| A] → [P, 3, Y−4, A+6, 1, 0, 1^v \| 6] | 230, 0 |
| S5 | [P, 3, Y, X, 1, 0, 1^v \| 6] → [P, 3, Y, X−2, 7, 1^(v+1) \| 4] | 230, 0 |
| S6 | [P, 3, Y, 2, 1^u \| A] → [P, 3, Y−3, A+4, 1^u \| 6] | 230, 0 |

**The ED0 boundary was scanned directly** (`edb.py`, T = 9..49, V = −3..4):
- the rule holds for every V ≥ 2;
- V ≤ 1 with A even: HALT;
- V ≤ 1 with A odd: a different B-form.

**Clearing (CLR).** With only standard tokens and A ≡ 1 (3), R1/R2 alone run.
- A token x ≥ 3 at depth ≥ 1 is consumed to x mod 3: D1 if x ≡ 1, D0 or D2 otherwise. The accumulator becomes the
  clearing output.
- After the first borrow, every deposit is standard.
- Nonstandard sources (D5, D8, D9, D(A+1), D(A+4)) are covered by the R2 check.

## 3. The real run (composed by `chain.py`, checked by `realshape.py`)

| # | configuration | how |
|---|---|---|
| 0 | [1^36 \| 6B+4] = B(2B+1; [0]^36), the record's first exhaustion | record (Coq); template K(0^n;0;b) → [1^(n+1) \| 6b+4]: 84/84; from blank, [D7 D1^35 \| 4] at step 6413 |
| 1 | [2, 1^(12B+12), 0, 1^35 \| 6] | H |
| 2 | [6^(4B+3), 9, 0, 1^(8B+43) \| 6] | TL × (4B+4) |
| 3 | [6^(4B+2), 2, 2, 0, 5, 1^(8B+50) \| 4] | ED0 (T = 9, V = 5) |
| 4 | [6^(4B+2), 2, 2, 0, 2, 4^(8B+49), 7 \| 4] | R2 chain (rebuild) |
| 5 | [6^(4B+2), 2, 2, 0, 2, 1^(8B+50) \| A1] | first full cycle (CLR), deepest digit at depth 8B+49 |
| 6 | [6^(4B+1), 3, A1+3, 8, 1^(8B+52) \| 6] | S1, S2 |
| 7 | [6^(4B+1), 3, A1+3, 5, 0, 1^(8B+51) \| A2] | R2 (deposit 9), CLR(9): 3 units at depth 8B+51 |
| 8 | [6^(4B+1), 3, A1−1, 2, 0, A2+1, 1^(8B+54) \| 4] | ED0 (T = 5, V = A2+1) |
| 9 | [.., A1−1, 2, 0, 2, 1^(8B+54) \| A'] | CLR(A2+1 ≡ 2 → D2): a2 units at depth 8B+54 |
| 10 | [.., A1−5, A'+4, 7, 1^(8B+55) \| 4] | S4, S5 |
| 11 | [.., A1−5, 2, 1^(8B+56) \| A''] | CLR(7): 2 units at depth 8B+55; CLR(A'+4 ≡ 2): a'+1 units at depth 8B+56 |
| 12 | [.., A1−8, A''+4, 1^(8B+56) \| 6] | S6 |
| 13 | **[6^(4B+1), 3, A1−8, A''+1, 0, 1^(8B+55) \| A''']** | R2 (deposit 9), CLR(9): 3 units at depth 8B+55, starting from A = 4 |
| 14 | HALT (I reads 0) | ED0 with V = A'''+1 − (A''−4)/2 ≪ 0: the exhausted regime, section 4 |

**Literal checks in the real shape** (`realshape.py`, B ≡ 6 (120) and B = 0..3, deep values in the real class mod 120):
- stages 0→4 run literally for B ∈ {0, 1, 2, 3, 6, 126}, including the whole TL loop (508 iterations at B = 126);
- stages 5→13 run segment by segment from constructed configurations;
- 2,088 rule applications, 0 mismatches.

**Which accumulators are deep.** A1, A2, A', A'' and A''' are all outputs of clearings whose last crossing is at
depth ≥ 8B+49. Their residues are therefore the universal tower residues of section 5. The small values (4, 6, 5, 8,
9, 7) are resets and constants.

**Literal order check with realistic sizes** (`order.py`).
- Start from the S6 input [6^n, 3, C, 2, 1 | A''] with A'' ∈ {5200, 11800} (≡ A_deep mod 6600), n ∈ {1, 3},
  C ∈ {152, 5192}.
- The run goes, fully literally:
  - [.., C−3, A''+4, 1 | 6];
  - R2: [.., A''+1, 9 | 4];
  - D9 → D6 → D3 → D0 with A = 16, 40, 88;
  - unpack of D(A''+1) with transit 89;
  - HALT at I0, with C untouched (steps 185,885 and 258,485).
- With one zero the D9 clearing is a depth-0 R1-run, so A''' = 88 here, not a deep value. That is why the real-class
  halting is checked separately from constructed configurations 13 (section 4).

**Why step 14 is not the claimed period step.**
- The token being unpacked is D(A''+1), made at stage 12 from A''.
- The transit is A'''+1, made at stage 13 by clearing a D9 (three units) from a reset (A = 4).
- In Ligocki units:
  - a''' = g_{8B+55}^3(1);
  - a'' = g_{8B+56}^{a'+1}(g_{8B+55}^2(1)), with a' itself a huge clearing output.
- So A'' ≫ A''' and V ≪ 0, whereas the rule needs V ≥ 2.
- The claim's step (2), "unpacking D(2r+3) with r = CURRENT accumulator", silently set the token size equal to the
  current accumulator. Its constructed period starts and end-game grids were built that way, so they test
  configurations the real run never reaches.

## 4. The exhausted-transit regime (step 14)

**How it unfolds** (`casc*.py`, `sweep*.py`, `rounds.py`).
- X = D(T) is unpacked into about T/2 "(D1 D0)" pairs.
- Each absorption takes two pairs: the transit drops by 2 and the zero block grows by 4.
- With A even, the transit is used up after A/2 absorptions, with zero block W1 = w + 4 + 2A.
- A sweep then rewrites the zero block. Its result depends only on W1 mod 5 (`sweepmap.py`, W = 9..89):

  | W1 mod 5 | after the sweep |
  |---|---|
  | 1, 3 | HALT |
  | 0 | transit 1 |
  | 4 | transit 2 |
  | 2 | transit t' = (3W1+14)/5, zero block t' − 2 |

**Real class.** W1 = 8B + 59 + 2A''' ≡ 7 (mod 10), since B ≡ 6 (10) and A''' ≡ 0 (mod 10).
- So t' is odd. It is used up as well, and the run halts at I0 with the fixed 20-token right end
  `D1 D0 z2 D0^2 z2 D0^4 z2 D0 z2 D0^3 z2 D0 z2 D1`.
- The prefix [6^(4B+1), 3, A1−8] stays untouched, and so do all but about A''' + t' of the ≈ A''/2 pairs.
- Substituting the real values into the formula below gives σ_ones = 3/2·A'' + A1 + 3/5·A''' + (212B+563)/5.
- This W1 ≡ 7 (10) route was seen for 20 values W1 = 17..207 (`rounds.py`).

**Real-class literal runs** of configuration 13.
- Deep values ≡ A_deep (mod 120), B ≡ 6 (120), T ≫ A:
  - `grid_real.py`: 72 runs;
  - `onesfit.py`: 24 random runs;
  - `seg5.py`: 12 runs.
- Mod 6600 (≡ A_deep mod 8, 3, 11 and 25), `seg5b.py`: B = 6, A1 = A''' = 5200, A'' = 223000 halts at step
  701,394,920 with 343,187 ones.
- Fully mod-6600 real class (B = 6366 ≡ B, A''' = 5200 ≡ A_deep, A1 = 11800, A'' = 269200; tape about 10^6 cells):
  halts at step 18,627,354,512 with 688,751 ones.
- **Result:** every run HALTS at I0, with the same tail and the prefix intact. The ones count fits exactly, with 0
  misfits over 108 + 2 runs.
- **No-residue-escape grid** (`noesc.py`, 60 runs): B = 6 + 120j (all classes mod 7), A''' = 40 + 120k (k = 0..29), A1
  and T random in the real class mod 120, with T only about 6A''' + 2w + 1000. All 60 HALT, with the same tail, the
  prefix intact and the formula exact. So no residue beyond mod 120 changes the route or the count.
- **Formula over all 170 real-class runs:**

      ones = 7n + Y + 3T/2 + 9w/5 + 3A/5 + 131/10    (n = 4B+1, Y = A1−8, T = A''+1, w = 8B+55, A = A''')

- **Wider evidence:** 300 more even-A cases outside the real class (A = 2..3000, w = 1..302) also all halt.
- **What is not proved:**
  - that the W1-mod-5 sweep and the round-2 route stay uniform for astronomically large W1 and A;
  - that no deeper residue (beyond mod 10) changes the route.
  - The tested W1 range goes up to about 6·10^4, through all mod-120 classes compatible with the real ones, plus two
    mod-6600 classes.

## 5. Residues (`res.py`)

**Method.** Tw(1) = 0 and Tw(m) = 2^(Tw(φ(m)) + φ(m)) mod m.
- I checked this against 2↑↑5 and 2↑↑6 for m ∈ {7, 11, 25, 40, 121, 1000}.
- Deep output: a ≡ Tw(m) − 3, so A = 3a + 1.
- Record: B = (Tw(2m) − 4)/2 (mod m).

**Results.**
- B ≡ 16537583495166 (mod 18101949465600), the same as bb8-ab's value: 6 (8), 8 (11), 1 (5), 0 (3), 16 (25).
- A_deep ≡ 44919652574200 (mod 54305848396800), which is 6·B + 4 against bb8-ab's universal R = 3B. So A_deep ≡ 0 (8),
  1 (3), 8 (11), 0 (25).
- Under the c35 agent's map A = 2r + 2 this gives r ≡ 3 (mod 11) and r odd, as claimed. That class is irrelevant,
  because the counter end-game never happens.

**Which free parameters matter.**
- N (the number of D6) and Y = C do not matter: they are never touched.
- Z (my w) matters only through W1 mod 10.
- The accumulators matter through their parity, their residues mod 3, 4 and 5, and the size order A'' ≫ A'''.

## 5b. Size and ranking (paper level)

**Arrow facts used.**
- Record clearing: g_k(x) + 3 = 2↑^k(x+3), so g_k^n(x) + 3 = (2↑^k)^n(x+3).
- (2↑^k)^n(y) ≥ (2↑^k)^n(2) = 2↑^(k+1)(n+1) for y ≥ 2.
- 2↑^(k+1)(y) − 1 ≥ 2↑^k(y).

**M3, lower bound.** From the depths in section 3:
- a2 + 3 ≥ 2↑^(8B+52)(4);
- a' + 3 ≥ 2↑^(8B+55)(a2+1);
- a'' + 3 ≥ 2↑^(8B+57)(a'+2).

Hence

    σ_M3 > 3/2·A'' > a'' + 3 ≥ 2↑^(8B+57)(2↑^(8B+54)(2↑^(8B+52) 3)) > 2↑^(8B+56) 4,   8B + 56 = 4·(2↑^37 3) + 40.

In FGH terms this is one f_ω-scale application whose index is ≈ 4·(2↑^37 3), roughly f_ω(f_38(3)). It is not
f_(ω+1).

**0LA (9 states, padded to 10; halt_redirect).** k = (24B+186)/5 ≈ 2.4·(2↑^37 3).
- Lower bound (bb8-ab): σ > 2↑^(k+2)(2↑^(k+1) 4).
- Upper bound (mine, crude; from the record's closed form 2V_j(x)+4 = 2↑^(j+1)(2x+4) and the chain's depths ≤ k+2):
  - c1, c2 < 2↑^(k+3) 3;
  - 2b1'+4 ≤ 2↑^(k+3) 5;
  - 2b2'+4 ≤ 2↑^(k+2)(2↑^(k+3) 6) = 2↑^(k+3) 7;
  - so σ_0LA ≤ 3·2↑^(k+3) 7 + O(B) < 2↑^(k+4) 4.
- Since 8B + 56 − (k+4) = (16B + 74)/5 ≈ 3.2B:

      σ_M3 > 2↑^(8B+56) 4 ≥ 2↑^(k+5) 4 > 2↑^(k+4) 4 > σ_0LA.

**bb8-ab's three-cycle sibling `..._1LC1RH_0LH0RF_---0LA` (padded).**
- Its third cycle clears [D(2R2−18), D0, D4^(m+40), …] at depth ≤ m+42 ≈ k+43.
- So σ_sib = 2R2 + 13/5·R3 + O(B) < 2↑^(k+47) 4 (same crude method).
- 8B + 56 − (k+47) = (16B − 141)/5 ≈ 3.2B, so M3 > sibling.

**0LJ0LC.** σ = 2·(2↑^L 5) + 2L − 2 < 2↑^L 6, with L = 4·(2↑^27 3) + 17 ≪ 8B.

    σ_M3 > 2↑^(L+2) 3 = 2↑^L(2↑^L 4) > 2↑^L 6.

**BB(10) champion.** Below 2↑^(N')(2N') with N' < 2↑^25 49 (score_comparison.md §6), so it is far below.

**Caveats.**
- The upper bounds for 0LA and the sibling are crude paper estimates. The margin is about 3.2B arrows, so the
  constants do not matter.
- Each ranking step assumes the other machine's stage chain. M3's own chain is strong evidence (sections 2–4).

## 6. Comparison with inv-bb10-c35-rebuild (read after the above)

**Stage-name map** (theirs → mine):

| theirs | mine |
|---|---|
| stage 0 | H, TL, ED0(T=9) |
| jump 0 | rebuild + first full cycle (A1) |
| stage 1 | S1, S2 |
| stage-1 jump | R2 + the first two units of CLR(9) (their R0) |
| period-1 S1 | the third unit of CLR(9) (their R1 = my A2) |
| period-1 S2 | ED0(T=5) |
| its jump | CLR(A2+1) → A' (their R2) |
| S3 + jump | S4, S5, CLR(7), CLR(A'+4) → A'' (their R3) |
| S4 + jump | S6, R2, two units of CLR(9) (their R4) |
| period-2 S1 | the third unit → A''' (their R5) |
| period-2 S2 | my configuration 13 → HALT |

- Their "S2 of period 2, after 7 jumps" is therefore my "second unpack, at the end of the first period".
- Their y = 2R+4−(x−3)/2 is my V, and their x2 = 2R3 + 3 is my T = A''+1.

**Agreements.**
- Revised verdict: one period, then a halt at period 2's S2 (my step 14), ω-level 1.
- Their S1–S4 table maps onto my S1 + R2 + CLR(9), ED0, S4 + S5 and S6 + R2 + CLR(9).
- Their sizes R0..R5 ↔ my A2, A', A'' and A''': their x2 = 2R3 + 3 is my T = A'' + 1, and their y is my V.
- Stage 0/1 counts (4b+2 D6, 8b+49 zeros) and C0 = 2r1 + 5 (my A1 + 3) agree.
- σ ≈ 3·R3 agrees with my 3/2·A''.
- Residues agree.

**Disagreements and additions.**
1. The original claim (periods with C −= 11, refill, second counter, f_(ω+1)) is wrong. The cause is the equal-size
   representatives: `ktrace.py` / `endgame.py` construct [.., C, D(2r+3), D3, 0^Z | r] with the token matched to the
   current accumulator. They now retract this too.
2. Their `m3unpack.py` real-class S2 runs used Z ∈ {3, 10, 25}, which is not the real class. The exhausted regime's
   route depends on W1 mod 5, so those runs reach the halt by other routes. My real-class runs (section 4) close
   this gap at the same evidence level, and add the exact ones formula.
3. "y ≤ −1 halts" is right for their family, where A = 2r + 2 is always even. For general B-forms, odd A with V ≤ 1
   does not halt at that point.

## 7. Open points

- **Coq**, for:
  - the parametric rules of section 2;
  - the exhausted-transit regime with W1 ≡ 7 (mod 10).

  The rest is the record's R1/R2 and its clearing lemma.
- **The size ranking (section 5b) is paper level.** The upper bounds for 0LA and the sibling are crude, and the
  margin is about 3.2B arrows. For a Coq comparison, M3's lower bound needs only "the run follows the chain to
  configuration 13" plus the D(A''+1) token's ones. Even halting anywhere after configuration 12 already gives
  σ > 3/2·A''.
- **The exhausted-transit regime for astronomically large W1 and A.** It is uniform over all 170 real-class runs
  (W1 up to about 6·10^4), but not proved.

## 8. Reproduction (in `bb10_fw1_verify/`)

**Build.** `g++ -O2 -static -o sim.exe sim.cpp` (MSYS2 ucrt64).

**Commands.**
- `python rules.py 200 7` (rule checks); `python rules.py 200 11 ED0` (ED0 with V ≥ 2);
- `python edb.py` (ED0 boundary);
- `python r0.py`; `python startup.py`;
- `python chain.py 1` (real chain);
- `python realshape.py 120`;
- `python grid_real.py OUT 3`; `python onesfit.py 24`;
- `python seg5.py 120 3 0,1,0,40 ...`; `python seg5b.py 6,5200,5200,223000`;
- `python order.py 5200,11800` (literal S6 → R2 → D9 → unpack → halt); `python noesc.py tmp/noesc.txt 2 60`;
- `python sweepmap.py 9 90`; `python rounds.py 2,9,1601 ...`;
- `python grid_ex.py ...` / `grid_ex2.py ...` (even- and odd-A grids);
- `python res.py`.

**Logs** are in `tmp/`:
- `rules200.txt`, `realshape120.txt`;
- `greal1.txt`, `onesfit.txt`, `seg5_120.txt`, `seg5b.txt`, `order.txt`, `noesc.txt`;
- `sweepmap1.txt`, `rounds1.txt`, `rounds2.txt`;
- `gex1.txt`, `gex2.txt`, `gex3.txt`, `gx2a.txt`.
