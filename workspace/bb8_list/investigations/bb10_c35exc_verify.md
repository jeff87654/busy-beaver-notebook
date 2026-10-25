# Independent check of the c35m14 exception `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0LD0RH_1RG1LF_0LJ1RI_---0LA`

Verifier: inv-bb10-c35exc-verify, 2026-10-08. Work folder: `investigations/bb10_c35exc_verify/`.
Steps 1-4 were done without reading the originating agent's files. Section 6 compares with them.

## 0. Verdict

**NEVER HALTS (strong evidence, not a proof). It is not a record candidate.**

1. The machine runs the BB(8) record exactly.
2. At the record's halting point it rebuilds a copy of the record inside a frozen outer frame, and that copy also exhausts.
3. The clearing of the inner region then recurses down to its bottom and climbs back. At the 14th of 18 recursion levels it reaches a *linear race* between the current accumulator Y and a level token a:
   - The configuration is `[.., a, 3, 1, 1, 0, 0, Y]`.
   - If Y < 2a+6, the machine enters a right-moving translated cycler.
   - In the real run Y is smaller than a by a whole arrow level, so it enters the cycler.
4. The outer zero block (Z ≈ 3.6·(2↑^37 3) zeros) and the X countdown are never touched. No f_ω-level cycle happens and nothing borrows into P.
5. The outcome depends only on the real inner width (36). It does not depend on any residue of T = 2↑^37 3.

## 1. Notation

- Tokens are `D(n) = 1 (01)^n`. Every tape in the run is `0^inf D(t_0) … D(t_m) G> 0^inf`.
- A **B-form** is a list ending `[…, 0, y]`: a D(0) token, then the accumulator token D(y). The head is in G at the right edge, reading blank.
- The record's family in this notation:
  - Ligocki's `B(a; d_1..d_n)` is `[3d_n+1, …, 3d_1+1, 0, 3a+1]`.
  - Kc snapshots are `[…, 3a+1, 3b+1, 2]` (one round earlier).
- One *event* runs from one B-form right-edge G0 event to the next.

## 2. Step 1: start-up and the record phase

- **The 13-step detour.** In M10, G0 = 0LD is followed by D1 E0 I1 I1 I1 I0 J1 A1 A0 B0 C1 B0. This leaves exactly the tape and state (C, 3 cells left) that the record's G0 = 1LC, C1, B0 leave, provided the 3 cells left of G are `101`.
- **Context histogram (`sim.exe hist=G0`).**
  - In a 3·10^9-step record run, G0 had only two contexts: `101_000 edge` (48,057 times) and `101_101 inner` (52 times).
  - The record's halting phases from B(a;0^k) add only `101_100`.
  - M10's E0 contexts mirror these.
  - So M10 is the record, with dilated steps, until the record's halting E0.
- **Start-up.** M10 reaches the record's B(5;[1]^36) = `[4^36, 0, 16]` at step 49,197 (the record does so at step 47,897).
- **Rules in token-count form.** These hold for **every residue of x mod 3** (x ≥ 3) and every y ≥ 2. They were checked on 400 random literal cases plus about 1,900 inside the rule checks, with 0 mismatches.
  - R1: `[.., x, 0, y] -> [.., x-3, 0, 2y+8]`
  - R2: `[.., x, 1^k, 0, y] -> [.., x-3, y+3, 1^(k-1), 0, 4]`

  For tokens ≡ 1 mod 3 these are the record's Coq-proved rules.
- **Record exhaustion.** It ends at `[1^36, 0, y_f]` with `y_f + 8 = 3·(2↑^37 3)`, so `y_f = 3T − 8`. This is the record's `a_36 + 3 = 2↑^37 3`.

## 3. Step 2: the first new events with the real parameters

**Tower residues.** `tower.py` computes the stable residue of 2↑↑h mod m for large h. The λ-chain of M has depth 11, and T is a 2-tower of astronomical height.

| Quantity | Value |
|---|---|
| T mod 3, 5, 8, 7 | 1, 1, 0, 2 |
| y_f | ≡ 0 mod 5 and ≡ 1 mod 3 |
| bb8-ab's B = (T−4)/2 | 16537583495166 mod 18101949465600 (exact match, all listed sub-residues match) |

**Outer exhaustion** (0^inf to the left). Literal-checked for y = 10…205 (y ≡ 10 mod 15) and k = 1, 2, 3, 5, 36; `repro.py` step 3.

    [1^k, 0, y]  ->  [2, 1^(2y+4), 0, 1^(k-1), 0, 6]          (inside the record's halt phase)
                 ->  [P, 6q+3, 1^(6q), 0, 5, 1^k, 0, 4],     P = 2 1 1 0 2 1 0 1,  q = y/5

- This is the branch for y ≡ 0 mod 5.
- y ≡ 2, 3, 4 mod 5 halt within a few thousand steps.
- y ≡ 1 mod 5 gives a different left part.
- Real values: q = (3T−8)/5, X = 6q+3, Z = 6q.

**Inner record.** R2 on the 5 gives `[.., 0, 2, 7, 1^35, 0, 4]`. That is the record's B(1;[0]^35,2) with the D2 as its left wall. It exhausts with the same y_f and **36 zero tokens**, which is the real inner width.

**Inner exhaustion.** This is rule S2w0, which was verified with ones blocks and across magnitude regimes.

    [P, X, 1^Z, 0, 2, 1^36, 0, y_f]  ->  [P, X-4, 3, 1^Z, y_f+2, 1^36, 0, 6]

## 4. Step 3: the dynamics after the inner exhaustion

### 4.1 Rules

`rules.py` holds the hand-derived special rules. They apply when the leftward scan meets a D0 or D2 token, read the token w to its left, and sometimes the token u beyond that. Examples:

- S0 for w ≥ 4: `[w, 0, 1^k, 0, y] -> [w-4, 3, y+1, 1^(k-1), 0, 4]`
- S2 for w ≥ 3: `[w, 2, 1^k, 0, y] -> [w-3, y+4, 1^k, 0, 6]`
- S0w2, S0w2u0, S0w2u0v0, S0w3, S0w3u0, S0w3u0v2, S0w0, S0j, S0j1w3u0, S2w1, S2w0, S2w2

Verification:

- `check_rules.py`: two random batches of 400 literal configurations, 0 mismatches.
- `regime_hand.py`: 24 rule templates, each run with the big token and the accumulator small (5–30) or large (300–3000) in all combinations. All 288 cases pass, so no hand rule depends on magnitudes.
- `oracle.py` infers any remaining event from literal runs with representatives and an exact affine fit.
- `regime.py` re-ran all 16 inferred shapes across magnitude regimes. All passed. The one apparent failure needed left context and passes with it (`t41.py`).

### 4.2 Symbolic engine

`engine.py` and `num.py` represent each value either as an exact integer or as "huge, known mod M".

- **Modulus.** M = 2^20·3^4·5^2·7^2·11·13·17·19. It is λ-closed with a factor of 3: λ(M) divides M/3. So an R1 iteration count (x−e)/3 fixes 2^v mod M exactly.
- **Cycle jumps.** On each counter, a repeated residue state of the suffix triggers an exact jump; the counter then lands on its exact small remainder.
- **Memoisation.** Results are memoised on the residue state of the suffix.
- **Validation:**
  - 1,582 small cases against brute force with the same rules: 0 mismatches.
  - 77 cases with jumps against residue brute force: 0 mismatches.
  - 157 cases against exact big-integer brute force: 0 mismatches.
  - 50 cases with a small λ-closed modulus (2^5·9·5·7) so that jumps happen, against exact big integers: 101 jumps, 0 mismatches (`t47.py`).

### 4.3 What the inner game does

Running the engine on `[3T−6, 1^36, 0, 6]`, with or without the left context `[P, X−4, 3, 1^k]`, gives the following (`t32`–`t45`).

1. **Top.** R2 gives `[A−3, 9, 1^35, 0, 4]`. The 9 clears in three units against 1^35 and becomes D0. S0 then gives `[A−7, 3, Y1+1, 1^34, 0, 4]`.
2. **Recursion.** Write Q(n) = `[3, D, 1^n, 0, y]` with D ≡ 2 mod 3. Each Q(n) does the following:
   - counts D down to 2;
   - S2 (w=3): `[0, Y'+4, 1^n, 0, 6]`;
   - R2;
   - a 9 is cleared against 1^(n−1);
   - S0b: `[0, Y'−3, Q(n−2)]`.

   The new D depends only on n. So levels 34, 32, …, 0 each leave a pair `0, Y'_n − 3` behind. Y'_n is about 2↑^(n+1) of a number at level n+2.
3. **Bottom climb.** At Q(0) and Q(2) the bottom eats the left-over level tokens one by one, using period-11 loops (S2w0, S0w3, S0j). Each loop exponentiates the accumulator once per period, so eating level n leaves an accumulator of about 2↑↑(Y'_n), which is at most 2↑^(n+1)(z_n+1). The trace shows only these single-loop consumptions at the bottom, with no nested jumps.
4. **The race.** After levels 0–12 are eaten, the next level token h (level 14) is borrowed from by 4. The rule `[h, 0, 3, 0, 0, 0, y] -> [h−4, 3, 1, 1, y+1, 0, 4]` is literal-verified for y ≪ h and y ≫ h. Then R1* gives

       [A', 0, H_34, 0, H_32, ..., 0, H_16, 0, a, 3, 1, 1, 0, 0, Y],   a = h-4,  Y = 12·2^((y+1)/3) - 8.

   This configuration is identical for any residue of the top token (`t50.py`).
5. **Race law** (`t35.py`, `t40.py`, `t43.py`, `repro.py` step 5).
   - From `[.., a, 3, 1, 1, 0, 0, Y]` the machine consumes about Y/2 + 6 of D(a). It never reads left of a.
   - If Y < 2a+6 it then runs a **translated cycler**: a block of 1s grows to the right at about 0.017 cells per step, with a record window that repeats every 118 steps shifted by +2 (`tcycler.py`).
   - If Y ≥ 2a+6 it continues normally.
   - The threshold is exact for a = 12, 15, 18, 24, 30 and was confirmed at a = 300 and 3000.
   - In the real 29-token list:
     - with representatives of comparable size, 10 of 12 samples ran into the cycler, and the 2 exceptions had Y ≥ 2a+6;
     - with the real ordering (Y ≪ a), 4 of 4 did (`t49.py`).
6. **Real magnitudes.** a = Y'_14 − O(1) ≈ 2↑^15 of a number of level 16. Y comes from levels ≤ 12 through tetration-type loops only, so Y is at most about 2↑^13 of a level-14 number. Hence **Y ≪ 2a+6**, the cycler is entered, and the machine never halts.

### 4.4 Answers to the four questions in the task

- **(a) Does the inner width matter?** Yes, decisively. With the same engine:
  - widths 1 and 3–13 finish the inner game;
  - width 2 and even widths ≥ 14 reach the race `[.., 3, 1, 1, 0, 0, Y]`;
  - odd widths ≥ 17 reach another runaway pattern, `[.., 2, 2, 1, 1, 0, Y]`.

  The real width is 36.
- **(b) Were the true residues used?** Yes, all of them (stable tower residues). The decisive event is magnitude-dependent, not residue-dependent, and the result does not change with the residue of T.
- **(c) Do the X countdown and the borrow into P end in J reading 0?** They never happen. Neither X nor the Z outer zeros is ever read after the inner exhaustion.
- **(d) How many f_ω-level cycles happen?** None complete. The only Ackermann-type work is the clearing of the 36-wide inner region, which is a finite number of arrows. Then the run is in an infinite loop.

## 5. Size comparison

Not applicable, because the machine does not halt (strong evidence). The three reference machines are unaffected:

- 0LJ0LC: σ = 2·(2↑^L 5) + 2L − 2.
- bb8-ab's 9-state 0LA, padded.
- The BB(10) champion.

## 6. Step 5: comparison with inv-bb10-open-threads

Sources: `bb10_open_threads.md` §2 and `bb10_open_threads/c35ev.py`.

**Agreements:**

- The configuration at the first outer event is the same.
  - Their `P D(X) D1^Z D0 D2 D1^35 | 0 | R1` is my `[P, X, 1^Z, 0, 2, 1^36, 0, y]`: their 35 zeros plus the a-slot D1 make my 36.
  - X = (36B'+39)/5 and Z = (36B'+24)/5 equal my 6q+3 and 6q.
  - Their first outer event equals my E_in followed by R2.
- B ≡ 16537583495166 mod 18101949465600 is reproduced exactly.
- Their "universal R ≡ 49612750485498 mod 54305848396800" is my post-clearing accumulator y = 3τ−8 under y = 2R+4. It reproduces exactly (`t48.py`).
- The first outer event is r-uniform.
- Runaway behaviour exists (their width-3 real-class runaway); the odd-width pattern above may be the same phenomenon.

**Disagreements and corrections:**

1. **The inner hydra does not die.** Their outer-zero analysis (§2.3–2.5) assumes the inner part finishes and then the Z block is converted. In the real run the inner game enters a translated cycler first, and the Z block is never reached. Their "leaning non-halting" conclusion has the right outcome, but the mechanism is different, and it does not depend on Z's 2-adic and 5-adic digits.
2. **c35ev.py resets every accumulator to a small r.** That keeps residues but destroys magnitudes, while the decisive event compares an accumulator with a level token. So their halting runs (widths 3, 7, 9 at X = 15, Z = 12) and runaway runs could not represent the real branch. They used wrong residue classes and also artificial magnitudes.
3. **Inner width.** Their "real inner width is 35" counts digits without the a-slot. In zero tokens at exhaustion it is 36, which is even. Parity matters: the even branch gives the race, the odd branch gives the `2 2 1 1` runaway.
4. **Proposed next step.** They proposed computing the Z residue recursion as the next step. It is not needed, because the run never gets there.

## 7. Caveats

- All event rules and the race law are verified on samples, not proved:
  - token values up to about 40 for the rule checks;
  - magnitude ratios up to about 600;
  - race tests with a ≤ 3000.

  Extending to astronomically large values assumes the usual uniformity of these linear sweeps.
- The ordering Y ≪ a is a hand argument from the level structure of the recursion. Its input — only tetration-type single loops at the bottom, no nested jumps — is read off the engine trace.
- The engine is exact modulo M and validated against brute force. It is not a proof tool.
- A Coq proof would need: the start-up (the record files can be reused), the detour emulation, the S2w0 and inner-game rules, the recursion, and the race → cycler lemma.

## 8. Files and reproduction (`investigations/bb10_c35exc_verify/`)

**Simulator and rule tools:**

- `sim.cpp` / `sim.exe`: literal simulator with batch mode and snapshot, stop and histogram options; B-form snapshots record the minimum head position. Built with MSYS2 g++ -O2.
- `lib.py`: Idle-priority batch driver and token parser.
- `rules.py`: hand rules.
- `oracle.py`: inferred events.
- `check_rules.py`: literal rule check.
- `regime_hand.py`, `regime.py`: magnitude-regime checks.

**Symbolic engine:**

- `num.py`: exact-or-huge numbers, M.
- `tower.py`: stable tower residues.
- `engine.py`: memoised, cycle-jumping suffix runner.
- `tcycler.py`: translated-cycler check.

**Scripts behind the claims above:**

| Claim | Script |
|---|---|
| Outer exhaustion | `t22.py` |
| Race tests | `t33.py`, `t35.py`, `t40.py`, `t43.py`, `t49.py` |
| Width scan | `t44.py` |
| With the outer context | `t45.py` |
| Engine validation | `t46.py`, `t47.py` |
| Top-token residue independence | `t50.py` |
| Universal residue | `t48.py` |

**`repro.py`** (about 5 minutes; output in `repro.out`) reproduces:

1. the start-up to [4^36,0,16] at step 49,197;
2. the residues;
3. the outer-exhaustion formula (0 mismatches);
4. the engine run ending at the race configuration;
5. the race-law grid.
