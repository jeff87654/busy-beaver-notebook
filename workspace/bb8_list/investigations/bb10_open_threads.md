# BB(10) triage: hand analysis of the three open threads

Agent inv-bb10-open-threads, 2026-10-07. Input: `bb10_bb7_descendants.md` sections 4.5 and 8.
Tools and logs: `bb8_list/investigations/bb10_open_threads/`.

## Verdict
**No confirmed record candidate.** The bar is f_omega^2(25) = f_F(F) with F = f_25(25). Two findings change the
triage's picture. Each has the record *shape* but an open halting question.

1. **Thread 1, the 27 non-halting g-type conveyors: record-shaped loopers, halting undetermined.**
   - The conveyor itself is unary, as the triage said. But it is not the end of the run.
   - After the groups and the prefix are consumed, the borrow walks off the leftmost `11` while the conveyor's long
     tail is still on the right. The machines then **rebuild a list whose length grows with the accumulator** and clear
     it with the champion rules. That is a full f_omega cycle.
   - For the E0=0LI representative the follower fits the list as **D4^(128R+517)**: ones, cleared with "huge-length
     list cleared: True". The fit is symbolic and validated.
   - Every later walk-off rebuilds again. Which form the rebuild takes depends on the zero count m at the walk-off:
     ones, D94 digits, zeros behind a digit, or g's prefix plus (4 2 7) groups again.
   - So these machines have the triage loopers' shape, with mixed cycle types. None halted in any probe.
   - A machine that halted after its 2nd Ackermann-type cycle would beat f_omega^2(25). Whether any of the 27 does was
     **not determined**.
2. **Thread 2, the c35m14 exception: record-SHAPED (route b), halting UNDETERMINED.** The triage's "unary" reading
   is wrong.
   - The machine converts its Z = (36B+24)/5 outer zeros (about 7.2 B, with 2B+4 = 2^^37 3) into V-counters and lists
     of ones whose length is proportional to Z. The champion rules then clear these lists: an **Ackermann cycle over
     cZ digits**. That is far beyond f_omega^2(25).
   - So if this machine halts at all, it is a record.
   - Halting is not decided. The outer zero block is converted *recursively*:
     - In the real class Z ≡ 0 mod 10 the block becomes a V-token D((3Z-10)/5) followed by (3Z-20)/5 zeros.
     - The next level depends on that new count mod 10, and so on.
     - So the end game depends on many 5-adic and 2-adic digits of Z. Small representatives cannot capture this.
   - **All my earlier end-game runs used Z in wrong residue classes** (Z = 12, 48, 84 are not 0 mod 5). Their
     outcomes (J0 halts at Z = 12, a translated runaway at Z = 48) do not transfer to the real run.
   - Full runs with accumulator r = 6 and r = 18 also diverge, so some later event depends on r's residue as well.
   - The independent verifier (inv-bb10-c35exc-verify) is continuing.
3. **Thread 3, rec14_1RE (24 NOBOUNDARY rows): quick classification.** These machines run their own counters with
   additive R1 (b -> b+3 or b+4), not the BB(7) champion's.
   - 4 machines (the "R5" type, e.g. `..._0RI1RE_0LA0RJ_0LC---`) rebuild, at a left-end exhaustion, a list of
     digits whose length is proportional to the accumulator, and clear it Ackermann-style. That is the looper shape, so
     they could reach f_omega^2 *if* they halted after two such cycles.
     - The only halting transition sits behind a rare chain (F0 G0 H0 I1 J1).
     - In all probes, J was entered only at left-part transitions, and always read 0.
     - Likely loopers; not proved.
   - 18 machines rebuild blocker-laden groups or junk: unary, no f_omega^2 potential seen.
   - 1 machine is unclear. 1 has no rebuild.

Confidence: literal simulation plus the stage follower (affine fits validated at extra points). There is no Coq and
no full super-cycle analysis.

## 1. Thread 1: the 27 g-type conveyors that do not halt at g's end
### 1.1 Classes and the conveyor phase
- The 27 machines are the non-halting rows of `bb10_bb7_descendants/endtest.tsv` (list:
  `bb10_open_threads/nonhalt27.txt`). Two classes, by how the conveyor groups are consumed:
  - **A** (12 machines, E0 = 0LI or 0LG; representative `..._0LI0LC_..._---0RE_0RJ1LI_1RI1RG`):
    - The last group's `4 2 2 1 1 X` (where g halts) continues as stages: `4 0 (2X-9) 92`, `4 0 1 R`,
      `1 (2R-4) 40 8`, `1 3 1 R`, `1 0 1 R`, then the next group's D7 -> D3 -> D0, `2 3 R`, ...
    - One group `4 2 7` takes about 6 follower stages, each a champion phase on a list of at most 4 tokens
      (`logs/A_G1.log`).
    - Each stage is f_c(R) with small c, so the k ~ 12B/7 groups give f_{c+1}-type growth: omega-level 0, unary.
  - **B** (15 machines, E0 = 1LH; representative `..._1LH0LC_..._0RI0RE_---0LJ_0RF---`):
    - The groups are consumed cheaply. Literally (`B1.txt`), one group takes r -> about 4r (8 -> 109 -> 481).
    - The prefix tokens D14, D10, Q are then consumed with r roughly doubling per decrement (`B_pfx.txt`).
- The conveyor's tail `D0^6 (1 00 D0^5)^T 1 00 1 00 D0` gains one unit at certain events. T is about 12B/7 + c.

### 1.2 Prefix
- Class A: the prefix `11 D4 D9 D6 Q D14 D10` with Q = D(2R+6) was followed with the follower (`logs/A_pfx.log`).
  - Loop acceleration (section 4) shrank Q, which acts as a V-type token: -3 per two stages, with a D3/D0 companion.
  - Q, D14, D10 and D6 are consumed in 18 stages and end at `11 D4 D9 D1 D3 | R` (literal check: `A_pfx_lit.txt`).
- Class B: literally, the whole prefix reduces to `11 | a=D1 | r` (`B_pfx.txt`, step 1.53e6).

### 1.3 The left-end rebuild (the new finding)
- **Class A** (`logs/A_left.log`, follower, period 1, validated):
  `11 D4 D9 D1 D3 | R`  ->  champion phase `11 D4^(128R+517) D1 | 40 | 8`
  - The jump clears this huge list: event `11 D1^(128R+518) | 1 | R'`, omega-level 1.
  - Literal view with r = 8 (`A_pfx_lit.txt`): `11 D4 D5 | 92` turns into `11 D4^3 D7 D1^1539 D2`. A conveyor then
    turns the zeros into ones, 22 per pass.
- **Class B** (literal, `B_left15.txt`):
  - `11 | D1 | 15` walks off the `11`. The accumulator becomes a (100)^k run.
  - Each conveyor pass appends one D94 (digit 31) on the left: `11 D94^j D95 ...`.
  - The finished list `11 D94^6 ...` is run by champion R1/R2/R3 (`D(93) D(191)`, `D(87) D(776)`, `D(81) D(3116)`, ...).
  - The list length grows with r: 4, 6 and 7 for r = 11, 14 and 17, and at least 40 for r = 1854 (`B_pfx.txt`).
- **All 27** (`leftend.py`, `leftend.tsv`, start `11 D1^m | D1 | r` with the conveyor tail, m = 0..3, r = 9 and 20):
  - The same left-end types appear for every machine:
    - m=0: `11 D94^k D95`;
    - m=1: `11 D8 D94^k D95`;
    - m=2: `11 (4 2 7)^k`, i.e. g-type groups again;
    - m=3: `11 D5 D1^k D0` for class A, `11 D2 D390 D4^k` or similar for class B.
  - k grows with r in every case. No run halted (5e7 steps each).
- For class A, larger m (4, 5, 6, 7, 10) gave in turn: zeros behind D3; `11 14 10 (4 2 7)^3`, g's prefix fragment plus
  groups; `11 4 412 94 95`; `11 4 9 D1^25`; `11 9 5 D1^28`. So the type depends on m in a non-obvious way.

### 1.4 What this means
- Real run: the BB(7) champion gives B (2^^13 3). The first exhaustion rebuilds L(B). Then come the inner counter, the
  second-level counter, the conveyor over about 12B/7 groups (unary) and the prefix. The accumulator R_end at the first
  left-end walk-off is f_{O(10)}(B) < F.
- Super-cycle 1 rebuilds a list of length proportional to R_end and clears it: f_omega(c R_end), omega-level 1. That
  alone is below the bar, since c R_end < F.
- Super-cycle 2 starts with m = (previous list length + c) zeros. Its type depends on m (for class A, m = 128R + 518).
  - A ones/D94/zeros-behind-a-digit type gives omega-level 2.
  - A g-group type is unary but leads to a further walk-off.
- **A halt at any point after the 2nd Ackermann-type cycle beats f_omega^2(25).**
  - Halting needs each machine's undefined transition in a context that no probe produced.
  - No probe halted: 216 left-end probes plus all literal traces.
  - Following the super-cycles needs the follower to fit stages whose representatives build long lists. It ran into
    timeouts: `logs/B_left3.log`, `logs/A_left3.log`, "no period ... T".
- **Status:** record-shaped loopers with m-dependent super-cycles. Halting undetermined; looping looks more likely
  (nothing halts, every type rebuilds).

## 2. Thread 2: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0LD0RH_1RG1LF_0LJ1RI_---0LA`
### 2.1 The real run up to the first outer event (triage log, re-checked)
- From the BB(8) record's exhaustion K(0^35;0;B') the run reaches
  `P D(X) D1^Z D0 D2 D1^35 | 0 | R1`, with X = (36B'+39)/5 and Z = (36B'+24)/5 (about 7.2 B').
- The first outer event gives `P D(X-4) D3 D1^Z D(2R1+3) D6 D4^33 D1 | 37 | 18`:
  - X goes to X-4 and a D3 appears next to it;
  - the Z zeros are untouched;
  - the right part is refilled.

### 2.2 The inner (right-part) counter: rules
Read off the follower stages and checked by literal probes (`logs/c35_*.log`, `C35_w1.txt`). V tokens are D(2R+c), q
tokens are D0/D3/D6, and z is a zero.
- **E1:** `D3 z^n | 0 | r` -> `D0 D(2r+4) D4^(n-2) D1 | 37 | 18`. The new digit is a standard digit, cleared to zero
  later.
- **E2:** `V D0 z^n` -> `V-4 D3 D(2r+2) D4^(n-2) D1`. D(2r+2) is a 3e+2 digit and bottoms at the blocker D2.
- **E3:** `D3 D2 z^n` -> `D0 D(2r+5) D6 D4^(n-2) D1`. This creates a new V = D(2r+5).
- **Dead V:** `V D0 D1 D0 z^n` -> `V-4 D2 D0 D2 D(2r+2) ...`. A V that died as D1 leaves a blocker pair D0 D2.
- Residues: the huge R are 0 mod 3 and 2 mod 4. So V1 = D(2R1+3) is 3 mod 4 and bottoms at D3; later V's,
  D(2R+5) and D(2R+1), are 1 mod 4 and die as D1.
- The structure is a hydra of V counters: bounded width (about 35), f_{O(35)} per outer step.

### 2.3 Outer events: what can happen to the Z zeros
Literal probes with X = 11, Z = 12 and various right parts (console probes; configurations listed here):

| right of the outer zeros | result for the outer zeros |
|---|---|
| pure zeros up to the a-token | outer D3 -> D0, **all zeros refilled with ones** (D13 D4^13) |
| `D0 z^3` | X -> X-4, zeros restructured to `D5 D1 D7 D1^6 D0 ...` |
| `D3 D0 z^3` (V1 at its bottom) | outer D3 -> D0, first zero -> D6, the rest untouched |
| `D1 D0 z^3` (dead V) | `D8 D1 D3 D8 D1^7 D5 D4^3 D7 ...`: a 3e+2 digit followed by 7 zeros, no blocker |
| `D0 D0 z^3`, `D0 D2 z^3` | restructuring, no refill |
| q token followed only by zeros: `D0 D6 z^14` | D6 -> D3, **full refill** D10 D4^12 |

- **Synthetic follower run** (`logs/c35_v1bot.log`; start: V1 at its bottom, pure zeros to its right):
  - outer D3 -> D0, D6;
  - then D6 -> D2 and a D3;
  - then E3 across the outer zeros;
  - then `... D(2R3+5) D3 D1^13 | 0 | R4` -> `D0 D(2R4+4) D4^11 D1`.
  - So 10 of the 12 outer zeros merged with the inner zeros and were refilled with ones.
  - In the real run that is an Ackermann cycle over about Z digits: f_Z(.) > f_F(F), since Z ~ 7.2 B' and
    2B'+4 = 2^^37 3 > F.
### 2.4 Event-level simulation of the real dynamics (`c35ev.py`)
**Method.** The state is the token list left of the a-token.
- Event: a literal run from `TOKENS D1 D(r) D4` until the first champion-phase lock that is followed by a verified
  transition (`evt -j 1`, `evt2.exe`, which is evt with a generous unlock limit).
- Jump: the abstract champion clear, using the same bottoms as follow2's jump.
- Accumulators are reset to r = 6 after every event, the real residue of R mod 24. So new big tokens D(2r+c) are small
  but have the right residue mod 24: the follower's loop acceleration, applied at birth.

**Checks.**
- Events 0-12 agree with the symbolic follower (`logs/c35r_w3.log`).
- Events 14 and 22 were re-checked by direct literal runs. Event 63 of the Z=48 run (the E1 refill
  `D12 D3 D1^14 -> D0 D16 D4^12 D1`) was also checked directly.
- The outer events are r-uniform: r = 6, 18, 30 and 42 give the same structure, only the D(2r+c) tokens change.
- Event detection with `-j 3` is wrong in the zero-free regime (it skips events). `-j 1` agreed with the literal
  checks.

**Runs** (P = `2 1*2 0 2 1 0 1`):

| X, Z, inner width | outer zeros | end |
|---|---|---|
| 15/131, 12, 3 (`c35ev_j1_w3X15.txt`, `..._w3X.txt`) | chunks refilled with ones (lists of 2); consumed in ~90 events | **HALT in J0** at event 93, sigma = 2r+27 (checked r = 6..102) |
| 15, 12, 7 (`..._w7X15.txt`, `..._w7X15c.txt`) | merged with the inner zeros and refilled (11 ones) | walks off P's left end, a small junk restructure, then **HALT in J0** (event 20 of the continuation) |
| 15, 12, 9 (`..._w9X15.txt`) | as above | **HALT in J0** at event 212 |
| 15, 12, 5 (`..._w5X15*.txt`) | refilled into a 13-wide V-hydra | not finished |
| 51, 48, 3 (`..._w3X51*.txt`) | `D27 D1^24`, then hydras and ones lists (12) | event 122: **translated runaway** (D0 run growing about 17k per 1e6 steps, no halt in 1e9 steps, r-independent) |
| 47, 48, 5 / 7 (`..._w5X51.txt`, `..._w7X51.txt`) | V-hydras of width proportional to Z (15 V's at width 5) | not finished (event count exponential in the hydra width) |
| 207, 84, 3 (`..._w3Z84.txt`) | `D49 D1^46`, a V-hydra `13 0 13 0 ...`, ones lists of 17-18 | stopped at event 77 |

**These runs are all in wrong residue classes; see 2.5.** They establish the mechanism (Ackermann use of the outer
zeros) but not the end game.

### 2.5 Real residues and the period-10 conversion (corrected analysis)
**Real parameters.**
- B is the BB(8) record's final accumulator, 2B+4 = 2^^37 3. From numres, B ≡ 16537583495166 mod 18101949465600:
  B ≡ 6 mod 360, 14 mod 16, 1 mod 5, 6 mod 7, 15 mod 27.
- Z = (36B+24)/5 and X = (36B+39)/5 (from the follower's stage 0 of the real run). Both are fixed modulo
  36M/5 = 2^12 3^9 5 7 11 13 17 19. In particular:
  - Z ≡ 0 mod 10, 48 mod 96, 240 mod 480, 144 mod 768, 912 mod 1536, 2448 mod 4096, 5520 mod 23040, 3 mod 9;
  - X ≡ 243 mod 480, 147 mod 768, 2451 mod 4096.
- Accumulators after champion clearings have the universal residue R ≡ 49612750485498 mod 54305848396800: 0 mod 3,
  2 mod 8, 10 mod 16, 3 mod 5, 23 mod 25. Small representatives: R ≡ 42 mod 48, 138 mod 240, 1098 mod 1200.
- The real inner width is 35, which is 3 mod 8. Widths 3, 11 and 19 are in its class mod 8.
- Earlier I wrote "Z = 48 mod 96 so Z = 48 is the real class". That was wrong: Z is also 0 mod 5. **Every Z in the
  table above (12, 48, 84) is in a wrong class mod 10**, and my r = 6 is not 3 mod 5 and not 2 mod 8.

**The first outer conversion** (`conv_scan.py`, `conv_scan.txt`):
- Input: `P X D3 D1^(Z-2) D0 D0 D2 D1 | 0 | r`, the state after the inner hydra first dies. Scanned for even
  Z = 8..60, X = 147, r = 6, 18, 42, 90.
- The result is **r-uniform**: only the D(2r+3) token changes (15, 39, 87, 183).
- It is **periodic with period 10 in Z**:

| Z mod 10 | result (the zero block becomes `D(a) D1^b`) |
|---|---|
| 0 (real) | `X-1 D2 D1 D((3Z-10)/5) D1^((3Z-20)/5) D0 D(2r+3) D3 D1^3` |
| 2 | `X-3 D1 D3 D((3Z-11)/5) D1^((3Z-16)/5) D(2r+2) D3 D1^4` |
| 4 | `X-3 D2 D3 D((3Z-7)/5) D1^((3Z-22)/5) D0 D(2r+3) D3 D1^3` |
| 6 | `X-4 D5 D1 D((3Z-13)/5) D1^((3Z-18)/5) D0 D(2r+3) D3 D1^3` |
| 8 | `X-4 D4 D1 D0 D1 D((3Z-9)/5) D1^((3Z-24)/5) D0 D(2r+3) D3 D1^3` |

- The cells are conserved: Z zeros take 3Z cells, and D(a) plus b zeros take about 1.2Z + 1.8Z cells. The machine
  re-parses the zero block, turning its left 40% into one big token.
- That token is a V-token: it later loses 4 per two outer events. The b ≈ 0.6Z zeros right of it are processed
  again. In the Z=48 run, the 26 zeros left after V 27 -> 23 became `D16 D1^14`, again about 0.6.
- So the outer zero block undergoes a **recursive conversion** with ratio about 3/5, roughly log_{5/3} Z levels deep.
  - Each level's class is the residue of the new zero count mod 10, then of the next, and so on.
  - The end game therefore depends on Z's residues modulo 10·(5/3)^k-type moduli: many 2-adic and 5-adic digits.
  - Z = (18·2^E - 48)/5 with 2^E = 2^^37 3, so those digits are computable with the recursive tower-residue method.
    I did not do that recursion.
- Further residue dependence: full runs at Z=12, w=3 with r = 6 and r = 18 diverge (r=18 restructures P instead of
  halting), so some event beyond the first conversion depends on r mod 8 or 16.

**Real-class simulations.** Memoised event simulation (`c35memo.py`): sub-runs are cached by suffix, and V-loops are
accelerated with residues kept mod 48. Runs with Z=240, X=243, r=138 (all in the real class mod 240/480) at widths
3 and 11 (`logs/memo_real_w*.log`) were started but stopped at the first top-level event when the lead asked me to
finalize. They need hours; the event count grows with the recursion depth.

### 2.6 Assessment
- The triage note ("borrows across the zeros without refilling them") describes only the first outer event.
- Later outer events convert the Z zeros recursively into V-counters and lists of ones of length proportional to Z.
  The champion rules clear these lists, giving f_{cZ}-type growth, far beyond f_omega^2(25) (Z ~ 7.2 B > F).
- So the machine is a **route-(b) record if it halts**. If it halted, sigma would be 2 R_final + c, as the J0 halts at
  Z=12 show: sigma = 2r+27 there.
- **Halting is undetermined.** It depends on the recursion of the zero-block conversion through the real residues of
  Z (and on r's residue). None of my end-game runs was in the real class.
- The independent verifier (inv-bb10-c35exc-verify) continues the machine.

## 3. Thread 3: rec14_1RE NOBOUNDARY rows (24)
- Method:
  - blank-tape structure (`t3/blank.sh`, `t3/blank.txt`);
  - empty-list exhaustion K(;0;b) for b = 1..4 from the watcher's template (`t3/rebuild_scan.py`, `t3/rebuild_scan.tsv`);
  - real-context probes for #1.
- Counters: lists of at most 5 tokens; R1 is additive (r -> 3r+4 per a-step in token terms); first exhaustion about
  3^^5.
- Types (variable part after `..._0RH0RF_`):
  - **R5, 4 machines** (`0RI1RE_0LA0RJ_0LC---`, `0RI1RE_0LA0RJ_1LF---`, `0RI1RE_0LA1RJ_0RF---`,
    `0RI1RE_0LA1RJ_1RA---`):
    - The left-end exhaustion rebuilds `0 1 0 0 2 1 1 0 4 5^L` with L = 12b + 39 (b = template accumulator).
    - The 5s (digit 2) are decremented 5 -> 3 -> 1 with the accumulator refilled into the next zero (R3-type): an
      Ackermann cycle.
    - In #1's real context, the first exhaustion gives `D(acc) D1^3`, a bounded phase. When D(acc) runs out, the
      long-list rebuild follows; when the long list is exhausted, the left part unwinds with small refills.
    - Halting: only J1 halts, reached via I1; J was entered only at left-part transitions, always reading 0 (`usage.exe`).
    - Looper-like. **Could exceed f_omega^2 only if it halts after two long cycles; no evidence that it does.**
  - **Z0, 7 machines** (`0RI1RE_0RJ0RA_---0RA`, `..._---1LH`, `0RI1RE_0RJ1LI_---0RA`, `0RI1RE_1RJ0RA_---1LA`,
    `..._---1LI`, `0RI1RE_1RJ1LI_---1LA`, `1RI1RE_1RJ1LA_---1LI`): a run of about 40-76 D0 tokens. It is restructured
    into blocker-laden junk with small additive counters. No Ackermann use seen.
  - **G3, 8 machines** (`0RI1RE_1LD1RJ_*`, `1RI1RE_0RA0RJ_*`, `1RI1RE_0RA1RJ_0LB---`, `1RI1RE_1LG*`): groups
    (D0 D0 D3)^k with k growing with b. Blocker per group, unary.
  - **Pairs, 3 machines** (`0RI1RE_1LE1RJ_1RF---`, `1RI1RE_0LC0RJ_0RB---`, `1RI1RE_1LH0RJ_0RB---`): groups (D2 D0)^k,
    unary.
  - **`1RI1RE_1LC0RJ_0RB---`**: `0 1 0 0 2 D1^58 0 1^3`, zeros behind a D2. Unclear.
  - **`0RI1RE_0LA0RJ_1RC---`**: no rebuild (at most 6 items).
- None halted in any probe.

## 4. Tools (all in `bb10_open_threads/`)
- `evt.cpp` / `evt.exe`: literal simulator with an event view.
  - It prints canonical configurations only at shape changes, champion-phase locks/unlocks with R1/R2/R3 counts,
    snapshots and halts.
  - `-j N` stops after N verified transitions.
- `tv.py`: runs evt/hyb from a configuration in the follower's notation (`D(expr)^{expr}`, blocks, junk, [Q]) with
  parameter values.
- `fstart.py`: follow2's stage follower from any symbolic start configuration. Options:
  - `--accel`: loop acceleration. A token that drops by a constant between equal-shape stage inputs is set to its
    residue mod 12 plus 12.
  - `--lb`, `--ks`: representative size and sample count.
  - `--retry`: timed-out samples are retried with a larger budget.
  - `--verify`: number of verified transitions required.
- `hybz.cpp`: hyb10 without parse amortisation. Not needed in the end.
- `c35ev.py`: event-level simulator for the c35 machine (literal event, abstract clear, accumulators reset to r).
  - Use `EVTEXE=evt2.exe JSTOP=1`.
  - `evt2.cpp` is evt with an unlock limit of 64 + 4r instead of 64 + r/4.
  - Junk items are carried as opaque blockers.
  - Example: `EVTEXE=evt2.exe JSTOP=1 python c35ev.py "2 1*2 0 2 1 0 1 15 1*12 0 2 1*3" --steps 400`
- `c35memo.py`: c35ev with suffix memoisation and V-loop acceleration (`--mv`, residues kept mod MV).
- `conv_scan.py`: scan of the first outer conversion over Z and r (`conv_scan.txt`).
- `leftend.py`: left-end probes for the 27 conveyors.
- `usage.cpp`: transition usage counts and entry contexts of one state.
- `t3/`: thread-3 scripts (`kprobe.py`, `rebuild_scan.py`, `blank.sh`).

Example:
- `python fstart.py MACHINE "D(0)^{2} D(4) D(9) D(1) D(3) D(R1) D(0)^{6} (1^1 0^2 D(0)^{5})^{13} 1^1 0^2 1^1 0^2 D(0)" "R1=H:24806375242748" --lb 2 --ks 7 --log logs/A_left.log`
- Set `HYBEXE=hyb10r.exe`, which is resolved against `bb10_bb7_descendants/`.

## 5. Open questions and next steps
1. **Thread 1 super-cycles.** Build a super-cycle map:
   - the left-end walk-off with m zeros (as a function of m and r residues) -> list type and length;
   - Ackermann clear or unary conveyor -> the next m.
   Then look for a cycle of types (looper, no halt) or a halting branch.
   - Halting needs each machine's undefined transition. For class A the representative's H0 is reached only via G0.
     Its contexts at the walk-off events should be enumerated.
   - Any machine that halts after its 2nd Ackermann cycle beats f_omega^2(25).
2. **Thread 2.** Compute the recursive zero-block conversion with real residues. The steps:
   - fit the conversion law per class at every level (the first level is in 2.5);
   - track Z's residues through Z -> (3Z-20)/5 -> ... using Z = (18*2^E - 48)/5, where 2^E = 2^^37 3 has known tower
     residues;
   - track the V-token and accumulator residues (R mod 2^k, 3, 5) at each branch.
   Then decide the end game: a J0 halt at P, or a runaway as seen in wrong classes. A memoised simulator with
   V-loop acceleration (`c35memo.py`) is ready for real-class representatives (Z=240, X=243, r=138), but it needs
   hours per run.
3. **Thread 3 R5 type.** The same super-cycle question, for a counter with additive R1. It needs a follower generalised
   to r -> alpha r + beta.
