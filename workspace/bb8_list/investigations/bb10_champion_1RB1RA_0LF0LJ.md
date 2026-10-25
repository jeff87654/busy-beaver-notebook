# The BB(10) champion `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ` and its TNF subtree

The machine is Racheline's 2024 entry in the wiki "Champions" table. This report gives its analysis, machine-checked
halting and score proofs, and a grader (`r10grade.py`) for its TNF subtree. Scripts are in
`bb10_champion_1RB1RA_0LF0LJ/`; the Coq files are in `../proofs/`.

## 0. Summary

- **The wiki's score is f_ω²(25) = f_ω(f_ω(25)), not f_{ω·2}(25).** The raw wikitext (MediaWiki API, page `Champions`,
  copied to `wiki_champions_excerpt.txt`) reads `<math>> f_\omega^2(25)</math>`. Copied as plain text, the superscript
  flattened into "fω2". The BB(10) bar is therefore two f_ω-scale steps, far below f_{ω+1}(3).
- **Structure.** The machine is the BB(9) champion with a new rebuild.
  - R1-R3 are the BB(9) champion's rules, unchanged: their phases never visit H, I or J.
  - R4, the rule for the used-up list, is new:
    - b odd: halt;
    - b = 4m: rebuild `Kd [1,(0,0,3)^m,0,0,2] 0 0`;
    - b = 4m+2: rebuild `Kd [3,(0,0,3)^m,0,0,2] 0 0`.

  The new state J lets the rebuild pass turn two counter blocks into one digit 3 behind two zero digits. The rebuilt
  list is therefore 3b/4 deep (the BB(9) champion's is b deep), and its digits are 3s.
- **Run.** The start-up reaches `Kd [2] 0 0` (step 12) and then `Kd [] 0 28` (step 434). Rebuild 1 has m = 7, with its
  deepest digit at depth 24, and is complete at step 1077. Clearing that list gives b1 ≡ 0 (mod 8). Rebuild 2 therefore
  has m1 = b1/4 even, its clearing gives an odd b2, and R4 halts.
  - So the machine makes **two rebuilds and halts at the third R4**, exactly like the BB(9) champion.
  - **sigma = b2 + 4**, with b1 = Tv 7 1 7 and b2 = Tv (b1/4) 1 7 (section 3).
- **Proved in Coq** (no axioms):
  - `../proofs/BB10_champion_1RB1RA.v`, checked by check.py, verbatim:
    `PASS BB10_champion_1RB1RA.v: 1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ HALTS (machine-checked, no axioms)`.
  - `../proofs/BB10_champion_bound.v` proves `score_exact`, which gives the exact score b2 + 4, and
    `sigma_lower_bound`: f_ω(f_ω(25)) < score. A strong form gives b1 ≥ 2^25 f_25(f_25(2)), b1 ≡ 0 (mod 8) and
    score > f_ω(3(b1/4)+3).
  - New 10-state setup `BB102.v`/`Individual102.v`. `check.py` now accepts states A-J; it still passes the 7-, 8- and
    9-state proofs I re-ran.
- **Two 2-adic constants.** For every depth j ≥ 3 and admissible x, U_j(x) mod 2^K depends only on the parity of x: it
  is E ≡ ...1235431 (odd) for even x and O ≡ ...14394096 (even) for odd x. This comes from a fixed point of the residue
  recursion, computed for K ≤ 24 and odd moduli; the mod-8 case is proved in Coq as `U_mod8` for j ≥ 2.
  - Consequence: in this family (BB(9)-champion R1-R3 with any residue-driven R4) **a halting run makes at most two
    deep clearings**. The champion uses both.
  - A relative can therefore only beat the champion with a deeper first list (larger x in f_ω²(x)) or, at equal depth,
    a larger digit or slope. f_ω³ is out of reach within the family.
- **Grader.** `r10grade.py` reproduces the champion (EQUAL, key `w^2(25) v=2 slope=3/4`) and the BB(9) champion
  (BELOW, `w^2(8)`), and passes a synthetic self-test.
  - All 7,721 r10m14 holdouts (enumeration complete) were graded, plus the 12,067 r10m13-only holdouts that existed at
    22:10 on 2026-10-07; the r10m13 run is still going, and its snapshot had 19,788 lines. **No BEATS-CHAMPION?
    machine** (section 8).
  - Eight EQUAL machines: the champion itself and seven variants that clear the same lists. One of them
    (`..._0LF0LJ_---0LG`) leaves J0 unused, so the champion has an equivalent form with a free transition.

## 1. Configuration family and rules

The notation is that of the BB(9) champion report (`bb9_champion_1RB1RA0LC0LF.md`), with the structure to the RIGHT of
the head:

    Kd ds a b = 0^inf [D on 0] 1^(b+1) 0 1^a 0 1^d1 0 1^d2 0 ... 0 1^dn 0^inf      (ds top digit first; zero digits allowed)

The depth of a digit is its index, i.e. the number of digits above it.

| rule | statement | transitions used | status |
| --- | --- | --- | --- |
| R1 | Kd ds (a+1) b -> Kd ds a (b+3) | A0 A1 B0 B1 C0 D0 F0 F1 | Coq (KR1) |
| R2 | Kd (y+1 :: t) 0 b -> Kd (y :: t) (b+2) 1 | A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1 | Coq (KR2) |
| R3 | Kd (0^k ++ (y+1) :: t) 0 b, 1 <= k, 2k <= b -> Kd (2^(k-1) ++ (b+2-2k) :: y :: t) 2 1 | same as R2 | Coq (KR3) |
| R4 odd | Kd [] 0 (2m+1) -> halt (E0 = 1RZ) with b+3 ones (b+4 after the final write) | A0 A1 B0 C0 C1 D0 D1 E1 G1, E0 | Coq (KR4Ox) |
| R4, b = 4m | Kd [] 0 (4m) -> Kd [1,(0,0,3)^m,0,0,2] 0 0 in 8m²+32m+27 steps | + F0 G0 H0 H1 I0 I1 J0 J1 | Coq (KR4E4) |
| R4, b = 4m+2 | Kd [] 0 (4m+2) -> Kd [3,(0,0,3)^m,0,0,2] 0 0 in 8m²+40m+44 steps | same | Coq (KR4E6) |

- **Reuse.** R1-R3 and the odd R4 are the BB(9) champion's. Their Coq proofs are reused verbatim and re-checked against
  this machine's table. The clearing functions are therefore the same: U_0(x) = 3x+7, U_{j+1}(x) = U_j^(x-2j)(X_j),
  X_0 = 7, X_{j+1} = U_j(U_j(X_j)). A digit v at depth j maps b to U_j^v(b) when 2j <= b (`CDPx_all`).
- **R4 mechanism** (`r4phases.py`, even b ≤ 120):
  - **Phase 1.** Up to the first G0 the run coincides with the BB(9) champion's R4: same tape, same step count. It
    rewrites the counter into (110)-blocks.
  - **Phase 2.** A leftward pass G0, H1 H0 I1 J1 J0, then `(H1 H1 H0 I1 J1 J0)^m`, then a fixed tail.
  - In Coq this is the crossing lemma `cr_IL_110110: [1;1;0;1;1;0]^^n *> l <{{I}} r -->* l <{{I}} [0;1;1;1;0;0]^^n *> r`.
    Each loop turns two (110)-blocks into `100011`, i.e. a digit 3 behind two zero digits.
  - The BB(9) champion's I1 = 0LH and I0 = 1LB instead produce one (0,1) pair per block.
- **Literal checks** (all with 0 mismatches, made before the Coq proofs):
  - `gridcheck.py`: 7,680 configurations;
  - `deepcheck.py`: 4,700 real-run-shaped R2/R3 sites down to depth 24;
  - `r4check.py`: R4 for b ≤ 200, with exact quadratic step counts;
  - `usage_r123.py`: the transition usage in the table above.
- **Boundary region** (never reached by the run; relevant for relatives). With k leading zero digits and 2k ≥ b+1:
  - b odd: the machine halts;
  - b even: it rebuilds over the zeros, e.g. `Kd [0,0,0,1] 0 0 -> Kd [1,0,0,2,0,1] 0 0` (`unpred10.txt`).

## 2. The run from the blank tape

Literal trace (`kdtrace.exe`, 2·10^10 steps). `checkchain.py` validates every transition (15 R2, 2 R3, 1 R4, plus
every R1 inside the tracer) with 0 mismatches:

    step   12: Kd [2] 0 0          step 62: Kd [1] 0 7       step 434: Kd [] 0 28       (b0 = U_0(U_0(0)) = 28 = 4·7)
    step 1077: Kd [1,(0,0,3)^7,0,0,2] 0 0                 (R4, m = 7: deepest digit, a 2, at depth 24)
    step 1223: Kd [2,2,3,2,0,0,3,...] 2 1                  (R3 at depth 3 with b = 7: exactly 2k = 6 <= 7)
    step 5299: Kd [91,1,3,2,0,0,3,...] 2 1                 (R3 at depth 1; then 91 units of b -> 3b+7 ...)

The exact high-level run, proved in Coq (`run1`, `run2`, `halt`):

    b1 = Tv 7 1 7 = U_24(U_24(T7)),   T7 = U_21^3(U_18^3( ... U_3^3(7)))      (clearing [1,(0,0,3)^7,0,0,2] from b = 0)
    b1 ≡ 0 (mod 8)  [Coq: Tv_mod8 via U_mod8];  in fact b1 ≡ 41712 (mod 2^16), ≡ 16 (mod 32)  [modexact.py]
    rebuild 2: m1 = b1/4 (even),  b2 = Tv m1 1 7 = U_{3m1+3}(U_{3m1+3}(Tpre m1 1 7)),  b2 odd  [Coq: b2_odd]
    R4 #3 halts: c_end (b2/2) has b2 + 3 ones; E0 = 1RZ writes one more:  sigma = b2 + 4  [Coq: score_exact]

`Tpre m j B` clears the m triples (digit 3 at depths j+2, j+5, ...); `Tv` adds the final 2. Parity: every unit flips
the parity of b. Rebuild 2 starts at b = 0 and holds 1 + 3m1 + 2 units, so b2 is odd exactly because m1 is even.
Residues: sigma ≡ 55787 (mod 2^16).

## 3. Score in the fast-growing hierarchy (machine-checked)

`BB10_champion_bound.v` reuses the BB(9) bound file's lemma `bound` (for the same U, X):

    2^(j+1) n <= z  =>  2^(j+1) f_{j+1}(n) <= U_j(z),      2^(j+2) (j+1) <= X_j.

With it the file proves:
- `b1_big`: b1 >= 2^25 · f_25(f_25(2)), via T7 >= 2^22 f_22(21) >= 2^26 (the last digit sits at depth 24);
- `b1_quarter`: b1/4 >= f_25(25) = f_ω(25), via f_25(2) >= f_3(2) = 2048;
- `second_big`: Tv m 1 7 >= f_ω(3m+3), since the second list's deepest digit is at depth 3m+3;
- `sigma_lower_bound`: **f_ω(f_ω(25)) < sigma**, with `f_omega n = f n n`, `f 0 = S`, `f (k+1) n = (f k)^n n`;
- `sigma_lower_bound_strong`: sigma > f_ω(3(b1/4)+3) with b1 >= 2^25 f_25(f_25(2)) and b1 ≡ 0 (mod 8).

So the wiki's claim f_ω²(25) holds, and sigma > f_ω(f_25(f_25(2))) is slightly sharper.

**Upper bound (machine-checked, `../proofs/BB10_champion_upper.v`, added 2026-10-08 for the BB(10) candidate
comparison).** It uses `arrow` = `BB9_record_1RB0RA.arrow`, where arrow k 2 x is 2 with k Knuth arrows applied to x;
the 9-state record files are only Required. It proves:
- `U_arrow_tight`: U_j(x) <= arrow j 2 (2x+4) and X_j <= arrow (j+1) 2 4 for j >= 1. This is one arrow tighter than
  `Uc_le` of BB9_record_vs_champion.v.
- `Tv_le_tight`: Tv m 1 7 <= arrow (3m+4) 2 (6m+7).
- `b1_le_tight`: b1 <= arrow 25 2 49.
- `champion_upper`: b2 + 4 <= arrow N' 2 (2N') and N' <= arrow 25 2 49, with N' = 3·⌊b1/4⌋ + 4.
- `champion_upper_ex`: exists Np, 4 <= Np <= arrow 25 2 49, and the halting configuration has N ones with
  N + 1 <= arrow Np 2 (2Np).

All are Closed under the global context, and probe `coq/probe_upper.v` re-checks the statements. So
**f_ω(f_ω(25)) < sigma <= arrow N' 2 (2N') with N' <= arrow 25 2 49**: one f_ω-scale application whose index is between
f_25(25) and about 2↑^25 49.

For comparison, the BB(9) champion has b1 >= 256 f_9(2) and sigma > f_{b1+2}(b1). Its first list is (0,1)^3 (0,2),
with depth 7. The BB(10) champion keeps the shape and raises the first level from 8 to 25.

## 4. Two 2-adic constants: at most two deep clearings in this family

`modexact.py` computes U_j modulo 2^K exactly through residue maps h_j: U_j(x) ≡ h_j(x mod 2^K) for x ≥ T_j. Orbit
periods must divide 2^K, which is asserted. Values below 2^64 are kept exact; every larger one is ≥ 2^64, above every
threshold. It does not use the stabilisation heuristic of the old `modeval.py`, and it agrees with it (752 mod 1024 for
both champions' b1).

- **Fixed point** (`hstab2.py`, K = 4..24; `hstab_odd.py`, moduli 2^6·3·5·7 and 2^8·9·5·7·11).
  - From depth 3 on (depth 2 for x ≥ T_2), h_{j+1} = h_j and X_{j+1} ≡ X_j.
  - The orbit of X_j is (E, O) with period 2.
  - By induction, U_j(x) ≡ E for even x and ≡ O for odd x, for all j ≥ 3 and x ≥ 2j. Here E ≡ 1235431 and
    O ≡ 14394096 (mod 2^24).
  - The mod-8 shadow of this (7 and 0) is the Coq lemma `U_mod8`, the mod-8 refinement of the BB(9) bound file's `mod4`.
- **Digit rule.** A digit v ≥ 1 at depth ≥ 3 sends b to E if b+v is odd and to O if b+v is even. So after a deep
  clearing (deepest digit at depth ≥ 3) the counter is E or O, decided by the parity of the start counter plus the number
  of units.
- **Cap.** R4 reads b through a residue (period p | 2^K, p ≤ 8 for every machine seen), so it acts identically on all
  E-states and on all O-states.
  - A halting run never repeats an R4 state, and each deep clearing ends in E or O. Hence **at most two deep clearings**
    occur. The champion uses both: b0 = 28 → O → rebuild → E → halt.
  - Shallow rebuilds (lists of bounded depth) can sit in between; each adds only boundedly many levels.
- **Effect of b0 under the champion's R4.** b0 ≡ 4 or 6 (mod 8) gives two deep clearings (the champion: 28). b0 ≡ 0 or
  2 gives one, i.e. a halt at R4 #2 with sigma ≈ f_ell²(..). Odd b0 halts at once.

## 5. What sets the score

1. **The start list `Kd [2] 0 0`**, reached at step 12 using A0 B0 C0 C1 D1 F0 G0 H0 H1 I0. It gives b0 = 28. Every
   r10m14 machine that keeps R1-R3 reaches the first R4 at b0 = 28, step 434, because all those transitions are fixed
   there. r10m13 frees E1 instead, and E1 is one of the transitions R2/R3 read, so its extra machines leave the
   family.
2. **The rebuild map** b = 4m -> `[1,(0,0,3)^m,0,0,2]`.
   - For b0 = 28 it gives depth 3·7+3 = 24, so the first level is x = 25: b1 ≈ f_25².
   - For the second rebuild it gives slope 3/4, so sigma > f_ω(3b1/4 + 3). The level x grows by 3 per +4 in b0.
   - The leading 1 leaves b = 7 at the first R3 site, depth 3, which is exactly the limit 2·3 ≤ 7. Three zero digits per
     block would put the first site at depth 4 > 7/2, inside the boundary region (see the self-test).
3. **The halting pattern** (section 4). b0 ≡ 4 (mod 8) gives exactly the family's maximum of two deep clearings.

In one line: sigma = b2 + 4 ≈ f_ω(f_25²(...)) ≈ "f_ω²(25)". The exponent 2 counts the deep clearings (capped at 2 in
this family), and 25 = 3·⌊b0/4⌋ + 4.

## 6. Coq formalization

| file | content | build |
| --- | --- | --- |
| `BB102.v`, `Individual102.v` | 10-state instance of busycoq, mirroring BB92/Individual92, plus `{{J}}>`/`<{{J}}` notations | ~18 s each |
| `BB10_champion_1RB1RA.v` | `Theorem halt : halts tm c0` | ~27 s |
| `BB10_champion_bound.v` | `score_exact`, `sigma_lower_bound`, `sigma_lower_bound_strong` | ~23 s |

`BB10_champion_1RB1RA.v` contains:
- the machine lemmas copied from `BB9_champion_1RB1RA.v`: crossings, R1, R2, ENTRY, LOOP, FINAL, KR1-KR3, LOOPS;
- the new `cr_IL_110110`, `R4E4`/`R4E6`, `KR4E4`/`KR4E6`, `KR4Ox`, and `init_reach` (12 steps);
- the exact clearing machinery from `BB9_champion_bound.v`: U, X, growth, parity, CDPx_all;
- the new `U_mod8`/`Pm8_all`, `TRIP_ALL`, `Tv_par`, `Tv_mod8`, and the run.

It is generated by `coq/gen_halt.py`, and `coq/gen_bound.py` generates the bound file.

- `python check.py BB10_champion_1RB1RA.v` prints
  `PASS BB10_champion_1RB1RA.v: 1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ HALTS (machine-checked, no axioms)`.
- **check.py extension.** Only the regexes changed: state letters A-I became A-J, the `Individual(\d)2` import became
  `Individual(\d+)2\.`, and the state string `'ABCDEFGHI'` became `'ABCDEFGHIJ'`; line endings are unchanged.
  - Re-run, all PASS: `BB9_champion_1RB1RA.v`, `BB9_record_1RB0RA.v`, `BB8_champ35_1RB0RA.v` and `BB7_16582_1RB1LD.v`
    (never halts).
  - Negative tests: a wrong J1 in the header gives `FAIL ... transition J1: Coq has 0LJ, machine string has 0LH`; a 9-row
    header gives `FAIL ... machine has 9 states but file does not import Individual92`.
- **Probe** (`coq/probe10.v`, log `coq/probe10.log`). It prints `tm`, `iter`, `f`, `f_omega`, `ones`, `count1`,
  `sym_val`, `b1`, `b2`, `second` and `Tv`. It re-checks the three bound statements against explicitly written types,
  and prints "Closed under the global context" for `halt`, `score_exact`, `sigma_lower_bound` and
  `sigma_lower_bound_strong`.
- **Pitfall (new, cost one 24 GB coqc).** `repeat split` on a goal containing `b1 mod 8 = 0` applies `eq_refl` and makes
  Coq evaluate b1. Split such conjunctions explicitly. `Opaque` declarations are not exported from an imported file, so
  re-declare `Opaque U X Tv b1 b2` in each importing file. `coq/coqc_guard.ps1` runs coqc with a memory and time guard.

## 7. The grader `r10grade.py`

Usage, in `bb8_list\investigations\bb10_champion_1RB1RA_0LF0LJ`, with `python` = `..\..\..\third_party\venv311\Scripts\python.exe`:

    python r10grade.py MACHINE [-v]            # one machine; -v prints every stage
    python r10grade.py --list FILE OUT.tsv     # one TSV row per machine; BEATS rows also go to stdout
    python selftest.py                         # synthetic R4 rules through the abstract stage and the comparison

TSV columns: machine, grade, key, note (score form, halting class or reason), fitted R4 rule, the exact rebuilds seen
(`b=28->[...]`), and the huge rebuilds (template, slope).

Stages:
1. **Parse and quick rejection.** Parsing fails loudly, giving INVALID. A 2·10^4-step in-process literal run and a
   3·10^5-step `kdtrace` run reject early deviations from R1-R3.
2. **Literal run** from the blank tape (`kdtrace.exe`, 2·10^7 steps).
   - R1 is checked inside the C++ tracer, and every R2/R3 transition against the prediction.
   - The exact R4 events are recorded.
3. **R1-R3.**
   - A machine that agrees with the champion on all 12 transitions R1-R3 read (A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1)
     inherits them verbatim.
   - Otherwise a 1,763-configuration literal grid is run.
4. **R4 fit** (`r4fit.py`, C++ prober `r4probe.exe`, cross-checked against Python on 4 machines × 144 b). Each class b = pn + r
   (p ≤ 8) must be all HALT, all NO-RETURN, or all `P + B^(αn+β) + S` rebuilds. The fit uses b = 16..79 and is validated
   on b = 80..143 and on the literal R4 events.
5. **Abstract continuation** (`hlev.py`, residues mod 2^16, digit rule of section 4).
   - It stops at a halting class, a repeated residue state, a NO-RETURN class (runaway), or a loop of shallow rebuilds.
     For a shallow loop it reports BELOW, because no deep clearing can follow.
   - Exact counters too small for an R3 site take one literal step.
6. **Key** `w^k(x) v=.. slope=..`, meaning sigma ~ f_ω^k(x).
   - k counts the deep clearings. The first, of the last exact rebuilt list, counts when its deepest digit is at depth
     ≥ 3.
   - x is that depth + 1; v is the deepest digit; slope is the depth of the next rebuilt list per unit of b.
   - The champion's key is `w^2(25) v=2 slope=3/4`. Keys are compared lexicographically, so one more f_ω application,
     or a larger inner argument at the same k, grades BEATS-CHAMPION?.
7. **Grades**:
   - BEATS-CHAMPION?: verify by hand;
   - EQUAL: same key and lists;
   - EQUAL-KEY;
   - BELOW;
   - NONHALT-PREDICTED: a cycle, or a NO-RETURN class;
   - HALTS-EARLY: with sigma;
   - OTHER-STRUCTURE;
   - R4-UNFIT: R1-R3 hold, R4 fits no template;
   - UNRESOLVED;
   - INVALID.

Validation (`validation.txt` → `validation.tsv`; `selftest.py`):

| machine | grade | key / note |
| --- | --- | --- |
| BB(10) champion; also with E0 = `---` (its TNF form) | EQUAL | `w^2(25) v=2 slope=3/4`, halts at R4 class 3 mod 4 |
| BB(9) champion `..._1LB0LH` | BELOW | `w^2(8) v=2 slope=1`: rebuild at b0 = 6, depth 7; matches the Coq analysis |
| BB(11) champion | OTHER-STRUCTURE | literal R1 fails |
| our BB(9) record `1RB0RA_..._0LH---`, BB(7) champion | OTHER-STRUCTURE | literal run leaves R2/R3 |
| `badmachine`, a table with an undefined target K | INVALID | parse error |
| selftest (synthetic R4 rules from b0 = 28) | PASS | see the cases below |

The self-test cases:
- the champion's rule gives EQUAL;
- (0,0,0,3) blocks with a leading 3 give BEATS-CHAMPION? `w^2(33)`;
- (0,0,0,3) blocks with a leading 1 give UNRESOLVED (boundary region at depth 4, b = 7);
- digit-4 blocks give BELOW `w^1(25)` (parity: one deep clearing);
- all classes rebuilding gives NONHALT-PREDICTED;
- a final digit 3 gives BELOW.

Limitations:
- R1-R3 must be the BB(9) champion's.
- R4 must have period ≤ 8 and one repeated block.
- R4 uniformity for huge b is extrapolated from b ≤ 143 (for the champion it is proved).
- OTHER-STRUCTURE machines are not scored.
- The "shallow loop ⇒ BELOW" conclusion and the cap rest on the residue argument of section 4.

## 8. Grading of the r10m14 and r10m13 holdouts

Coverage:
- **r10m14**: complete enumeration, 4 parts, 7,721 holdouts, all graded.
- **r10m13**: snapshot of 2026-10-07 22:10, 19,788 holdouts (the run is still going). It contains all 7,721 r10m14
  holdouts plus 12,067 r10m13-only machines, all graded.

Several passes were run at Idle priority: pass 1 on the first 3,355 r10m14 holdouts, passes 2-6 with the final grader.
Pass-1 family rows were either regraded or had their keys converted to the f_ω^k(x) form (`snap1_converted.tsv`; same
logic). The UNRESOLVED and R4-UNFIT rows were regraded with the final grader, which adds R4 periods 3, 6 and 12 and
treats shallow loops. Later passes override earlier ones; the merge is done by `grades/summarize_final.py`.

**r10m14 (complete enumeration)**: 7721 holdouts in the snapshot, 7721 graded.

| grade | count |
| --- | --- |
| OTHER-STRUCTURE | 5615 |
| NONHALT-PREDICTED | 1308 |
| BELOW | 783 |
| EQUAL | 8 |
| R4-UNFIT | 4 |
| HALTS-EARLY | 3 |

Keys of the family machines that halt (f_omega^k(x), v = deepest digit, slope):

| grade | key | count |
| --- | --- | --- |
| BELOW | `w^1(15) v=2 slope=0` | 251 |
| BELOW | `w^1(15) v=1 slope=0` | 148 |
| BELOW | `w^0(1) v=47 slope=0` | 115 |
| BELOW | `w^1(13) v=6 slope=0` | 46 |
| BELOW | `w^1(14) v=2 slope=0` | 40 |
| BELOW | `w^1(31) v=2 slope=0` | 32 |
| BELOW | `w^1(13) v=1 slope=0` | 17 |
| BELOW | `w^1(14) v=1 slope=0` | 13 |
| BELOW | `w^1(14) v=3 slope=0` | 13 |
| BELOW | `w^1(17) v=2 slope=0` | 12 |
| BELOW | `w^2(9) v=2 slope=1/4` | 12 |
| EQUAL | `w^2(25) v=2 slope=3/4` | 8 |
| BELOW | `w^1(16) v=2 slope=0` | 7 |
| BELOW | `w^1(12) v=8 slope=0` | 7 |
| BELOW | `w^1(15) v=3 slope=0` | 6 |
| BELOW | `w^1(13) v=2 slope=0` | 6 |
| BELOW | `w^1(15) v=4 slope=0` | 6 |
| BELOW | `w^1(8) v=4 slope=0` | 6 |
| BELOW | `w^1(13) v=3 slope=0` | 4 |
| BELOW | `w^1(13) v=4 slope=0` | 4 |
| BELOW | `w^1(13) v=5 slope=0` | 4 |
| BELOW | `w^2(7) v=1 slope=1/4` | 4 |
| BELOW | `w^2(9) v=1 slope=1/4` | 4 |
| BELOW | `w^1(11) v=1 slope=0` | 4 |
| BELOW | `w^1(14) v=5 slope=0` | 3 |

EQUAL (8):

- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_---0LG` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)
- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)
- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH1RH` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)
- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0RJ_0LJ0LG` w^2(25) v=2 slope=3/4 score ~ f_omega^1(f_25(..)) [champion: f_omega^1(f_25(..)) ~ f_omega^2(25)]; halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0) [pass-1 row; key converted to the f_omega^k(x) form]
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_---0RA_1LB0LG_1LH1RE_0LI1LH_0LF0LF_1LB1LJ` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_---0RA_1LB0LG_1LH1RE_0LI1LH_0LF0RH_1LB1LJ` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LB_1LH1LF` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LB_1LH1RI` w^2(25) v=2 slope=3/4 sigma ~ f_omega^2(25) [champion f_omega^2(25)] (first list cleared at level f_25, digit 2; 1 deep rebuild(s) from huge counters, slope 3/4); halts at R4 class 3 mod 4, HALT(ones=4n+6 at E0)

R4-UNFIT (4):

- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_0RJ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0RE_---0RE`  R1-R3 hold (grid and literal run), R4 does not fit a template: no R4 template with period in 1,2,3,4,6,8,12 (outcomes {'K': 64, 'HALT': 64})
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_0RI0RA_1LB---_1LH1RE_0LI1LH_0LF0RE_1LB1LJ`  R1-R3 hold (grid and literal run), R4 does not fit a template: no R4 template with period in 1,2,3,4,6,8,12 (outcomes {'K': 128})
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_0RI0RA_1LB1LF_1LH1RE_0LI1LH_0LF0RE_---1LF`  R1-R3 hold (grid and literal run), R4 does not fit a template: no R4 template with period in 1,2,3,4,6,8,12 (outcomes {'K': 128})
- `1RB1RA_0LC0LJ_0RD1LC_1RA1RG_0RI0RA_1LB1LF_1LH1RE_0LI1LH_0LF0RE_---1RI`  R1-R3 hold (grid and literal run), R4 does not fit a template: no R4 template with period in 1,2,3,4,6,8,12 (outcomes {'K': 128})

HALTS-EARLY (3):

- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF1LJ_1LI1LJ`  halts at step 1365766 (state E reading 0), sigma = 1247; 1 exact rebuilds before the halt
- `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF1RJ_1LI1LJ`  halts at step 7999092 (state E reading 0), sigma = 3019; 3 exact rebuilds before the halt
- `1RB1RA_0LC0RG_0RD1LC_1RA1RG_1RG0RA_1LB---_1LH1RE_0LI1LH_0LF0LJ_1LE1LE`  halts at step 652596 (state F reading 1), sigma = 1275; 0 exact rebuilds before the halt

OTHER-STRUCTURE reasons:

| reason | count |
| --- | --- |
| literal run leaves R2/R3 | 5476 |
| literal R1 fails | 98 |
| grid fails (R1-R3) | 41 |

NONHALT-PREDICTED: cycle 1284, no-return R4 class 24

**r10m13-only (snapshot of 2026-10-07 22:10, 19,788 holdouts of which 7,721 are the r10m14 holdouts above; the rest)**: 12067 holdouts in the snapshot, 12067 graded.

| grade | count |
| --- | --- |
| OTHER-STRUCTURE | 12059 |
| HALTS-EARLY | 8 |

HALTS-EARLY (8):

- `1RB1RA_0LC0RA_0RD1LC_1RA1RG_1LJ0LB_1LB---_1LH1RE_0LI1LH_0LF0LE_0RE1RB`  halts at step 15563333 (state F reading 1), sigma = 3840; 0 exact rebuilds before the halt
- `1RB1RA_0LC0RA_0RD1LC_1RA1RG_1LJ0LB_1LB---_1LH1RE_0LI1LH_0LF0LE_0RG1RB`  halts at step 15563067 (state F reading 1), sigma = 3839; 0 exact rebuilds before the halt
- `1RB1RA_0LC0RA_0RD1LC_1RA1RG_1LJ0LB_1LB---_1LH1RE_0LI1LH_0LF0LE_1LC1RB`  halts at step 15563325 (state F reading 1), sigma = 3840; 0 exact rebuilds before the halt
- `1RB1RA_0LC0RA_0RD1LC_1RA1RG_1LJ0LB_1LB---_1LH1RE_0LI1LH_0LF0LE_1RC1RB`  halts at step 15563327 (state F reading 1), sigma = 3840; 0 exact rebuilds before the halt
- `1RB1RA_0LC0RA_0RD1LC_1RA1RG_1LJ0LB_1LB---_1LH1RE_0LI1LH_0LF0LE_1RG1RB`  halts at step 15563323 (state F reading 1), sigma = 3840; 0 exact rebuilds before the halt
- `1RB1RA_0LC0RA_0RD1LC_1RA1RG_1LJ0LB_1LB---_1LH1RE_0LI1LH_0LF0LE_1RJ1RB`  halts at step 15563329 (state F reading 1), sigma = 3840; 0 exact rebuilds before the halt
- `1RB1RA_0LC1RD_0RD1LC_1RA1RG_0RG0RD_1LB---_1LH1RE_0LI1LH_0LF0LJ_0LC1LE`  halts at step 13477983 (state F reading 1), sigma = 3309; 0 exact rebuilds before the halt
- `1RB1RA_0LC1RJ_0RD1LC_1RA1RG_1LA1LE_1LB1RB_1LH1RE_0LI1LH_0LF---_0RD0RF`  halts at step 590112 (state I reading 1), sigma = 679; 0 exact rebuilds before the halt

OTHER-STRUCTURE reasons:

| reason | count |
| --- | --- |
| literal run leaves R2/R3 | 11870 |
| grid fails (R1-R3) | 182 |
| literal R1 fails | 7 |



Reading:
- **No machine in either run beats the champion.** Family machines that halt make at most one deep clearing (keys
  `w^1(x)` with x ≤ 31, `w^0`), or two deep clearings from a shallower first list (`w^2(9)`, `w^2(7)`, slope 1/4).
  - 1,308 family machines never halt (predicted). In 1,284 of them the residue dynamics cycles, as the cap of
    section 4 predicts; in 24 a no-return R4 class (a runaway) is reached.
- **The 8 EQUAL machines** all clear the champion's lists, so their score is exactly the champion's:
  - the champion (E0 undefined);
  - `..._0LF0LJ_---0LG`: J1 = 0LG followed by G0 = 1LH does what J1 = 0LJ followed by J0 = 1LH does, so J0 is free;
  - `..._1LH1RH` and `..._0LF0RJ_0LJ0LG`: the same Kd configurations through a slightly different pass (b = 8: 129
    steps instead of 123);
  - four machines with B1 = 0LJ whose R1 sweep runs through J (in `..._1LB1LJ` exactly as F does in the champion:
    J1 = 1LJ, J0 = 1LB) and whose rebuild pass is re-routed: `..._1LB0LG_..._0LF0LF_1LB1LJ`,
    `..._1LB0LG_..._0LF0RH_1LB1LJ`, `..._0LF0LB_1LH1LF` and `..._0LF0LB_1LH1RI`.
- **The 4 R4-UNFIT machines, examined by hand (`r4probe.exe M 0 144`):**
  - `..._0RJ0RA_..._0LF0RE_---0RE`: even b rebuilds a 3- or 4-digit list whose digits are piecewise linear in b; odd b
    halts. There is no deep rebuild after the first, so it is BELOW.
  - `..._0RI0RA_..._0LF0RE_1LB1LJ`, `..._---1LF`, `..._---1RI`: every R4 outcome for b ≤ 143 is a rebuild (shallow
    lists for even b, `[(2)^((b-1)/2),1]` with a = 2 for odd b). They cannot halt at R4, so they never halt if the
    rules hold.
- **HALTS-EARLY**: 3 r10m14 machines (sigma 1,247, 3,019, 1,275) and 8 r10m13-only machines (sigma ≤ 3,840).
- **The 12,067 r10m13-only machines** are all OTHER-STRUCTURE or HALTS-EARLY. Their E1 differs from 0RA, and E1 is one
  of the transitions R2/R3 read, so none of them is in the champion's family.

## 9. Reproduction

In `bb8_list\investigations\bb10_champion_1RB1RA_0LF0LJ` (python as above; `kdtrace.exe`, `r4probe.exe` built with
`g++ -O2 -std=c++17 -static`, `C:\msys64\ucrt64\bin` on PATH):
- `python trace.py 3000000`: Kd trace with the transitions used by each step. For the long trace, run
  `kdtrace.exe MACHINE 20000000000 > trace_ch10_2e10.txt` (Idle, about 3 min), then
  `python checkchain.py trace_ch10_2e10.txt`.
- Literal checks: `python gridcheck.py`, `deepcheck.py`, `r4check.py 200`, `r4phases.py`, `usage_r123.py`.
- Residues: `python modexact.py` (b1 mod 2^K), `hstab2.py` (fixed point, E and O), `hstab_odd.py` (odd moduli).
- Grader: `python r10grade.py MACHINE -v`, `python selftest.py`, `python r10grade.py --list validation.txt validation.tsv`.
- Coq, in `bb8_list\proofs`:
  - regenerate with `python ..\investigations\bb10_champion_1RB1RA_0LF0LJ\coq\gen_halt.py` (and `gen_bound.py`);
  - then `python build.py BB10_champion_bound.v` and `python check.py BB10_champion_1RB1RA.v`;
  - the probe is `coqc -Q ..\..\third_party\busycoq\verify BusyCoq -Q . BB8 ..\investigations\bb10_champion_1RB1RA_0LF0LJ\coq\probe10.v`.
- Wiki row: `wiki_champions_excerpt.txt`.

## 10. Open questions and recommendations

- Proved: halting, the exact score b2 + 4, the bound f_ω²(25) and b1 ≡ 0 (mod 8).
- Not proved: the full residue fixed point (E and O for all K) and the "at most two deep clearings" cap. An upper bound
  is now proved (`BB10_champion_upper.v`, section 3).
  Both are computer or paper arguments.
- **For the BB(10) search** (the lead's call):
  - **within this family.** Only a deeper first list can win, at the same parity pattern. In r10m14 the first R4
    counter is fixed at 28, and no holdout's R4 produces a deeper list with that pattern. r10m13 (root with E1 free)
    adds only machines outside the family. The start-up transitions (A0 B0 C0 C1 D1 F0 G0 H0 H1 I0) are the first ten
    of the TNF path, so b0 = 28 is fixed in every subtree from r10m10 on. Only wider roots (r10m9 or below) could
    change b0 and hence x.
  - **other families.** A 10-state machine with one more deep rebuild in a different family would win. For example, our
    BB(9) record, about f_ω(2↑^13 3) after its single rebuild, plus one more deep rebuild gives about
    f_ω(f_ω(2↑^13 3)) > f_ω²(25).
  - **free transition.** The equivalent champion form with J0 free (`..._0LF0LJ_---0LG`) is a natural redirect root,
    since the champion family can host one more transition.

Approximate token cost of this assignment: about 0.75M tokens. CPU: the r10grade passes at Idle priority, the
2·10^10-step literal trace, and the Coq builds (about 1.5 min).
