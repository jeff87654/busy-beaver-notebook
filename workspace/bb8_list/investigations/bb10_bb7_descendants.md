# BB(10) from the BB(7) champion: triage of the rec14 and c35m14 descendants

Agent inv-bb10-bb7desc, 2026-10-07. Scratch and tools: `bb8_list/investigations/bb10_bb7_descendants/`.

## Verdict
- **No record candidate.** No machine in either subtree was found that halts after a rebuild cascade at omega-level 2 or
  higher. In the rec14 subtree that would be two nested full rebuild-and-clear cycles, the second list's length growing
  with the first cycle's accumulator. In the c35m14 subtree it would be one full rebuild of the 35-digit start's
  exhausted list followed by a halt.
- **Record-shaped, but never halting.** Both subtrees contain machines with exactly the f_(omega+1) shape: clean,
  ever-growing rebuild cycles (the "loopers", section 4.3). Their stage maps have no residue dependence, so they never
  halt (strong evidence, no Coq).
  - Two loopers are in c35m14, starting from the BB(8) record's 35-digit list.
  - A variant whose rebuild halted at the 2nd or 3rd exhaustion would beat f_omega^2(25) by a wide margin. None was
    found.
- **Halting relatives of the loopers (section 10): none found.**
  - Searched: every radius-2 change and a targeted radius-3 set of the looper parents C28, C29, C32, the rec14_0RH
    looper and c35a/c35b. 2,642 + 796 + 143 root-changing variants keep the start; for C28, 87,761 radius-3
    variants keep it.
  - Result: the variants keep looping, halt at a level-0 event, or turn chaotic. The chaotic ones have outcomes
    that depend non-periodically on the huge accumulator and cannot be proved.
  - Structural reason: from the second exhaustion on, the C28-type cycles differ only in n mod 8. The c35 E_1
    handler visits no tape context that does not also occur elsewhere.
- **The best halting structure found** is one rec14 class of 6 machines, two full cycles at omega-level 1:
  `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_---0RE_1LJ0LG_0RJ1RI`.
  - The score is about f_{12B+1}(f_{12B}(...)), one FGH index above our BB(9) record's level.
  - It is far below f_omega(f_omega(25)) (section 4.2).
- **Confidence.** Strong evidence for the classes the follower completed. Each stage is a literal simulation at
  representatives in the real residue class, fitted affinely and validated at a further real-class point. Each jump is
  an abstract R1-R3 run after a literal rule check in front of the actual tail. No Coq.
- **Coverage.**
  - rec14: 2,174 rebuilders (rounds 1 and 2) in 324 behaviour classes. 614 machines were followed individually; 1,560
    are classified only through their class representative.
  - c35m14: all 15,166 holdouts were screened. 397 reproduce the BB(8) record's run:
    - 251 have E0 undefined, so they halt at the first exhaustion like the record;
    - all 146 with E0 defined were followed.
- **Open.**
  - The UNCLEAR classes (about 640 rec14 machines, mostly g-type conveyors and non-champion processes after the first
    exhaustion; section 4.5).
  - The 1,560 class-inferred machines. Members can diverge late (section 3). The member pass can be resumed:
    `python batch.py members.tsv results_mem.tsv 4 12 150000000`.

## 1. The bar (FGH)
- The BB(10) champion is listed as `> f_omega^2(25)` = f_omega(f_omega(25)) = f_F(F), where F = f_25(25) > 2^(24 arrows) 25.
- The rec14 start: the first exhaustion is K(0^11; 0; B) with 2B+4 = T = 2^^13 3 (13 arrows).
- One full cycle (a list of length about cB cleared by the champion rules) gives about f_{cB}(...) = f_omega-level with
  index cB, roughly 6T.
  - Since 6T << F, any bounded composition of functions of index 12B + O(1) stays below f_F(F).
  - The reason: f_F(F) >= f_{12B+k+1}(F) = f_{12B+k}^F(F).
  - So a halting machine beats the bar only if a later cycle's list length is itself an omega-level-1 accumulator.
    That is omega-level >= 2: f_omega(f_omega(cB)).
  - This holds even when a run makes many same-level cycles. A fixed-length list cleared R times gives
    f_{12B+O(1)}(R) with R < f_{12B+O(1)}^3(12B). That is below f_F(F).
- c35m14 (route b): the first exhaustion is K(0^35; 0; B') with 2B'+4 = 2^^37 3 > F. So one full cycle over a list of
  length about 12B' already beats the bar.
- The follower records an **omega-level** for every accumulator.
  - The level of a new accumulator is the maximum level of its inputs.
  - Add 1 when the cleared list's length is huge; that is, when the length involves a huge parameter of level L,
    the new accumulator gets level L+1.
  - Record: halts at level >= 2 (rec14), or level >= 1 from the 35-digit start (c35m14).

## 2. Method
**`hyb10.cpp`, the literal simulator.** It works for any number of states (up to 16) and reports "canonical
configurations": head in a given state, reading 0, right of all 1s. Each is shown as D-token items
(D(m) = (10)^m 1), with junk runs.
- It detects a champion phase automatically:
  - Two configurations with the same suffix shape that differ only in two adjacent tokens (a, r) as
    a: m+3 -> m, r -> 2r + 6 - e. This fixes the tail and the accumulator offset e.
  - Then >= 4 consecutive verified R1/R2/R3 transitions (R2: a := 2r + 7 - 2e, r := e).
- Other features:
  - parsing is incremental and amortised;
  - a prelock mode for rule checks;
  - a hash mode for behaviour signatures.

**`numres.py`, residue arithmetic.** Huge numbers are kept as residues modulo Q = 2^10 3^8 5^2 7 11 13 17 19.
- Q is lambda-closed: lambda(Q) | Q, so 2^x mod Q follows from x mod Q.
- The universal residue tau of tower-type accumulators is the fixed point of H_1 on residues.
- It reproduces B = 1 (mod 5), 6 (mod 7), 6 (mod 9), 14 (mod 16), 8 (mod 11) and 6 (mod 13).

**`follow2.py`, the stage follower.**
- Start: K(0^n; 0; b) with b = B (n = 11; or n = 35 with the BB(8) record's dlscan2 template, canonical state G).
- Each stage is simulated literally at representative parameter values:
  - Detect the period: 22 consecutive values per parameter, the smallest class period on which the outcome shape and
    every field are affine. Larger periods (multiples of the shape period) are tried with direct samples.
  - Fit the real residue class (4 points per parameter, plus a diagonal).
  - Validate at a further point of the real class modulo lcm(period, 12).
  - Item lists are compressed into repeated blocks, so lists and tails that grow with a parameter keep their shape;
    junk is expanded into runs.
- If no K-moment is found in the input's state, the other canonical states are tried.
- Rule check: R1, R2 and R3 are checked literally in front of the phase's actual tail before every jump.
- Jump: the champion process runs abstractly to the next event, using:
  - closed forms H_0^u(r) = (r + 6 - e) 2^u - (6 - e) and H_d(r) = H_{d-1}^{(2r+6-2e)/3}(e);
  - the universal fixed point for deep or huge iterations;
  - blocks of tokens with huge repeat counts.
  The event is the borrow reaching D0/D2/D3, junk or the list's left end, or the a-token bottoming out.
- Loop detection: three identical stage-input shapes, with every constant field equal.

**Regression checks.**
- The padded BB(9) record `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---`:
  - the follower finds the period 5 automatically;
  - it returns ones = 2 R1 + (108/5) B + 282/5;
  - this equals the machine-checked score_exact, 6 b' + 108 floor(B/5) + 82 with R1 = 3b' + 2.
- 9-state group 1 (`..._0RI0LC_..._0RE0LG_---1LF`): ones = 2 R1 + 24 b + 43. This equals the report's
  24B + 6 b_f + 47 with R1 = 3 b_f + 2.
- 9-state group 2 (g): the follower reaches the conveyor stage, and the conveyor stage stays UNCLEAR. That is the right
  outcome: its end needs the exponential 4^b terms and the last-group analysis of the 9-state report.

**Coverage.**
- rec14 rebuilders, rounds 1 and 2:
  - every NOBOUNDARY, R4-SOME and HALT? row of the watcher;
  - plus the round-1 bign rows HALTS-AT-11 with n11 = HTTTTTTT/HHTTTTTT.
- They were deduplicated by behaviour signature: a hash of the first 3,000 canonical configurations from
  K(0^11;0;b), b = 6, 7, 13.
- One representative per class was followed. Class members were then followed with the representative's fitted stage
  results reused when they agree at two points (`--ref`); this is a partial pass, see the tally.
- c35m14: all 15,175 holdouts were screened (`c35screen.py`, 3e6 steps from blank).
  - Those reproducing the BB(8) record's champion run (list 4*34 1 at 3e6 steps) were followed with the record's
    template.

## 3. Tallies (generated by `tally.py`)
```
rec14 rebuilders (round 1 + round 2): 2174 machines, 324 behaviour classes
  GROUP-1-LIKE                                           734   (own follower run: 251)
  CHAMPION-LIKE                                          587   (own follower run: 48)
  UNCLEAR-T                                              389   (own follower run: 148)
  UNCLEAR-FAIL                                           181   (own follower run: 88)
  INFINITE-REBUILDS (loop)                               116   (own follower run: 5)
  UNCLEAR-MAXSTAGES                                       43   (own follower run: 28)
  NON-HALT (runaway, tape > 4e6 cells)                    38   (own follower run: 19)
  INFINITE-REBUILDS? (T at omega-level >= 2)              38   (own follower run: 7)
  UNCLEAR-RULES                                           12   (own follower run: 5)
  UNCLEAR-CRASH                                           11   (own follower run: 9)
  UNCLEAR-LOOP                                             9   (own follower run: 9)
  ONE-REBUILD (omega-level 1, 2 full cycle(s))             6   (own follower run: 1)
  UNCLEAR-T after 3 full cycle(s)                          2   (own follower run: 1)
  UNCLEAR-ORDER (fit subtracts accumulators)               2   (own follower run: 2)
  ONE-REBUILD (omega-level 1, 1 full cycle(s))             2   (own follower run: 2)
  UNCLEAR-MAXSTAGES after 2 full cycle(s)                  2   (own follower run: 2)
  UNCLEAR-T after 1 full cycle(s)                          1   (own follower run: 1)
  UNCLEAR-MAXSTAGES after 4 full cycle(s)                  1   (own follower run: 1)
  machines with their own follower run: 627; inferred from their class: 1547
by watcher/bign tag:
  CAND: GROUP-1-LIKE=229, UNCLEAR-T=10, UNCLEAR-FAIL=9, UNCLEAR-CRASH=2, NON-HALT (runaway, tape > 4e6 cells)=2, UNCLEAR-MAXSTAGES=1
  H11part: GROUP-1-LIKE=9, UNCLEAR-T=7, UNCLEAR-FAIL=2
  HALT?: UNCLEAR-T=1
  NOB2: CHAMPION-LIKE=578, GROUP-1-LIKE=466, UNCLEAR-T=223, UNCLEAR-FAIL=110, INFINITE-REBUILDS (loop)=94, UNCLEAR-MAXSTAGES=34, INFINITE-REBUILDS? (T at omega-level >= 2)=33, NON-HALT (runaway, tape > 4e6 cells)=29, UNCLEAR-RULES=9, UNCLEAR-CRASH=6, ONE-REBUILD (omega-level 1, 2 full cycle(s))=6, ONE-REBUILD (omega-level 1, 1 full cycle(s))=2, UNCLEAR-MAXSTAGES after 2 full cycle(s)=2, UNCLEAR-T after 1 full cycle(s)=1, UNCLEAR-LOOP=1, UNCLEAR-MAXSTAGES after 4 full cycle(s)=1, UNCLEAR-ORDER (fit subtracts accumulators)=1
  NOHALT: UNCLEAR-T=147, UNCLEAR-FAIL=46, GROUP-1-LIKE=30, INFINITE-REBUILDS (loop)=22, UNCLEAR-LOOP=8, UNCLEAR-MAXSTAGES=8, NON-HALT (runaway, tape > 4e6 cells)=6, INFINITE-REBUILDS? (T at omega-level >= 2)=5, CHAMPION-LIKE=4, UNCLEAR-CRASH=3, UNCLEAR-RULES=3, UNCLEAR-T after 3 full cycle(s)=2, UNCLEAR-ORDER (fit subtracts accumulators)=1
  R4-SOME: UNCLEAR-FAIL=14, CHAMPION-LIKE=5, NON-HALT (runaway, tape > 4e6 cells)=1, UNCLEAR-T=1
notable (own runs):
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---1RJ_0LD1RJ  RESULT UNCLEAR-T stages=9 full_cycles=6 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', True), ('J', 'block', True), (
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_1RI0RE_0LJ0RI_1LD---  RESULT UNCLEAR-T stages=9 full_cycles=6 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', True), ('J', 'block', True), (
  UNCLEAR-T after 3 full cycle(s)          1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_---0RE_0RJ0RC_1RJ0RD  RESULT UNCLEAR-T stages=10 full_cycles=3 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', False), ('J', 'block', False)
  INFINITE-REBUILDS (loop)                 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---0RJ_0LB0RJ  RESULT LOOP stages=3 full_cycles=3 history=[('J', 'block', True), ('J', 'block', True), ('J', 'block', True), ('LOOP', 2)]
  INFINITE-REBUILDS (loop)                 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0LB0RE_---0LJ_0RJ0RH  RESULT LOOP stages=3 full_cycles=3 history=[('J', 'block', True), ('J', 'block', True), ('J', 'block', True), ('LOOP', 2)]
  INFINITE-REBUILDS (loop)                 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_---0RE_0LB0LJ_0RJ0RI  RESULT LOOP stages=3 full_cycles=3 history=[('J', 'block', True), ('J', 'block', True), ('J', 'block', True), ('LOOP', 2)]
  INFINITE-REBUILDS (loop)                 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_---0RE_0LD0RJ_0LB1RI  RESULT LOOP stages=3 full_cycles=3 history=[('J', 'block', True), ('J', 'block', True), ('J', 'block', True), ('LOOP', 2)]
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0LJ0RE_---0RJ_1LE0LF  RESULT UNCLEAR-T stages=9 full_cycles=6 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', True), ('J', 'block', True), (
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_---0RE_1RB0LJ_1RJ0RI  RESULT UNCLEAR-T stages=6 full_cycles=4 level=2 history=[('J', 'block', False), ('J', 'block', True), ('J', 'block', True), ('J', 'block', T
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_---0RE_1LJ1RJ_0RC0LH  RESULT UNCLEAR-T stages=9 full_cycles=6 level=2 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', True), ('J', 'block', 
  UNCLEAR-T after 1 full cycle(s)          1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_---0RE_0RJ0LJ_0RC0RI  RESULT UNCLEAR-T stages=6 full_cycles=1 level=1 history=[('J', 'block', False), ('J', 'a-block', False), ('J', 'block', False), ('J', 'block
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_1LJ0RE_---0RJ_0RC0RH  RESULT UNCLEAR-T stages=9 full_cycles=6 level=2 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', True), ('J', 'block', 
  ONE-REBUILD (omega-level 1, 2 full cycle(s)) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_---0RE_1LJ0LG_0RJ1RI  RESULT HALT stages=3 full_cycles=2 level=1 history=[('J', 'block', True), ('J', 'block', True), ('H', '2*R2+24*b+54')] ones=2*R2+24*b+54
  UNCLEAR-MAXSTAGES after 4 full cycle(s)  1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RJ0RE_1LH0LG_---1RI  RESULT MAXSTAGES stages=12 full_cycles=4 level=1 history=[('J', 'a-block', False), ('J', 'block', False), ('J', 'block', False), ('J', 'bloc
  INFINITE-REBUILDS (loop)                 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_0RH0RF_0LJ0RE_---0RJ_1LG0LF  RESULT LOOP stages=3 full_cycles=3 level=3 history=[('J', 'block', True), ('J', 'block', True), ('J', 'block', True), ('LOOP', 2)]
  UNCLEAR-MAXSTAGES after 2 full cycle(s)  1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_1RJ0RE_0LG1LI_---0RI  RESULT MAXSTAGES stages=12 full_cycles=2 level=1 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', False), ('J', 'block'
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_0RH0RF_---0RE_0LJ0LI_0RE0RC  RESULT UNCLEAR-T stages=7 full_cycles=2 level=2 history=[('J', 'a-block', False), ('J', 'a-block', False), ('J', 'block', False), ('J', 'a-b
  UNCLEAR-MAXSTAGES after 2 full cycle(s)  1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_0RH0RF_0RI0RE_0RC0LJ_---0LH  RESULT MAXSTAGES stages=12 full_cycles=2 level=1 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', False), ('J', 'block'
  INFINITE-REBUILDS? (T at omega-level >= 2) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_0RH0RF_1RB0RE_---0RJ_1RG0LJ  RESULT UNCLEAR-T stages=12 full_cycles=8 level=2 history=[('J', 'block', False), ('J', 'block', False), ('J', 'block', False), ('J', 'block'
  ONE-REBUILD (omega-level 1, 1 full cycle(s)) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---_------  RESULT HALT stages=2 full_cycles=1 level=1 history=[('J', 'block', True), ('H', '2*R1+108/5*b+282/5')] ones=2*R1+108/5*b+282/5
  ONE-REBUILD (omega-level 1, 1 full cycle(s)) 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RH0RE_0LH---_------  RESULT HALT stages=2 full_cycles=1 level=1 history=[('J', 'block', True), ('H', '2*R1+108/5*b+282/5')] ones=2*R1+108/5*b+282/5
c35m14: 15166 holdouts screened; 397 reproduce the BB(8) record run; 146 of them have E0 defined
  UNCLEAR-MAXSTAGES                                    60
  CHAMPION-LIKE 24*b+106                               37
  CHAMPION-LIKE 24*b+107                               16
  CHAMPION-LIKE 24*b+105                               12
  UNCLEAR-T                                            4
  GROUP-1-LIKE 2*R2+24*b+104                           3
  CHAMPION-LIKE 24*b+102                               2
  CHAMPION-LIKE 20*b+69                                1
  UNCLEAR-MAXSTAGES after 6 full cycle(s)              1
  GROUP-1-LIKE 2*R1+2*R4+2*R5+24*b+82                  1
  CHAMPION-LIKE 24*b+67                                1
  CHAMPION-LIKE 24*b+66                                1
  CHAMPION-LIKE 24*b+68                                1
  GROUP-1-LIKE 2*R2+24*b+103                           1
  NON-HALT (runaway, tape > 4e6 cells)                 1
  INFINITE-REBUILDS? (MAXSTAGES at omega-level >= 2)   1
  CHAMPION-LIKE 108/5*b+492/5                          1
  UNCLEAR-FAIL                                         1
  CHAMPION-LIKE 108/5*b+592/5                          1
```
- "[by class]" verdicts are inferred from the class representative. Members share the first 3,000 canonical
  configurations, which covers the first rebuild and the start of the first champion phase. Members can still differ
  at later events: group 1 and group 2 of the 9-state study share their early history.
- The members pass checks this per stage.
  - Among the members followed individually, about 1 in 4 of the GROUP-1-LIKE classes diverged later.
  - All of those diverged into UNCLEAR outcomes: g-type conveyors, unary loops over L(B), T. None diverged into a full
    cycle.
  - So the "[by class]" GROUP-1-LIKE counts are upper bounds on the true GROUP-1-LIKE counts. The NOT-RUN members and
    the remaining "[by class]" verdicts are the main coverage gap.

## 4. The classes
### 4.1 CHAMPION-LIKE and GROUP-1-LIKE (halting, omega-level 0)
- CHAMPION-LIKE: the machine halts during the first literal stage after K(0^11;0;B). The ones count is affine in B
  (e.g. 24 b + 50, 3 b + 34, 12 b + 56), about c*T.
- GROUP-1-LIKE: the first rebuild builds L(B) = 11 D7 D1^(12B-2) D0 plus a small inner list. The inner champion
  counter runs; the machine halts at or shortly after the inner exhaustion.
  - Typical ones: 2 R1 + 24 b + c with c in 41..50. R1 is the inner counter's tower-type accumulator, e.g. 2 b_f + 4
    = 2^^6 3 for B(5;[1]^5).
  - About 12 T plus a 6-arrow tower.
- Both are far below the bar.

### 4.2 ONE-REBUILD (omega-level 1)
- `..._1LI0LC_..._---0RE_1LJ0LG_0RJ1RI` and its class (6 machines, round 2) is the best halting structure found.
  - The first rebuild gives the record-like list [4, 9, 4, 14, 4, 24, 4^(12B-18), 1 | 40 | 8].
  - Full cycle 1 clears the 12B-18 ones and stops at D24 -> D3.
  - The D3 event turns D3 into D0 + D(2 R1) and rebuilds the zeros as ones (12B-19).
  - Full cycle 2 clears D(2R1) and the ones. The halt comes at the D0 event, with ones = 2 R2 + 24 b + 54.
- Both cleared lists have length about 12B, so both cycles are omega-level 1.
  - R2 is about H_{12B}^{2R1/3}(...), about f_{12B+1}(R1), with R1 about f_{12B}(...).
  - That is one FGH index above our BB(9) record's level, f_omega(about 6T) (which, being a 9-state machine, it does
    not affect). It is far below f_F(F).
- The padded BB(9) record and its twin are themselves rec14 holdouts (J unused, I1 undefined).
  - TNF enumeration branches only transitions reached within its step budget. So no 10-state extension of the record
    through I1 exists in rec14.

### 4.3 INFINITE REBUILDS (record shape, no halt)
**rec14, 116 machines in LOOP classes plus 38 more followed to omega-level >= 2** (example
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---0RJ_0LB0RJ`; one class alone has 107 members).
- Stage map (fitted with period 1 in every parameter, validated):
  K(0^n; 0; R) -> [11, D4^(n+4R-6), D1 | a=37 | r=20] -> clear (full) -> K(0^(n+4R-5); 0; R').
- In the follower: n = 12B+14, then 4R1+12B+9, then 4R1+4R2+12B+4, ...
- The omega-level rises by 1 per cycle. The LOOP detector fires after 3 cycles.
- bign grid: K at every n in 11..49 for all 88 n=11-clean rebuilders of rounds 1 and 2 (0 "CANDIDATE" rows). No n
  class halts.

**rec14, n -> n + 4R loops with 2- and 3-stage cycles.**
- Examples:
  - `..._0LG0LC_..._0RI0RE_---1RJ_0LD1RJ`: the cycle [D(2R-1), 1^(n-1)] -> clear -> [D3, 0^n] -> [D0, D(2R'), 1^(n-2)]
    -> clear -> [D0, 0^n] -> [11, 1^(n+4R''-5)] -> clear.
  - `..._0RI0LC_..._---0RE_1RB0LJ_1RJ0RI`: a 2-stage cycle.
- Each was followed for 4-6 full cycles to omega-level >= 2. The follower then stops at T, because the representatives
  of a 4R-length rebuild are slow to simulate. No halt.

**c35m14, 2 machines** (listed in the tally as one "INFINITE-REBUILDS?" and one "MAXSTAGES after 6 full cycles"; the
second is a run made before the level was recorded).
- Example: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LB0LC_1RG1LD_0RI0RH_1RG1LF_0LB0RJ_0LE---`. From the BB(8) record's
  exhaustion K(0^35;0;B') it goes:
  [D5, D4^(12B'+45), D1 | 37 | 18] -> clear (full) -> [D2, 0^(12B'+46)] -> [D(2R+4), D4^(12B'+44)] -> clear (full)
  -> [0^(12B'+46)] -> [D5, D4^(4R+12B'+56)] -> ...
- The other is `..._1LJ0LC_..._0LI0RH_1RG1LF_0RC1RE_---1LI`, with the same pattern and D8 in place of D5.
- These reached omega-level 3 within 6 stages and never halt.
- A variant that halted after the first full cycle would be a route-(b) record, f_omega(12B'). One halting after the
  second would beat even that.

### 4.4 c35m14
**Champion-like.**
- 251 record-like holdouts have E0 undefined. E0 is only reached at the first exhaustion, so they halt there with the
  BB(8) record's score.
- About 75 of the 146 with E0 defined halt there too, with ones = 24 b + 66..107, 20 b + 69 or (108/5) b + 492/5 (or
  + 592/5). That is the record's 24 B' + 106 or less: none beats it by more than a constant.
- 5 halt after an inner counter (GROUP-1-LIKE, e.g. 2 R2 + 24 b + 104).

**G0 = 0LD / 1LD and similar (60 machines, MAXSTAGES): bounded nesting, no full cycle.**
- These machines keep the 35-digit start (G0 = 0LD emulates G0 = 1LC via I).
- At the exhaustion they build [D2, 0^(12B'+11), D0, D5, D4^32, D1 | 37 | 18].
- The 12B'+11 zeros sit behind a D2 (a blocking token) and are consumed one at a time, as a unary outer counter.
- Between that block and the right end, a structure of at most about 35 tokens is manipulated.
  - New digits D(2R_i + c) hold successive accumulators, and residue-0/2 tokens trigger events.
  - The width stayed <= 36 tokens over 21 stages (`tests/c35b.log`).
- So the structure is f_{O(40)}(B')-type, not omega-type: no list of huge length is ever cleared. Not a record.
  Halting was not determined; MAXSTAGES.

### 4.5 UNCLEAR
- **g-type conveyors** (e.g. `..._0LI0LC_..._---0RE_1LJ0LG_0RJ1RI`, 17 machines).
  - After the inner exhaustion and a second-level counter, the borrow converts L(B)'s zeros into groups such as
    (D4 D6 D7)^k with k about 12B/7, or g's (D4 D2 D7)^k.
  - Every group carries a blocking token (D2 or D6 -> D3), so no champion phase can cross a group: no full cycle there.
  - Whether the machine halts at the last group, as g does, was not determined for every class. Periods of 21 in b and
    non-affine (4^b) halting counts defeat the fitter.
- **T at stage 0.** No K-moment and no halt within 1.5e8-2e8 steps after K(0^11;0;6), in any canonical state. Examples
  of the post-exhaustion processes:
  - two (10)-runs exchanging, with a growing D1 list;
  - champion-like counters whose accumulator is followed by a 0 (tail "0 1 ...").
  These are not champion phases the follower can verify.
- **FAIL.** The fitter could not find a consistent period or validation. Causes:
  - a tool limitation fixed during the run (rational counts, e.g. (12b-30)/7 groups); these classes were re-queued;
  - periods > 21;
  - samples timing out.
- **NON-HALT runaways.** The tape grows past 4e6 cells (e.g. a left-moving 1-writer after the exhaustion).
- **UNCLEAR-LOOP at level 0.** Unary loops over L(B): each cycle consumes 2 zeros of L(B) and clears a one-digit list
  holding the accumulator. Example: `..._0LG0LC_..._0RI0RE_0RJ1LI_---1LF`, with 12b-2 -> 12b-4 -> 12b-6 zeros.
  - This is about a tower of height 6B, f_3-type. Halting at the end was not determined.
- **Two runs where the fitted fields subtract accumulators** (e.g. D(4 R2 - 2 R4 - 7)):
  `..._1RI0LC_..._---0RE_0LJ0LI_0RE0RC` and `..._0LI0LC_..._---0RE_0RJ1RD_1LI0RI`.
  - Here the representatives (all accumulators about 200) violate the real ordering R4 >> R2. The later stages of
    these two are therefore unreliable, including the level-2 claim of the first one; they are listed as UNCLEAR.
  - The follower treats accumulators as independent parameters. This is safe only while no stage compares two of
    them.

## 5. Round-2 bign probe (partial)
- `bign_r2.tsv`: 782 of the 1,596 round-2 NOBOUNDARY rows were probed before I stopped it to give the follower the CPU.
  Result: 174 CANDIDATE?, 321 HALTS-AT-11, 287 NO-HALT; 0 CANDIDATE (clean K at n=11, halting at a larger n).
- The follower covers all 1,596 rows anyway.

## 6. Reproduction
- Build: `g++ -O2 -std=c++17 -static -o hyb10n.exe hyb10.cpp` (MSYS2 ucrt64).
- One machine: `python follow2.py MACHINE [--stages 12] [--budget 150000000] [--log FILE]`.
  - c35m14: add `--template R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101 --n 35`.
  - Class members: add `--ref REPRESENTATIVE`.
  - Environment variable `HYBEXE=hyb10n.exe`.
- Batches: `python batch.py SET.tsv RESULTS.tsv WORKERS STAGES BUDGET`. Columns: machine, tag, template, n, ref.
- Signatures: `sigs2.py set_all.txt sigs2_all.tsv 4`. Classes: `classes.py`, `members.py`. Tally: `tally.py`.
- c35m14 screen: `c35screen.py c35screen.tsv 3`.
- Result files: `results_r1.tsv`, `results_reps.tsv`, `results_cls.tsv`, `results_pkl.tsv`, `results_mem.tsv`,
  `results_c35.tsv`. Per-machine logs and stage pickles are in `logs/`.

## 7. Open questions
1. The UNCLEAR classes, especially the g-type conveyors. Each needs a 9-state-style hand analysis of its end (last
   group). Structurally they cannot clear a huge list in one champion phase, but a later stage could in principle
   rebuild.
2. Members not individually followed (see the tally).
3. Proofs:
   - Coq for the loopers' non-halting: their stage maps are regular, similar to the BB(8) 30-digit rebuilders that
     were proved.
   - Coq for the ONE-REBUILD class (not a record).
4. A targeted search for **halting variants of the loopers**, rec14 and c35m14. The rebuild would have to detect a
   residue of n (n_1 = 11 or 35, n_2 = 12B+14 or 12B'+46, ...) and halt at cycle 2 or 3. This is the most direct
   route to f_omega^2-or-better behaviour that this triage found.

## 8. Addendum (later on 2026-10-07)
**1. c35m14 G0 = 0LD rebuilders: settled, unary.**
- Run: I followed `..._0LI0LC_1RG1LD_0LD0RH_1RG1LF_---0RJ_1RJ0LF` from the configuration the real run reaches at its
  first outer event, with the first accumulator set to a small exact value (R1 = 3). The big digit then runs out
  after 3 decrements and the next outer steps come into reach. Script `c35outer.py`, log `tests/c35outer3.log`.
- What happens:
  - Each decrement of the big digit takes 2 stages, each clearing only a bounded list (about 30 ones) with a fresh
    accumulator.
  - The outer zeros are then removed a few at a time: 12b+11 -> 12b+10 -> 12b+9 -> 12b+5.
  - No zero is ever refilled, and the leading D2 is never decremented.
  - So the 12B' zeros are a unary counter: omega-level 0, about f_{O(40)}(B'). No record.
- With R1 = 3 the machine halts at stage 15 in state I on a 0, with ones = 2 R14 + 108 b / 5 + 497 / 5. Whether it
  halts with the real huge R1 was not determined.
- 56 of the 60 c35 MAXSTAGES machines have this outer-block shape [D2 (or D6), 0^(12b+c), D0, ...].
- Of the other 4:
  - two build a (D0 D2)^(6b+3) list and one builds a (D0 D1 D2)^(4b+2) list. Every repetition carries a blocking token.
  - one, `..._1LI0LC_..._0LD0RH_1RG1LF_0LJ1RI_---0LA`, builds a big digit D((36b+39)/5) followed by
    (36b+24)/5 zeros. Its first event borrows from that digit across the zeros (D(X) -> D(X-4) plus a D3 next to it)
    without refilling them. Followed with R1 = 3 for 12 stages (`tests/c35outer_b.log`), the right part stays a
    bounded-width nested counter. It is unresolved whether a later event refills the zeros; that is the one c35 case
    that would need a hand analysis.

**2. A blank-tape mode (`follow2.py --blank`).**
- The champion phase from the blank tape is jumped abstractly to the real first exhaustion, so no starting shape is
  assumed. Any start works, including short starts; three nested cycles from a small start, f_omega^3(8), would also
  beat f_omega^2(25).
- Check: from blank, the BB(9) record gives ones = 36/5 R1 + 2 R2 + 42, which is the Coq score
  (R1 = 3B + 2 is the exhaustion accumulator).

**3. Sibling subtree rec14_1RE.** It had 24 NOBOUNDARY rows at the time of writing.
- None has the champion's doubling rule (dlscan2 R1: b+2, b+3, b+4 or 3b+3), and its 11-digit-start rows are
  CHAMPION grades. All 24 time out in the follower, whose model needs doubling.
- These families need a generalised follower (r -> alpha r + beta) or the bign route.
- rec14_0RH had no rows yet.

**4. g-type conveyors from g's real end configuration** (`endtest.py`, `endtest.tsv`).
- What was tested: the 57 machines whose follower logs reach g's conveyor groups (D4 D2 D7)^k, plus g itself. Each
  was started from the real end-of-list configuration of the 9-state study (`bb9_c7m12_1RB0RA_0RI0LC/g2/endtoks_B6.txt`,
  digit D(6139) exhausted, accumulator X = 2, 5, 8). 51 of the 58 runs finished before I stopped the job (the
  non-halting ones use the full 2e9-step budget).
- Results of the 51:
  - 24 halt exactly as g does, with ones 448 / 592 / 1168 (one machine 447 / 591 / 1167). So they are GROUP-2-LIKE:
    about 17 T, no record.
  - 27 do not halt there. Within 3e7 steps they keep working on the last group, or have already moved into the
    next-to-last group (D7 -> D6 or D3, new digits).
    - The groups further left stay intact, so as far as visible they consume the groups one at a time from the right.
      That is unary over about 12B/7 groups, omega-level <= 1.
    - Whether some group step rebuilds a list as long as the accumulator was not determined. One representative needs
      a hand analysis: the (10)^Y sublist of g's end, Y = 48*4^b, would be such a list.
- The follower cannot settle these by itself. In front of g's merged-counter tail the champion rules hold only for
  about 12 transitions; then the tail itself becomes active, and the rule check correctly refuses the jump
  (UNCLEAR-RULES).

**5. Files.**
- Full looper list: `loopers.tsv` (156 machines with class ids).
- The member pass stopped at 236 machines (`results_mem.tsv`). Resume it with
  `python batch.py members.tsv results_mem.tsv 4 12 150000000`.

## 9. How to triage new watcher rows (rec14_0RH, rec14_1RE, any later subtree)
- All commands run from `bb8_list/investigations/bb10_bb7_descendants/`. They use Idle priority and skip machines that
  are already in the results file, so they can be re-run after every watcher round.
- Whole watcher file:

      python watch_triage.py ../bb10_from_bb7/rec14_0RH/watch_hits.tsv results_0RH.tsv 4 12 150000000

  Arguments: hits file, results file, workers, stage cap, step budget per simulator call. It takes the NOBOUNDARY,
  R4-SOME and HALT? rows, runs `follow2.py --blank` on each (log in `logs/<machine>.log`), then prints a tally and a line
  `!!! RECORD CANDIDATE: ...` for every HALT at omega-level >= 2.
- One machine:

      HYBEXE=hyb10r.exe python follow2.py MACHINE --blank --stages 12 --budget 150000000 --log logs/MACHINE.log

  For a start on the BB(8) record's 35-digit list use `--template R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101 --n 35`
  instead of `--blank`.
- Reading the last line, `RESULT KIND stages=S full_cycles=C level=L history=[...] [ones=...]`:
  - `history` has one entry per stage. `('J', blocker, cleared)`: the run jumped to the next event; the borrow stopped
    at `blocker` (`block` = a blocking token, `a-block` = the a-token bottomed, `left` = the left end); `cleared` is True
    when a list of huge length was cleared, i.e. one full rebuild-and-clear cycle. `('H', ones)` = halts there.
  - `level` is the omega-level of the newest accumulator: 0 = the first exhaustion's size (about B), 1 = one full cycle
    over a list of length about 12B (f_omega(12B)), 2 = a second length-expanding cycle (f_omega^2(12B)).
  - HALT with level 0: CHAMPION-LIKE (stages=1) or GROUP-1-LIKE. Level 1: ONE-REBUILD (best so far, below the bar).
    **Level >= 2: RECORD CANDIDATE.** From the 35-digit start, a HALT with level >= 1 is already a record (route b).
  - LOOP with full_cycles >= 1: the stage input repeats with only lengths/accumulators changing, an infinite rebuilder.
  - UNCLEAR-T: the simulator ran out of budget. With level >= 2 this is almost always a looper whose next list is too
    long to simulate (tally: "INFINITE-REBUILDS? (T at omega-level >= 2)"). UNCLEAR-RULES: the champion rules failed in
    front of the tail, so the jump was refused. MAXSTAGES: stage cap reached (raise `--stages`). CRASH: a parser
    failed; the error is in the log (parsers fail loudly, nothing is guessed).
  - The tally categories are those of `tally.py` (`category()`).

## 10. Halting relatives of the loopers (radius-2 and targeted radius-3 search, 2026-10-07/08)
**No halting relative was found.** Every variant either still loops, halts at a level-0 event (GROUP-1-like), or
becomes chaotic: the outcome of an event depends on the huge accumulator with no period the follower can find.

**What a stop condition could test**
- C28 and the rec14_0RH looper: one event type, [11 0^n | R].
  - Every event's accumulator, the first exhaustion's included, has the universal residue rho (= 20 mod 2520 for
    e = 2; the blank-tape follower assigns it).
  - The rebuild gives n' = n + 4R - 5. So n mod 3, 5, 7, 9 never change, and n mod 8 runs 3, 6, 1, 4, 7, 2, 5, 0
    over E_0, E_1, E_2, ...
  - A halt at E_2 (omega-level 2, a record) therefore needs a test of n mod 4 or mod 8, which means a parity-tracking
    pass over the whole list.
  - The handler's left-end contexts are its own (a radius-3 window around the head already separates them from the
    champion phase), but the left end looks the same for every n.
- C29 / C32: three event types.
  - [11 0^n | R] stores R as a left digit D(2R-1); [D3 0^n | R] stores again; [D0 0^n | R] expands the list by
    4R - 5.
  - n mod 8 alternates 3, 7 between cycles.
- c35a / c35b: E_1 = [D2 0^Z D1 | R | D4] differs from E_0 by the D2 marker. But every (state, tape window) context
  the E_1 handler visits also occurs in the start-up, the E_0 handler or the champion phase: windows of radius 8 for
  c35a (new contexts only at radius 12), radius 12 for c35b (`loopvar/winctx.py`). So no change of a few transitions
  can act at E_1 alone.

**Residue correction (affects only the screens below).** The first-exhaustion accumulator 3B+2, with 2B+4 = 2^^13 3,
has the universal residue rho; checked directly, 3B+2 = rho mod Q. So b = B = 6 mod 840. By an arithmetic slip the
first screens used b = 14 for E_0; they were redone with R = 20 = rho mod 2520. The c35 post-cycle tests were redone
with R = 18 and 138 (rho_0 = 18 mod 2520 for e = 0); the earlier tests used R = 201 and 606, which match only mod 3.

**Radius 2** (every pair of slots, every value including `---`; `loopvar/nbrstart.exe`). A variant must first reach
the parent's start configuration from the blank tape:
- rec: C28 3,300; C29 3,229; C32 2,817 (9,337 distinct); rec14_0RH looper 2,563.
- c35: c35a 427; c35b 761.
- Variants that change only free slots are inside the triaged trees (rec14, rec14_0RH, c35m14). The new territory
  is the root-changing ones: 2,642 rec, 796 rec14_0RH, 143 c35.

**c35 (143).**
- All rebuild at E_0 (`screen.py c35`, b = 6, 7).
- The 137 that keep a parent rebuild shape (5 4*117 or 8 4*115) rebuild again at E_1 and E_2, for b = 6, 11 and
  R = 18, 138 (`c35_r2_post18.tsv`). The 88 radius-1 variants do the same (`c35_r1_post18.tsv`).
- The other 6 (follow2, template mode):
  - one new clean c35 looper, B1=1RJ J0=0LH, with n -> 5n + 4R + 15. It rebuilds in every (n, R) cell tested.
  - 2 unary LOOPs: the outer zeros 12b+3 -> 12b+1, the G0=0LD pattern.
  - 3 MAXSTAGES at level 0 (non-clearing events with blocking tokens).

**rec (2,642 + 796): fast halting scan** (`loopvar/cellscan.exe`, `cellrun.py`).
- Cells:
  - C28 and 0RH: E_0 = (n = 11, R = 20) and n = 12..19 at R = 20.
  - C29 / C32: the same E_0, then each of the three event types for n = 12..19.
- Results:

| family | halt at E_0 | halt only in later cells | no halt in any cell |
|---|---|---|---|
| C28 | 121 | 14 | 758 |
| C29 + C32 | 198 | 47 | 1,504 |
| rec14_0RH looper | 83 | 37 | 676 |

- All 98 later-halting variants were followed from the blank tape (`results_r2halt*.tsv`):
  - 38 GROUP-1-like;
  - 37 chaotic FAILs;
  - 17 UNCLEAR-T before any full cycle;
  - 3 UNCLEAR-RULES;
  - 2 simulator failures;
  - 1 ONE-REBUILD: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RF_---1RJ_0RC1RJ`, a C29 variant that halts
    after one full cycle at level 1.
  - None halts after a full cycle.
  - Most halting cells come from H1 = 1RE or H1 = 0RF combined with another change. Those handlers no longer
    rebuild like the parent: the real run halts at a level-0 event (GROUP-1-like), or the outcome depends chaotically
    on the accumulator.
  - Example of the chaotic kind: `..._0RG0RF_0RD0RH_0RE---_0LB0RJ` and its 0RH siblings do one full cycle. Their E_1
    handler then runs a conveyor whose pieces shrink by a factor 5/3 (636, 374, 224, 134, 80 at R1 = 260), and its
    outcome changes with R1 from sample to sample. Only the follower's samples near the real class mod 120 were
    examined. These are Collatz-like and cannot be settled with these tools.
- n-sensitive handlers do exist at radius 2. For example `..._0RH0RF_0RD0RF_0RE---_0LB0RJ` halts exactly when
  n = 12 mod 20, for every R tested. But in each such case the rebuild also changes the tail or the event type, so the
  clean n -> n + 4R - 5 cycle is lost.

**Targeted radius 3** (triples of E0, G0, H0, H1, I0, I1, J0, J1 that contain a root slot, G0 or H1; 2.3M variants
per parent; `nbrstart3.exe`, `r3pass.py`).
- C28: 87,770 reach the start (87,761 not already at radius <= 2).
  - 7,367 halt at E_0. The other 80,394 fall into 5,054 classes by their configuration fingerprint at the E_0 cap
    (one representative per class gets the full grid).
  - 4,964 classes halt in no cell; 90 halt only in later cells.
  - The 90 representatives are being followed from blank (`results_r3late.tsv`, 1 worker): 4/90 done: 3 UNCLEAR-T, 1 UNCLEAR-RULES
- C29 / C32: 87,019 and 84,199 reach the start (171,209 new).
  - The fingerprint pass stopped at 24,520 machines because of the lead's compute cap: 1,223 halt at E_0, and the rest
    fall into 437 classes.
  - Resume: `python loopvar/r3pass.py loopvar/r3_C2932_new.txt r3_C2932 C2932 4` (it does not skip finished machines).

**Why a hand construction was not attempted**
- C28-type cycles: a stop at E_2 needs a mod-4 test of n. Every state and transition of the parents is used by the
  champion phase, so such a test needs a list pass driven by states that are free in that context. None exists
  within radius 3.
- c35: the marker difference at E_1 is invisible to any local change (see the window argument above).
- The machines closest to the target are chaotic. Example: `..._0RI1RE_---0RJ_1LB0RJ` rebuilds at E_0 to a list of
  length 4R1/5 + 3 (one full cycle). Its E_1 outcome then depends on R1 and halts in most samples, which would be
  level 1. Even a lucky one could not be proved with these tools.

**rec14_0RH round 2 (watch_triage, 1 worker since the compute cap)**
- NOBOUNDARY / R4-SOME / HALT? rows: 83/461 done: 43 INFINITE-REBUILDS? (T at omega-level >= 2), 25 GROUP-1-LIKE, 7 UNCLEAR-T, 3 chaotic FAIL (no period in the accumulator), 2 UNCLEAR-MAXSTAGES, 1 UNCLEAR-LOOP, 1 ONE-REBUILD (omega-level 1, 2 full cycle(s)), 1 simulator FAIL
- 43 of them are new loopers (two full cycles, level 2, then T). None halts in any n-cell (n = 11..43, R = 20).

**rec14_1RE (all 56 rows)**
- 35 T: the non-doubling family, outside the follower model.
- 13 GROUP-1-like.
- 8 FAIL.
- No full cycle.
