# Score comparison: the 9-state 0LA candidate vs our BB(9) record and the BB(10) champion

Opus analyst, 2026-10-07. Paper-level analysis (no new Coq). Candidate (9 states, I0 undefined):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA        (FINDING_9state_0LA.md)

Its 10-state padding adds a row J = `------` that is never reached; the run and the score are unchanged.

Notation: `2^(n) x` = 2 with n Knuth arrows applied to x (`arrow n 2 x` in the Coq files). Facts used without comment:
2^(n) x is increasing in x (x >= 1) and nondecreasing in n (x >= 2); 2^(n) 2 = 4; 2^(n+1)(x+1) = 2^(n)(2^(n+1) x), hence
2^(n+1) 3 = 2^(n) 4 and (2^(n))^m (2^(n+1) y) = 2^(n+1)(y+m) (Coq `A_iter`); 2^(n) 4 >= 2^(n+3) > 2n for n >= 1.

## Verdicts

| comparison | inequality | confidence |
| --- | --- | --- |
| candidate vs our BB(9) record | sigma_cand > 2^(k+3) 3 >= 2^(n9+2) 3 = 2^(n9)(2^(n9) 4) > sigma_9, with n9 = 6T-33, T = 2^(13) 3 | as high as the stage chain |
| padded candidate vs BB(10) champion | sigma_cand > 2^(k+3) 3 >= 2^(N+2) 3 = 2^(N)(2^(N) 4) > 2^(N)(2N) > sigma_10, with N = 3*floor(b1/4)+6 <= 2^(27) 49 | as high as the stage chain |
| peer BB(10) candidate vs BB(10) champion (section 6) | sigma_peer > 2^(L) 5 >= 2^(N'+2) 3 = 2^(N')(2^(N') 4) > 2^(N')(2N') >= sigma_10, with N' = 3*floor(b1/4)+4 < 2^(25) 49 | as high as the peer's rules (literal checks) |
| padded candidate vs peer BB(10) candidate `..._0LJ0LC_..._---1LC` | sigma_cand > 2^(k+3) 3 >= 2^(L+2) 3 = 2^(L)(2^(L) 4) > 2^(L) 6 > sigma_peer, with L = 4 * 2^(27) 3 + 17 | as high as the stage chain (section 5) |

Here k = (24B+186)/5 > 4B and 2B+4 = 2^(37) 3. Both comparisons are clear-cut once the candidate halts as the stage
chain says. The candidate's arrow count is about 2.4 * 2^(37) 3; the BB(10) champion's is below 2^(27) 49; our BB(9)
record's is about 6 * 2^(13) 3. The BB(10)-side upper bound is essentially machine-checked (section 3). The only real
uncertainty is the candidate's own stage chain (section 4).

## 1. Lower bound for the candidate

### 1a. The process (BB(8) record rules)
Tokens D(m) = (10)^m 1; digit d = D(3d+1); accumulator token D(3b). The rules R1-R3 (FINDING) say, in values:
- R1: a unit in the a-slot (depth 0) maps the accumulator b -> 2b+2.
- R2/R3: a unit borrowed at depth d >= 1 (zeros above it) refills depth d-1 with the digit 2b+2 and resets b to 0.

Let V be the BB(8) record's clearing functions (BB8_champ35_bound.v, called `U` there):

    V_0(x) = 2^(2x+3) - 2,   V_(j+1)(x) = V_j^(2x+2)(0),   2 V_j(x) + 4 = 2^(j+1)(2x+4)   (Coq U_closed, BB8_champ35_exact.v)

A unit at depth d maps the accumulator b to V_(d-1)(b). For d = 1 it is (b -> 2b+2)^(2b+2)(0) = 2^(2b+3) - 2 = V_0(b).
For depth d+1 it places the digit 2b+2 at depth d, cleared from 0, i.e. V_(d-1)^(2b+2)(0) = V_d(b). So a digit v at
depth d, reached with accumulator c, leaves V_(d-1)^v(c) (the record's CH/CDP lemma family). Every V_j is increasing
and V_j(y) >= y.

### 1b. The two clearings (depths read off the stage chain)
Configurations are written deepest token first; the a-slot is depth 0, the token left of it depth 1, and so on.

**Jump 1.** List `[D9^x, D8, D6, D4^k, D1 | D37 | D18]`, k = (24B+186)/5: ones at depths 2..k+1, D6 at depth k+2.
The run ends at `[.., D8, D3, D1^(k+1) | D1 | D(R1)]`. So the last event is the single borrow D6 -> D3 at depth k+2,
made with depths 1..k+1 all zero and some accumulator c1 >= 0. With b1' = R1/3:

    b1' = V_(k+1)(c1) >= V_(k+1)(0),        2 b1' + 4 >= 2^(k+2) 4.                                    (1)

**Stage 1** turns this into `[.., D8, D0, D(2R1+4), D4^(k-1), D1 | D37 | D18]`. The token D(2R1+4) = D(6b1'+4) is the
digit v = 2b1'+1 at depth k+1 (a-slot 0, D1 at 1, D4^(k-1) at 2..k).

**Jump 2** ends at `[.., D8, D0, D1^(k+1) | D1 | D(R2)]`, so the digit v is used up completely and the borrow stops at
D0. With b2' = R2/3 and c2 >= 0 the accumulator when the digit's first unit is borrowed:

    b2' = V_k^(2b1'+1)(c2) >= V_k^(2b1')(0) = V_(k+1)(b1' - 1),
    2 b2' + 4 >= 2^(k+2)(2b1' + 2) >= 2^(k+2)(2^(k+2) 4 - 2) >= 2^(k+2)(2^(k+1) 4).                     (2)

**Stage 2** halts in I reading 0 with ones = 2 R2 + (744B+2121)/25 = 6 b2' + (744B+2121)/25. Add 1 if the missing
halting transition is filled with a 1-writing halt, the usual convention. Since b2' >= 2, 6 b2' > 2 b2' + 4, and

    sigma_cand > 2^(k+2)(2^(k+1) 4) > 2^(k+2) 4 = 2^(k+3) 3,      k = (24B+186)/5 > 4B = 2 * 2^(37) 3 - 8.     (3)

In the V functions: sigma_cand > 6 V_(k+1)(V_(k+1)(0) - 1).

Heuristic FGH reading: about f_(k+3)(f_(k+2)(..)). That is one f_omega-scale application with index ~4.8B ~ 2.4 * 2^(37) 3,
roughly f_omega(f_38(3)). The second clearing does NOT add a second f_omega level: its list has the same depth k+1, and
only its deepest digit (2b1'+1) is huge.

### 1c. Which steps rely on the stage chain (not proved)
- **Stage 0** (the rebuild after E0 -> I -> 0LA) gives the Jump 1 list and k = (24B+186)/5. It is literal for
  b = 1..196 (40 values) and extrapolated to the real B.
- **R1-R3 themselves.** The BB(8) record's R1-R3 never read E0 (the record reads E0 only at exhaustion), so they carry
  over. But here they act on lists with non-digit tokens (D9, D8, D6, D3, D0). The borrow from D6 (residue 0) and the
  stops at D3 and D0 are literal-checked only (about 300 random configurations).
- **Stage 1 and Stage 2.** Stage 1 (D3 -> D0, the new digit 2R1+4) and Stage 2 (halting for all m' outside {0, 7}, the
  ones formula) are literal grids with m <= 67 and r <= 90. They are extrapolated to m' ~ 4.8B and r ~ 2^(k+2)(..).
  The halt also needs the real m' to avoid {0, 7}; it does (m' = 4 mod 7, from the residues of B).
- **What the size argument needs.** (1) and (2) use only the depth of the deepest borrowed token in each clearing and
  the fact that each clearing finishes; they do not use the exact ones formula. Even a halt right after Jump 1 with
  the accumulator R1 on the tape would leave at least about 2^(k+2) 4 ones, which still beats both bars below. The
  real risk is that the machine does not halt, or leaves the family, for the actual huge parameters. The size is not
  the risk.

## 2. Comparison with our BB(9) record

Machine-checked (BB9_record_bound.v, `score_exact` / `score_closed`), with T = 2^(13) 3:

    sigma_9 = 3 * 2^(6T-33) 8 + (54T + 26)/5.

Let n9 = 6T - 33. Then 2^(n9) 9 = 2^(n9-1)(2^(n9) 8) >= 2^(2^(n9) 8) > 3 * 2^(n9) 8 + (54T+26)/5, so
sigma_9 < 2^(n9) 9. The candidate's arrow count k+3 > 2 * 2^(37) 3 is far above n9 + 2, since 2^(37) 3 >> 6 * 2^(13) 3.
By (3):

    sigma_cand > 2^(k+3) 3 >= 2^(n9+2) 3 = 2^(n9+1) 4 = 2^(n9)(2^(n9) 4) >= 2^(n9)(16) > 2^(n9) 9 > sigma_9.

**Verdict:** the candidate beats our BB(9) record. In FGH terms the margin is "index about 2^(37) 3 vs about 2^(13) 3"
in the single f_omega-scale application. It is conditional only on the candidate's stage chain.

## 3. Upper bound on the BB(10) champion's actual score

Machine `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ`. Everything structural is proved in Coq
(../bb10_champion_1RB1RA_0LF0LJ.md; proofs/BB10_champion_1RB1RA.v, BB10_champion_bound.v):
- R1-R3 are the BB(9) champion's.
- R4 rebuilds b = 4m -> [1,(0,0,3)^m,0,0,2] (and b = 4m+2 -> [3,(0,0,3)^m,0,0,2]); odd b halts.
- The run rebuilds twice and halts at the third R4 (b2 odd, Coq `b2_odd`).

No literal simulation is needed, because `score_exact` gives the exact score:

    sigma_10 = b2 + 4,   b1 = Tv 7 1 7,   m1 = floor(b1/4),   b2 = Tv m1 1 7,
    Tv m 1 B = U_(3m+3)(U_(3m+3)(Tpre m 1 B)),   Tpre m 1 B = U_(3m)^3( ... U_6^3(U_3^3(B)) ... ).

U is the BB(9) champion's: U_0 x = 3x+7, U_(j+1) x = U_j^(x-2j)(X_j), X_(j+1) = U_j(U_j(X_j)). So Tv m 1 7 is 3m+2
applications of U_d with d <= 3m+3, starting at 7. Every intermediate value is >= 7 (U_j(y) >= y, Coq `Uc_ge`).

Machine-checked bound on U (proofs/BB9_record_vs_champion.v, same U):

    Uc_le   : U_j(x) <= 2^(j+2)(2x+4),   X_j <= 2^(j+3) 4
    Uc_le_K : j + 2 <= K, 3 <= y  ->  U_j(y) <= A(A(y)),   A = 2^(K)

Take K = 3m+5, which is >= d+2 for every depth used. A is increasing, and 7 <= 2^(K+1) 3 = 2^(K) 4, so the 3m+2
applications give at most A^(6m+4)(7) <= A^(6m+4)(2^(K+1) 3) = 2^(K+1)(6m+7) (Coq `A_iter`). Hence

    Tv m 1 7 <= 2^(3m+6)(6m+7)   for all m.                                                                 (4)

This is the BB(10) analogue of the Coq lemma `second_le` (for the BB(9) champion: second b <= 2^(b+4)(b+6)). A Coq
proof is a direct copy of `Pv_le` / `second_le` with Tpre in place of Pv.

- **b1** (m = 7): b1 <= 2^(27) 49. The Coq lower bound is b1 >= 2^25 f_25(f_25(2)), about 2^(25) 4.
- **sigma_10** = b2 + 4 <= 2^(N)(6m1+7) + 4 <= 2^(N)(6m1+8) < 2^(N)(2N), with N = 3 m1 + 6 <= b1 <= 2^(27) 49.

So the champion lies between the Coq lower bound f_omega(3m1+3) and 2^(3m1+6)(6m1+12). That is one f_omega-scale
application whose index, about 3 b1/4, is itself about f_25(f_25(..)) <= 2^(27) 49. This is the listed "f_omega^2(25)":
the second f_omega is the index, not a deeper hierarchy level.

**Comparison with the padded candidate.** 2^(37) 3 >= 2^(28) 4 = 2^(27)(2^(27) 4) >= 2^(27)(65536). So
k > 2 * 2^(37) 3 - 8 > 2^(27) 49 + 4 >= N + 4, and by (3)

    sigma_cand > 2^(k+3) 3 >= 2^(N+2) 3 = 2^(N+1) 4 = 2^(N)(2^(N) 4) > 2^(N)(2N) > sigma_10.

**Verdict:** the padded candidate beats the BB(10) champion's ACTUAL score, not just its listed f_omega^2(25).
- In arrow counts it is not close: the candidate's f_omega-scale index is about 2.4 * 2^(37) 3, the champion's is below
  2^(27) 49.
- In FGH language both are "f_omega(f_c(small))". The candidate wins on the inner level, about 37-38 vs 25-27, not by an
  extra f_omega application.
- The inequality needs neither the candidate's second clearing nor the exact ones formula: the first clearing's
  accumulator, about 2^(k+2) 4, already exceeds 2^(N)(2N).

## 4. Weakest link and what would settle it

1. **The candidate's stage chain is the weakest link** (section 1c): Stage 0 for the real B, the two abstract
   clearings on lists containing the non-digit tokens D6/D3/D0, and above all Stage 2. Stage 2 must halt for the real,
   enormous m' and r, not just for the grid values m <= 67, r <= 90. A Coq proof of `halts` for the candidate (the
   other agent's job) settles both comparisons, because the size inequalities need nothing beyond "the run follows
   the chain and halts".
2. **BB(10) side: low risk.** The exact score is Coq and the U bound is Coq (`Uc_le_K`). Only the composition (4) and
   the final arrow arithmetic are paper-level, a few lines in the style of BB9_record_vs_champion.v.
3. **Score convention.** The candidate halts on an undefined I0 reading 0, so its standard score is the tape count + 1.
   This is irrelevant at these sizes.
4. Step counts are not compared here.

## 5. Comparison with the peer BB(10) candidate (added 2026-10-07)

Peer machine (another session, investigations/bb10_lead_0LJ0LC; a c35m14 relative of the BB(8) record):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC
    sigma_peer = 2 * (2^(L) 5) + 2L - 2,   L = 4 * (2^(27) 3) + 17        (formula as reported by the lead)

`2^^L 5` means L arrows applied to 5. Section 6 derives this formula from the peer's rules and re-runs the peer's literal check.

Upper bound: 2^(L) 6 = 2^(L-1)(2^(L) 5) >= 2^(2^(L) 5) > 2 * 2^(L) 5 + 2L, so sigma_peer < 2^(L) 6.

Arrow counts: 2^(37) 3 >= 2^(28) 4 = 2^(27)(2^(27) 4), which is vastly larger than 4 * 2^(27) 3 + 17 = L. Hence k + 3 > 2 * 2^(37) 3 - 5 > L + 2, and by (3)

    sigma_cand > 2^(k+3) 3 >= 2^(L+2) 3 = 2^(L+1) 4 = 2^(L)(2^(L) 4) >= 2^(L)(16) > 2^(L) 6 > sigma_peer.

**Verdict:** if its stage chain holds, the padded 0LA candidate beats the peer candidate.
- Both scores are a single f_omega-scale application. The peer's index is about 4 * 2^(27) 3 (inner level about 28). The 0LA candidate's index is about 2.4 * 2^(37) 3 (inner level about 38).
- So the 0LA machine wins by about ten arrows in the inner number, not by an extra f_omega.
- **Caveat:** the peer's formula is exact if its own analysis is right. The 0LA side is a lower bound that rests on the stage chain (section 1c), so the weakest link is the same as in section 4.

Peer vs the BB(10) champion: decided in section 6 (the peer wins).

## 6. Peer BB(10) candidate vs the BB(10) champion (sharper bound on b1)

### 6a. A sharper bound on the champion's U: j arrows instead of j+2
The Coq bound `Uc_le` (U_j(x) <= 2^(j+2)(2x+4)) loses two arrows, which is too loose here. Sharper:

**Lemma S.** For all j >= 1 and x >= 0: U_j(x) <= 2^(j)(2x+4) and X_j <= 2^(j+1) 4.

Coq-style statements. They use U, X, Tpre, Tv, b1, b2 exactly as defined in proofs/BB10_champion_1RB1RA.v and
`arrow k 2 x` (k arrows) as in proofs/BB9_record_vs_champion.v, where arrow 1 2 x = 2^x:

    Lemma U_arrow_tight : forall j, 1 <= j ->
      (forall x, U j x <= arrow j 2 (2 * x + 4)) /\ X j <= arrow (S j) 2 4.
    Lemma U_le_K_tight : forall j K y, 1 <= j -> j <= K -> 4 <= y ->
      U j y <= arrow K 2 (arrow K 2 y).
    Lemma Tv_le_tight : forall m, Tv m 1 7 <= arrow (3 * m + 4) 2 (6 * m + 7).
    Lemma b1_le_tight : b1 <= arrow 25 2 49.
    Lemma b2_le_tight : b2 + 4 <= arrow (3 * (b1 / 4) + 4) 2 (6 * (b1 / 4) + 8).

`U_arrow_tight` is the one-arrow analogue of `Uc_le`, which has arrow (j+2) and arrow (j+3). `U_le_K_tight` follows from
it with `A_lin` (2y+4 <= 2^y for y >= 4) and `arrow_level_mono`. `Tv_le_tight` holds because Tv m 1 7 is 3m+2 applications of
U_d with 3 <= d <= 3m+3, all on arguments >= 7. With K = 3m+3, 7 <= arrow (K+1) 2 3, and `A_iter`, the bound is
arrow (K+1) 2 (2(3m+2)+3). `b1_le_tight` is the case m = 7, and `b2_le_tight` follows from b2 = Tv (b1/4) 1 7.

Proof by induction on j.
- **Base j = 1.** U_1(x) = U_0^x(7) = (21 * 3^x - 7)/2 <= 16 * 4^x = 2^(2x+4). X_1 = U_0(U_0(7)) = 91 <= 2^(2) 4 = 65536.
- **Step j -> j+1, part 1.** For y >= 4 (j = 1) or y >= 3 (j >= 2) we have 2y+4 <= 2^(j) y (Coq `A_lin` for j >= 2;
  2^y >= 2y+4 for y >= 4). So U_j(y) <= A(A(y)) with A = 2^(j).
- **Step, part 2.** X_j >= 7, and every iterate of U_j from X_j is >= X_j because U_j(y) >= y. By monotonicity of A,
  U_j^n(X_j) <= A^(2n)(X_j) <= A^(2n)(2^(j+1) 4) = 2^(j+1)(2n+4) (`A_iter`).
- **Step, part 3.** With n = x - 2j (truncated) <= x this gives U_(j+1)(x) <= 2^(j+1)(2x+4). For x <= 2j it is just
  X_j <= 2^(j+1) 4.
- **Step, part 4.** X_(j+1) = U_j(U_j(X_j)) <= A^4(2^(j+1) 4) = 2^(j+1) 8 <= 2^(j+1)(2^(j+1) 4) = 2^(j+2) 4.

Numeric sanity: the closed form of U_1 checked for x < 400; U_2(3) ~ 2^148 and U_2(4) are far below 2^(2) 10 and
2^(2) 12. Consequence, used below: for 1 <= d <= K and y >= 4, U_d(y) <= 2^(d)(2^(d) y) <= 2^(K)(2^(K) y).

### 6b. The champion's score, re-bounded
Every U argument in Tv m 1 7 is >= 7.
- **b1** = Tv 7 1 7 consists of 23 applications of U_d with 3 <= d <= 24 (U_3^3, U_6^3, ..., U_21^3, then U_24 twice).
  With K = 24 and 7 <= 2^(25) 3:

      b1 <= (2^(24))^46 (7) <= (2^(24))^46 (2^(25) 3) = 2^(25)(49).

  The Coq lower bound is b1 >= 2^25 f_25(f_25(2)), so b1 really is at this level.
- **b2** = Tv m1 1 7 consists of 3m1+2 applications with d <= 3m1+3 =: D, so b2 <= 2^(D+1)(6m1+7). With
  N' = 3m1+4 = D+1:

      sigma_10 = b2 + 4 <= 2^(N')(6m1+8) = 2^(N')(2N'),   N' = 3*floor(b1/4) + 4 < 2^(25) 49.

  This is sharper than section 3 by two arrows on b1 and by two in the outer count.

### 6c. The peer's score formula, checked
Peer `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC`. Family: list entries (10)^n 1, digit d =
entry 2d+1, accumulator entry 2b+1, head in G at the right end. The rules come from the peer's rules.py and lead_check.py:
- **R1:** the nearest digit loses 1 and b -> b+2.
- **R2/R3:** borrow across zeros; the borrowed entry loses 2 (one unit), the refilled digit is b+2, and b -> 0.
- **Rebuild:** C(0^m | b) -> N(6, 1^(4b+m+6), 1), i.e. a raw entry 6 (three units) behind 4b+m+6 zero digits, b = 0.
- **Halt:** N(0, 1^L, 2b+1) halts with J reading 0 and 2b+2L+5 ones.

Derivation. A unit at depth d (d zeros in front) maps b to F_d(b), with F_0(b) = b+2 and F_(d+1)(b) = F_d^(b+2)(0).
Hence F_d(b) = 2^(d-1)(b+4) - 4 for d >= 1, where 2^(0) is doubling: F_1(b) = 2b+4 and F_2(b) = 2^(b+4) - 4, then by
induction.
- **Start:** C([2,0^26] | 0) at step 3890. Its clearing gives B_p = F_26^2(0) = 2^(25)(2^(25) 4) - 4 = 2^(27) 3 - 4.
- **Rebuild:** m = 27, so L = 4 B_p + 33 = 4 * 2^(27) 3 + 17, as stated.
- **Clearing the 6 at depth L:** b2 = F_L^3(0) = F_(L+1)(1) = 2^(L) 5 - 4.
- **Halt:** ones = 2 b2 + 2L + 5 = 2 * 2^(L) 5 + 2L - 3. Adding 1 under the convention that the undefined halting
  transition writes a 1 gives sigma_peer = 2 * 2^(L) 5 + 2L - 2, exactly the reported formula. Without the +1 it is
  smaller by 1, which does not matter here.

Re-ran `bb10_lead_0LJ0LC/lead_check/lead_check.py` (the lead's independent simulator). TOTAL MISMATCHES: 0.
- C([2,0^26]|0) is reached at step 3890.
- Rule checks: 1,274 R1 and 217 R2/R3 configurations.
- Rebuild: 180 cases, m <= 12, b <= 14.
- Halt: 600 cases, L <= 24, b <= 24.
- The whole end-game for L = 1 halts with 63 ones.

The peer's own verify_rebuild_halt.py sweeps further (m <= 30, b <= 60, b up to 2048 at m = 27). Status of the peer's
formula: derived exactly from rules that are literal-checked, not yet proved in Coq. There is no residue condition in
its chain: the rebuild and the halt apply for every b and L tested.

### 6d. Verdict: the peer beats the BB(10) champion
L = 4 * 2^(27) 3 + 17 > 2^(27) 3 = 2^(26) 4 = 2^(25)(2^(25) 4) >= 2^(25)(65536) > 2^(25)(49) + 2 > N' + 2. Hence

    sigma_peer > 2^(L) 5 >= 2^(N'+2) 5 > 2^(N'+2) 3 = 2^(N'+1) 4 = 2^(N')(2^(N') 4) > 2^(N')(2N') >= sigma_10.

- The peer's f_omega-scale index is L ~ 4 * 2^(26) 4. The champion's is N' < 2^(25) 49. So the peer wins by about one
  arrow level in the index.
- That margin is smaller than the 0LA candidate's (about 37 vs 25 levels), but it is rigorous given the peer's rules.
- Confidence: the BB(10)-champion side is Coq (`score_exact`) plus Lemma S and the composition, both short paper
  proofs. Lemma S is a straightforward Coq target by modifying `Uc_le` in BB9_record_vs_champion.v.
- The peer side rests on its literal-checked rules (start, R1-R3, rebuild, halt), extrapolated to b ~ 2^(27) 3 and
  L ~ 4 * 2^(27) 3.

Ranking, if every stage chain holds: 0LA (padded) > peer > BB(10) champion; and 0LA > our BB(9) record.
