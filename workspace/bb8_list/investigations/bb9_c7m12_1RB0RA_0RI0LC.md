# 9-state candidate `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0RE0LG_---1LF` (c7m12 holdout)

> **!!! POSSIBLE NEW BB(9) CHAMPION (section 10.1, strong evidence, NOT proved):**
> `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---` and its twin `..._0RH0RE_0LH---`.
> - Its first rebuild turns L(B) into a champion list of 12B - 12 ONES, which is used Ackermann-style.
> - The machine then halts at the end of the list.
> - **sigma > 2^^(12B-13) 3 with 2B + 4 = 2^^13 3**, i.e. about f_omega(6*(2^^13 3)), far above f_omega(f_9(2)).
> - The main machine and both groups below are NOT records.

> **Verdict: HALTS. It does NOT beat the BB(9) champion, and it does not come close.**
> - The machine rebuilds once, at its first list exhaustion. The halt comes at the *second* exhaustion, but the list
>   being exhausted there is a small 4-digit inner list. The huge rebuilt list L(B) is never used.
> - Score (ones on the tape at the halt), with B = the BB(7) champion's final accumulator (2B + 4 = 2^^13 3, i.e.
>   2 with 13 arrows 3) and b_f the inner counter's final accumulator (2 b_f + 4 = 2^^6 3):
>   **sigma = 24 B + 6 b_f + 47 = 12*(2^^13 3) + 3*(2^^6 3) - 13** (+1 if the undefined halting transition counts as
>   writing a 1). That is about 4x the BB(7) champion's 3*(2^^13 3) + 22.
> - The BB(9) bar is f_omega(f_9(2)) ~ 2^^(f_9(2)) f_9(2). This score is far below it, and also far below our 8-state
>   record 12*(2^^37 3) + 59.
> - Confidence: **strong evidence** (no Coq proof). Every rule was checked by literal simulation on grids, with
>   end-to-end literal runs of the composed rules. Symbolic uniformity in the parameters is assumed, not proved.
>
> **GROUP 2 (mirrored E0): ALSO HALTS. Not a record (section 9).**
> Machines: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---` and `..._1LI0LC_..._1RH---`.
> - They follow the main machine's chain up to the inner exhaustion, then keep going. A second-level counter runs, and
>   its borrow does reach the rebuilt list L(B).
> - L(B)'s 12B - 2 zeros are rebuilt into k = (12B - 30)/7 groups `D(4) D(2) D(7)`.
> - Only the **last** group is ever used. When the borrow reaches that group's `D(4) D(2) D(2)` block, it collapses
>   into a sublist `11 (10)^Y` directly behind the previous group's D(7), which has dropped to D(3). That sublist's
>   exhaustion steps onto a 1, and I1 is the undefined (halting) transition.
> - **sigma = (120*(2^^13 3) - 1080)/7 + 212*4^b_f + 48*4^b_last + 68** for `..._0RF---`; the `..._1RH---` version
>   has one more. This is about 17.1*(2^^13 3): roughly 6x the BB(7) champion, far below f_omega(f_9(2)).
> - The f_omega mechanism never materialises.
> - Confidence: strong evidence (literal checks of every stage on the real residue class; no Coq).

Notation: `2^^k x` means 2, k up-arrows, x (Knuth). `D(m) = (10)^m 1`.

## 1. Templates and rules
- Outer (champion) template `K(ds; a; b) = 11 D(3d_1+1) ... D(3d_n+1) D(3a+1) (10)^(3b+2) 111001`, head in state B
  on the blank to the right. This is the dlscan2 template `R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001`.
- Champion rules, in K form. All three were checked literally for this machine (section 4).
  - R1: `(ds; a+1; b) -> (ds; a; 2b+2)`
  - R2: `(ds, d+1; 0; b) -> (ds, d; 2b+2; 0)`
  - R3: `(ds, d+1, 0^(k+1); 0; b) -> (ds, d, 2b+2, 0^k; 0; 0)`
- Ligocki-style form: `A = 2b+1`, list nearest-first `[a, d_n, ..., d_1]`. The rules become
  `B(A; x+1, ...) -> B(2A+3; x, ...)` and `B(A; 0^k, 0, x+1, ...) -> B(1; 0^k, A+1, x, ...)`.
- Closed form, the same rule system as `proofs/BB8_champ35_exact.v` (machine-checked there): `B(5; [1]^k)` ends
  with all digits 0 and `A_f + 3 = 2^^(k+1) 3`, i.e. `2 b_f + 4 = 2^^(k+1) 3`. Hand checks: k = 1 gives b_f = 6,
  k = 2 gives b_f = 2^15 - 2.

## 2. How the machine emulates the champion
- A-G equal the BB(7) champion except E0 (champion: halt) and G0 (champion: `0RG`). The champion uses G0 often:
  about 31,568 times per 1e9 steps, always in the context `G0 x 0 1 ...`.
- Here `G0 -> 0RH`, `H1 -> 0LG`, `G0 -> 0RH`, `H0 -> 0RE`, `E0 -> 0RI`, `I1 -> 1LF`, `F0 -> 1RG`, `G1 -> 0RF`
  reproduces the champion's `G0, G1, F0, G1` (same tape, same exit state F, 4 extra steps). So E0, H and I1 are
  part of the ordinary engine. A halt needs E0 with a 0 to the right of the head (`I0` undefined).
- Literal blank-tape matches: K(2,0^10;0;0) @2149, K(1,2,0^9;0;0) @2971, K(1^10,2;0;0) @7849,
  **K(1^11;1;2) = B(5;[1]^12) @8317**, K(1^11;0;6) @9135, K(1^10,0;14;0) @12385.
- The first exhaustion is therefore the champion's halting configuration K(0^11; 0; B), with 2B + 4 = 2^^13 3.
- Cross-check of this B: from K(0^11;0;b) the BB(7) champion halts with 6b + 33 ones (literal, b = 1, 2, 3, 10).
  That gives sigma_7 = 6B + 34 = 3*(2^^13 3) + 22, the known exact value.

## 3. Post-exhaustion behaviour (question 1)
### 3a. Left rebuild (n = 11, the only case the real run meets)
`K(0^11; 0; b)  ->  J_b(1*, 1, 1, 1; 1; 2)` in exactly **324 b^2 + 2334 b + 6524 steps** (b >= 1). Here:
- `J_b(e1*, e2, e3, e4; a; y) = L(b) X D(2) D(3e1+2) D(3e2+1) D(3e3+1) D(3e4+1) D(3a+1) (10)^(3y+2) S'`, head in B
  on the blank to the right.
- `L(b) = 11 D(7) D(1)^(12b-2) D(0)`. This is a fresh champion start list K(2, 0^(12b-2)), i.e. 12b - 1 digits.
- `X = (10)^8 0 1111 (10)^3 0` is fixed junk.
- `S' = 1^8 00 1 00 1`.
- The inner list's first digit e1 uses the encoding 3e+2, behind a `D(2)` boundary.

Checks:
- Literal match of the whole word for b = 1..10, 14, 30, 62, 126, 254, 510. The step formula is exact for all 16
  values, which is consistent with a fixed sequence of sweeps.
- b = 0 is a different case and irrelevant here, since B is huge.

### 3b. Right-end process = the champion's program on the inner list
- R1, R2 and R3 hold on `J` (section 4). The borrow from e1 is literal too:
  `J(1*,0,0,0;0;b) -> J(0*,2b+2,0,0;0;0)` (b = 0..12).
- `J(1*,1,1,1;1;2)` is `B(5;[1]^5)`. It runs to `J(0*,0,0,0;0;b_f)` with **2 b_f + 4 = 2^^6 3**.
- The head never goes left of the D(2) boundary, so L(b) is untouched.
- This is the "nested counter" seen in the earlier traces. The run (01)^X with X = 3a+1 (40, 37, 34, ..., 4, 1) is
  the inner a-digit. The new (01)^196597 after the borrow is a = 2*98300 + 2.

### 3c. Inner exhaustion
- `J_B(0*,0,0,0;0;b) -> HALT` in state I reading 0, after exactly **36 b^2 + 636 b + 920 steps**, with
  **24 B + 6 b + 47 ones**.
- Final tape for B = 1, b = 0:
  `111 (01)^7 1 (0 11)^9 0 111 (01)^7 00 1^5 (01)^(6b+10) (10)^2 00 [I]0 1 0 11 0 11 00 111 00 1 00 111 00 1 00 1 0 1`.
- Checks:
  - B = 1: every b = 0..700. B = 3: b = 0..60. B = 2: b = 0..2.
  - End to end from smaller inner states, composing R1-R3 with the exhaustion, ones as predicted:
    J(0*,0,0,1;0;0) gives b_f = 6; J(0*,0,0,0;3;0) gives 14; J(0*,0,0,0;7;0) gives 254;
    J(0*,0,1,0;0;0) gives **32766** (halt at step 51,563,202,864).

## 4. Rule verification (literal; `rulegrid.py` driving `neighbors/probe2.exe`)
| template | probes | mismatches |
|---|---|---|
| outer K | 580 (lists <= 3 digits, d,a <= 2, b <= 4) + 2 x 9,513 (<= 4 digits, d,a <= 3, b <= 6) | 0 |
| inner J, e1 = 1* | 580 + 2 x 9,513 (with L(1), L(2)) | 0 |
| inner J, e1 = 0* | 580 + 9,513 | 0 |

## 5. Halting verdict and score (questions 2 and 3)
1. Blank -> K(1^11;1;2) -> (R1-R3) -> first exhaustion K(0^11; 0; B), with 2B + 4 = 2^^13 3.
2. Rebuild -> J_B(1*,1,1,1;1;2) -> (R1-R3) -> J_B(0*,0,0,0;0;b_f), with 2 b_f + 4 = 2^^6 3.
3. Halt. **sigma = 24B + 6 b_f + 47 = 12*(2^^13 3) + 3*(2^^6 3) - 13**, or -12 with the final write counted.
   - Steps are Theta(B^2): the rebuild alone takes 324 B^2 steps.
   - Residues: B + 2 and b_f + 2 are powers of 2, so both are 2 mod 4. Tested values of that form:
     B in {6, 14, 30, 62, 126, 254, 510}; b in {6, 14, 30, ..., 510} and 32766. All behave like the other values.
4. Comparison:
   - About 4*sigma(BB(7) champion).
   - Far below the 8-state record 12*(2^^37 3) + 59.
   - Hopelessly below f_omega(f_9(2)): that would need about f_9(2) arrows, and this score has 13.

The b-dependence of the inner exhaustion is trivial. It halts for every b, so no residue condition can change the
verdict. The rebuilt list L(B) would give f_omega(12B)-type growth if it were ever used as digits, but here the
halt comes first.

### Other n (not met by the real run; `ngrid.py`, b = 1..3, 3e8 steps; H = halts, R = still running)
- H for all b: n in {4, 5, 7, 8, 10, 12, 14, 15, 17, 20-23, 25-28, 31, 36, 38, 40}.
- R for all b: n in {1, 2, 3, 6, 9, 11, 13, 18, 19, 24, 29, 30, 32-34, 39}.
- Mixed: n = 0 (H at b = 3), 16 (H at b = 3), 35 and 37 (H at b = 1).
- The R cases are inner digit-list counters like n = 11 (n = 11 is the 4-digit B(5;[1]^5)). Their inner lists and
  rebuild shapes vary with n; I did not characterise them all.
- The earlier probe2 "T" entries at n = 11 were not runaways: the n = 11 inner counter takes about 2^^6 3 steps.
  probe2 also has a tape limit.

## 6. Relatives (question 4; `relcheck.py`, `relexh.py`, output `relcheck_out.txt`)
**Group 1 (same chain, same verdict).** All six pass every stage: blank -> K(1^11;1;2), rule grids, J_b inner start
for b = 1..6, e1 borrow. Inner-exhaustion halts were fitted over b = 0..60:

| machine (variable part) | inner-exhaustion halt (B = 1) | sigma |
|---|---|---|
| `0RI0LC ... 0RB0RE_---1LH` | 36b^2+636b+918 steps, 6b+71 ones | same as main |
| `0RI0LC ... ---0RE_---1LF` | 36b^2+630b+910, 6b+71 | same |
| `0RI0LC ... 1LF0RE_---0LG` | 36b^2+636b+918, 6b+71 | same |
| `0RI0LC ... 1RG0RE_---1LH` | 36b^2+630b+910, 6b+71 | same |
| `1RI0LC ... ---0RE_---0RF` | 36b^2+624b+902, 6b+72 | main + 1 |
| `1RI0LC ... 0RE0LG_---0RF` | 36b^2+630b+912, 6b+72 | main + 1 |

The differences are only in how the G0 step is emulated, plus one extra one at the end.

**Group 2 (mirrored E0: `..._0LI0LC_..._0RF---` and `..._1LI0LC_..._1RH---`): different path, also halts.**
- Every stage up to the inner exhaustion matches the main machine: blank -> K(1^11;1;2) at 8317 / 8405, rule grids
  with 0 mismatches, J_b inner start for b = 1..6, e1 borrow.
- J(0*,0,0,0;0;b) does not halt. A second-level counter runs, its borrow reaches the rebuilt list L(B), and L's
  zeros are rebuilt into groups `D4 D2 D7`.
- The machines halt when the last group is reached, with a score of about 17.1*(2^^13 3). Details are in section 9.

## 7. Reproduction (scratch dir `bb9_c7m12_1RB0RA_0RI0LC/`)
**Tools:**
- `tr9.exe` (`tr9.cpp`; build with MSYS2 g++): literal tracer. Modes: `geo F`, `every K`, `usage W`, `trans QS N`,
  `redge GAP N`, and `match WORDFILE`, which stops when the tape equals a word with the head in B on the right edge.
  Any other mode name means quiet.
  `tr9b/c/d/e.exe` and `tr9run*.exe` are copies of the same final build. Copies were needed because an exe
  cannot be rebuilt while it runs; the scripts refer to them by these names.
- `kword.py`: K words.
- `dconf.py`, `inner_start.py`, `exh_check.py`: build L, J and the inner words.
- `dtok.py`, `dshape.py`: D-token views of snapshots.

**Commands:**
- `python rulegrid.py outer|inner1|inner0 BOUTER MAXLEN MAXD MAXA MAXB` (set env `TM9=` for another machine).
- `python exh_scan.py 1 0 700 3`
- `python e2e.py`
- `python relcheck.py MACHINE`
- `python relexh.py MACHINES...`
- `python ngrid.py 0 40 1 3 300000000`

**Data:** `exh_scan_1.txt`, `exh_scan_3.txt`, `rulegrid_big.txt`, `relcheck_out.txt`, `ngrid_n0-40.tsv`.

`qs_from.py` starts Ligocki's Quick_Sim from an arbitrary tape. It was not useful here: at block size 2 it proved no
rules and ran about 10x slower than literal simulation.

## 8. Open questions
- Coq: the rules are the champion's (as in `BB8_champ35*.v`). A halting proof would need the rebuild lemma for
  symbolic b, the inner rules on the J template, and the exhaustion lemma. Doable, but low value, since this is not
  a record.
- Group 2 also halts (section 9). The token-level tools (`tr9` dshape/deadend/aevents/kcanon, `tok2word.py`) can be reused on other rebuilders.

## 9. Group 2 in depth (`..._0LI0LC_..._0RF---` = g, `..._1LI0LC_..._1RH---` = h)
Scratch: `bb9_c7m12_1RB0RA_0RI0LC/g2/`.

New tracer modes in `tr9.cpp`:
- `dshape N`: D-token view at right-edge visits, printed only when the shape changes.
- `deadend N`: E0 events other than the G0-emulation context; tags A = E entered from D1, B = entered from H0.
- `aevents N`: compact log of A-events, with WHOLE marking an exhaustion with only blanks to the left.
- `kcanon N`: token view of every configuration that ends in the K suffix `111001`.

`tok2word.py` turns a token view back into a tape word. It is exact: it reproduces a real snapshot bit for bit.

### 9.1 g and h are the same machine at the token level
- Both pass every stage of section 6: blank -> K(1^11;1;2), rule grids, J_b inner start, e1 borrow.
- From J_4(0*,0,0,0;0;0), the right-edge token histories of g and h are identical for 260k steps (111 snapshots,
  diff empty). That covers the second-level counter, the borrow into L and the start of the rebuild of L.
- Their outer-exhaustion halts are the same n, with step counts a few % apart.
- Everything below was measured on g.

### 9.2 What happens after the inner exhaustion (question 1)
Data are literal simulation with small parameters.
1. **Second-level counter.** `J_B(0*,0,0,0;0;c)` becomes `L(B) X' D(6c+5) D(49) T` (c = 0, 2, 6, and 126 via a = 6).
   - Here `X' = (10)^8 0 1111`, and T is a tail of `1^5 100` units.
   - Rule: `D(M) D(y) -> D(M-3) D(2y+4)`, i.e. a = (M-2)/3 = 2c+1 champion R1 steps with y + 4 doubling.
2. **Borrow into L(B).** When M reaches 2, the borrow walks left through X' and L(B)'s 12B - 2 zeros to L's
   leading digit D(7) (= 2). It becomes D(4) (= 1).
3. **Rebuild of L's zeros.** The zeros are not kept as zeros, as the champion's R3 would keep them.
   - About 13 are absorbed next to the borrowed digit: the prefix becomes `11 D(4) D(9) D(6) D(~y+10) D(14) D(10)`.
   - The rest are converted at **7 zeros per group** into groups `D(4) D(2) D(7)`.
   - Each conversion cycle is driven by an A-event at the left end of the right-hand tail list (9.3).
   - Measured group counts k: B = 3..14 give k = 1, 3, 5, 6, 8, 10, 11, 13, 15, 17, 18, 20, and B = 20 gives 30.
     For B = 6 mod 7 (B = 6, 13, 20) this is exactly k = (12B - 30)/7.
   - The end pattern depends on B mod 7. Examples: B = 3 and 10 end in `1 15`, B = 4 and 11 in `4 3 5 1`, B = 6 in `0 9`.
   - The real B is 6 mod 7. Reason: B + 2 = 2^(X-1) with X a power of 2 whose own exponent is even, so X - 1 = 0 mod 3.
     So the real run follows the B = 6 / B = 13 pattern.
4. **Merged counter.** A champion-type counter runs on `11 D4 D9 D6 D(..) D14 D10 (D4 D2 D7)^k <end> a acc`:
   a decreases by 3 per round, acc doubles (2y+4).
   - A synthetic probe in which the borrow reaches a group's D(2) (`... 4 2 7 4 2 1*7 ...`) passes it without
     halting (`4 2 7 2 4 6 ...`, then further counters).
   - So the merged list has the f_omega shape: about 1.7B digits (k ones, k twos, and k D(2) tokens).
   - But only its last group is ever used (9.5).

### 9.3 The exact halting condition
- E0 events come in two kinds:
  - **A**: E entered by `D1 = 1LE`. This is exactly the BB(7) champion's own halting move, when a borrow walks off
    the `11` prefix of a list. Here t[p+1] = 1 always.
  - **B**: E entered by `H0 = 0RE`. This is the G0 emulation; the anomaly is G0 over `0 0`.
- The main machine halts only at a B anomaly with t[p+3] = 0. That is its halt in section 3c, ctx 00.
- g and h ignore B anomalies. **They halt exactly at an A-event whose left neighbour cell is 1**: the walked-off
  `11` prefix is preceded by `1 0` instead of `0 0` or blank.
- What was observed:
  - The first exhaustion (blank on the left) passes.
  - Every A-event in the proxy runs had raw `... 1 0` on the left of the `11` prefix. For B = 6, c = 0 over 1.5e9
    steps: 11 A-events, all with left context `<1 0>`.
  - The halting cases have a D-token directly before `0 11`.

### 9.4 Halting data
- **Outer exhaustion grid** `K(0^n;0;b)` for g (`g2/degrid_g.tsv`, `g2/ngrid_g.tsv`; n <= 70, b <= 3 or 4,
  1e8-2e8 steps):
  - Halts for all b: n in {3, 8, 16, 19, 29, 34, 53}.
  - Halts for b = 1 only: n in {50, 52, 68}.
  - Extended to n = 71..110 at b = 1 (`g2/degrid_g_71_110.tsv`): only n = 110 halts within 1e8 steps.
  - Extended to n = 111..420 at b = 1, 3e7 steps (`g2/hgrid_g_111_420_b1.tsv`): 35 of 310 cells halt early.
    The halting n are irregular: 112, 118, 135, 148, 153, 168, ... , 405, 407.
  - Every other cell is still running at the step limit, inside long inner counters, so it is undecided.
  - probe2 had found only n = 16; it missed 19, 29, 34 because of its tape cap.
- **Proxy runs** from the inner exhaustion `J_B(0*,0,0,0;0;c)` (B = 1..8, c in {0, 1, 2, 6}, 2e10 steps each,
  `g2/proxy_g.txt`): **no halt** (32 of 32 runs reached 2e10 steps without halting). This covers the second-level counter, the borrow into L, and all
  seven B mod 7 classes of the rebuild of L.
- Rebuild of L for B = 1..14, c = 0, to 3e8 steps: no halt.

### 9.5 What happens after the conveyor: the last group and the halt (questions 2-3)
Real residue class: B = 6 (mod 7), so the end pattern is `0 9`. Literal traces for B = 6 and B = 13, with c = 0, 1, 2.
1. **The merged counter does not depend on y, c or B, apart from k and one prefix token.** The merged list is
   `11 D4 D9 D6 D(Q) D14 D10 (D4 D2 D7)^k D0 D9 | a | acc`.
   - The only y-dependent token is `Q = 212*4^c - 2`: 210, 846, 3390 for c = 0, 1, 2. In the real run c = b_f.
   - Everything right of it is identical for c = 0, 1, 2, up to step 2.8e8 at least
     (`... 4 2 2 6133 10 12282` in all three).
2. Champion R1/R2 consume the a-digit and `0 9`.
   - The borrow then reaches the last group's D(7). The block `D7 D0 D0 D0` becomes `D2 D(6139) D1`: the D(7) turns
     into a second D(2), and a new digit D(6139) (d = 2046) appears.
   - Configuration `P 4 2 2 6139 1 2` (a = 0, b = 0): step 5.46e7 for B = 6, 5.84e7 for B = 13. Here P is the
     prefix plus the first k - 1 groups.
3. D(6139) is an ordinary 3d+1 digit. Champion rules turn `(2046; 0; 0)` into `(0; 0; b_last)` with
   `b_last = g^2046(0)`, where `g(x) = 2^(2x+3) - 2` (g(0) = 6, g(6) = 2^15 - 2; checked against the trace's a = 2, 14).
4. **The last group's `4 2 2` block and the halt.** The borrow walks through `D1 D1` and reaches the two D(2) tokens.
   The block `D4 D2 D2` plus the zeros is absorbed into `11 (10)^Y` with **Y = 48*4^b - 9** (b = 0..4 give 39, 183,
   759, 3063, 12279). The previous group's D(7) drops to D(3).
   - The `11` sublist's exhaustion is then an A-event with a 1 on its left (ctx 11): **HALT**.
   - Literal runs:
     - from the real configurations of step 2 with D(6139) replaced by its exhausted D(1), and acc D(X) for
       X = 2, 5, 8: B = 6 and B = 13, both g and h;
     - from synthetic prefixes (k - 1 = 0, 5 and 17 groups) for X = 2..14.
     All halt the same way, with halting time about 4^b.
   - The halt is local: it does not depend on how many groups lie to the left.
5. **Ones at the halt** (g), fitted on B = 6 and 13 and X = 2, 5, 8:
   - `ones = Y + 20k + Q + 79`. h has one more.
   - With k = (12B - 30)/7, 2B + 4 = 2^^13 3, Q = 212*4^b_f - 2 and Y = 48*4^b_last - 9:
     **sigma = (120*(2^^13 3) - 1080)/7 + 212*4^b_f + 48*4^b_last + 68**, plus 1 if the halting transition counts
     as writing a 1.
   - b_f = (2^^6 3 - 4)/2. b_last is a tower of height about 2048.
   - Both 4^b terms are negligible next to 2^^13 3, so **sigma is about 17.1*(2^^13 3)**.

### 9.6 Verdict for group 2
- **Both g and h HALT**: in the first cycle, at the exhaustion of the last group of the rebuilt list. Confidence:
  strong evidence.
- **Score about 17.1*(2^^13 3).** That is about 5.7x the BB(7) champion and 1.4x the main machine's 12*(2^^13 3).
  It is far below the 8-state record and below f_omega(f_9(2)) by an unimaginable margin. **No record.**
- Why the f_omega shape fails: the rebuild over L(B) does make about 1.7B digits. But the groups contain D(2)
  tokens, and the first `D4 D2 D2` block the borrow reaches turns into an exhausted `11` sublist sitting right behind
  a D-token. g and h halt exactly there (I1 undefined). The other k - 1 groups and the prefix are never touched.
- The A-event/D(2) mechanism also explains the earlier data:
  - the outer-grid halts (n in {3, 8, 16, 19, 29, 34, 53, ...});
  - the probe2 n = 16 halt.
- Assumptions this verdict rests on:
  - The absorption-and-halt step (4) holds for astronomically large b. It was checked for b <= 4; the halting time
    and Y are exact 4^b laws.
  - The formulas for k, Q and the ones count hold beyond the 2-3 values used to fit each of them.
  - The merged-counter phase is the same for c = b_f as for c = 0..2. Literally checked: everything right of the
    prefix token is identical for c = 0, 1, 2.

Data: `g2/endtoks_B6.txt`, `g2/endtoks_B13.txt` (real end configurations); `g2/merge_B6_c{0,1,2}.txt`;
`g2/dshape_B6c0_5e9.txt`; `g2/proxy_g.txt`; `g2/wipe_g.txt`.
Scripts: `endhalt.py`, `tprobe.py`, `wipe.py`, `kprobe.sh`, `kseq.py`, `whole.py`, `hgrid.py`.

## 10. Thirteen new c7m12 variants (full run, 57,947 holdouts): quick classification
Scratch: `bb9_c7m12_1RB0RA_0RI0LC/v13/`.
- `classify.py MACHINE` runs four checks:
  - blank -> K(1^11;1;2);
  - K(0^11;0;b) -> J_b;
  - the inner exhaustion J_1(0*,0,0,0;0;c), against the main machine's halt law;
  - the right-edge token history from J_6(0*,0,0,0;0;0), against group 2 (g).
  It also runs group 2's real end configuration (from section 9).
- `fprobe.sh`, `lchain.py` (rule-chain check of R1-R3 in any prefix/tail context) and `lam_check.py` are used for
  the machines that differ.
- Variable part shown as `E0 ... H_I`.

| # | machine (E0 / H / I) | verdict | reason |
|---|---|---|---|
| 1 | `0LG0LC ... 0RI0RE_---1LF` | group 1, halts | inner exhaustion halts exactly like the main machine (920/71, 1592/77, ...) |
| 2 | `0LG0LC ... 1RI0RE_---0RF` | group 1, halts | inner exhaustion like the `1RI` group-1 relatives (912/72, ...): sigma = main + 1 |
| 3 | `0LI0LC ... ---0RE_0RF---` | group 2, halts | token history = g (202/202), end configuration halts with g's ones |
| 4 | `0LI0LC ... ---1RE_0RF0RE` | group 1, halts | inner exhaustion halts (1385/69, 2057/75, ...): sigma = main - 2 |
| 5 | `0LI0LC ... 0LG0RE_1RH---` | group 2, halts | token history = g, end halts identically |
| 6 | `0LI0LC ... 0RB0RE_0RH---` | differs, no record | see 10.2 |
| 7 | `0LI0LC ... 0RF0RE_0LG---` | differs, halts early, no record | see 10.3 |
| 8 | `0LI0LC ... 0RG0RE_1LH---` | differs, halts early, no record | see 10.3 |
| 9 | `0LI0LC ... 1RG0RE_0RH---` | group 2, halts | token history = g, end halts identically |
| 10 | `0LI0LC ... 1RI0RE_0LG---` | same as #7 at token level | see 10.3 |
| 11 | `1LI0LC ... 0RG0RE_0LH---` | **RECORD CANDIDATE** | see 10.1 |
| 12 | `1LI0LC ... 0RH0RE_0LH---` | **RECORD CANDIDATE** (twin of #11) | see 10.1 |
| 13 | `0LI0LC ... ---1RE_0RB0RI` (R4-SOME) | differs, no record | see 10.4 |

Transitions that never fire: #1-#5 and #9 differ from the main machine or from g only in how the G0 step is
emulated (H1 = 0RE short-cuts H1 = 0LG; E0 = 0LG reroutes through G0/H0) and in the H0/I transitions used at the
anomaly. Their token histories coincide exactly.

### 10.1 #11 and #12 (`1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---` and `..._0RH0RE_0LH---`): possible new BB(9) champion
1. **The champion phase is unchanged.**
   - blank -> K(1^11;1;2) at step 8317, the same as the main machine.
   - Outer rule grid: 580 + 9,513 probes, 0 mismatches.
   - No anomaly (A- or B-type E0 event) in the first 2e9 steps from the blank tape.
   - So the first exhaustion is K(0^11; 0; B) with 2B + 4 = 2^^13 3.
2. **The rebuild makes a list of ONES.**
   - `K(0^11;0;b) -> Lambda(b) = 11 D4 D21 D4 D17 D4^(12b-12) D1 | a = D34 (a = 11) | acc = D44 (b = 14) | tail`.
   - Literal match of the whole word for b = 1..6, 14, 30, 62, in 4356 b^2 + 13254 b + 28278 steps.
   - #12 is identical, with the same step counts for b = 1..6 and 14.
   - So the rebuilt list has 12B - 12 digits of value 1 plus four prefix tokens, in place of L(B)'s 12B - 2 zeros.
3. **That list is run by the champion rules.**
   - `lchain.py` on the prefix `11 D4 D21 D4 D17` with digits (1,1,1,0), a = 1, b = 2 extracted 17 consecutive
     canonical configurations, all exactly R1/R2/R3.
   - Further chains, all exact R1/R2/R3: (1^6, 0; 0; 0) 15 configurations; (1, 0^5; 0; 0) 19, the R3 cascade;
     the real start (1^12, 0; 11; 14) 7.
   - The prefix digit D17 behaves as a digit of value 5 (3e+2 encoding): `17 -> 14` with the standard refill
     `4 7 1*k`.
   - So the 12B - 12 ones are consumed Ackermann-style before anything else happens.
   - By the closed form for B(5;[1]^k) (2 b_f + 4 = 2^^(k+1) 3), the accumulator when they are used up is
     **b >= 2^^(12B - 13) 3 / 2**.
4. **It then halts.** Probes of the prefix phase and of the fully exhausted list all end in an A-event with a 1 on
   the left (I1 undefined): `0*2 3 [E] 0*2 (10)^Y ...`, the leftmost D4 dropped to D3.
   - Probes: `[4 21 1 2 1*4]`, `[4 0 1 2 1*4]`, `[4 3 1 2 1*4]`, `[1 0 1 2 1*m]` for m = 1, 13 and X = 2, 5, 8, 11,
     in both #11 and #12.
   - The halting tape holds `(10)^(2X+1)`, where X = 3b + 2 is the final accumulator. So **sigma >= about 6b**.
5. **Score: sigma > 2^^(12B - 13) 3 = 2^^(6*(2^^13 3) - 37) 3**, i.e. f_omega(about 6*(2^^13 3)).
   - **That is far above f_omega(f_9(2))**, because 6*(2^^13 3) >> f_9(2) + 2.
   - Confidence: strong evidence for the structure (every stage checked literally on small parameters). It is not
     proved. The end-of-list halt is checked only for small accumulators.
   - **Recommended next step: a dedicated Opus/Coq effort on #11.** It needs:
     - the champion rules;
     - the rebuild lemma K(0^11;0;b) -> Lambda(b);
     - the rules on Lambda (champion rules with the D17/D21 prefix tokens);
     - the end-of-list halt;
     - a lower bound in the style of `BB8_champ35_exact.v`.

### 10.2 #6 (`..._0RB0RE_0RH---`): no record
- Its rebuild and inner counter are the main machine's. At the inner exhaustion it builds a different
  second-level counter, borrows into L(B), and turns L's zeros into `1 00` units, not g's 7-zero groups.
- Each time its small inner list `D8 D4 D4 D1` (2*, 1, 1, 0) runs out, it consumes one unit and builds a new
  `D(2X+4) 0 0 0` list. Its leading digit carries the accumulator X (checked: X = 62 gives D128).
- So each of the ~12B units adds a fixed number of arrow levels, about x -> 2^^5 x. After 12B units that is about
  2^^6 (12B). This is a bounded number of arrows above B, nowhere near f_omega(f_9(2)).
- Halting was not determined. There was no halt in 3e8 steps after an inner-list exhaustion.

### 10.3 #7, #10 (token-identical) and #8: halt early, no record
- **#7 / #10.** The rebuild gives `L'(B) = 11 D7 D1^(12B-1) D0 (10)^5 0` plus a separate inner list
  `11 D5 D1 D3 D4^7 | a`. When the inner list is exhausted, the machine halts with ctx 11 within 358 steps (probe).
  sigma is about ones(L'(B)), about 24B: main-machine scale.
- **#8.** The rebuild gives one list `11 D7 D1^(12B-3) D0 D5 D5 D98 D1 | a | acc`. Once D5 D5 D98 are used up,
  the borrow reaches the D0, and the machine halts with ctx 11 (probe: X = 2 at 7129 steps, X = 5 at 69677). L's
  zeros are never used, so sigma is about 24B.

### 10.4 #13 (R4-SOME, `..._---1RE_0RB0RI`): no record
- The rebuild gives a short list `D0 D1 D(6b-12) | a = D1372 | acc`. b enters a single digit's value, not the list
  length.
- At its exhaustion it has ctx-11 events, but I1 = 0RI is defined, so it continues. It rebuilds a run of zeros
  about proportional to the accumulator, consumed two zeros per doubling (`(10)^11, 31, 71, 151, ...`).
- That is exponential growth per cycle, with no digit-list recursion. Halting was not determined, and the halting
  transition H0 was not reached in the probes.
- It cannot approach f_omega-scale without a recursion not seen here.
