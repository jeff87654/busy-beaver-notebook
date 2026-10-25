# BB(8) m7-subtree NOBOUNDARY machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE

Opus retry (inv-m7-0RB0LC-opus, 2026-10-07). Scratch and tools: `bb8_list/investigations/bb8_m7_0RB0LC_ctl/`.
The two earlier reports follow as appendices: the Opus structure analysis and the Sonnet first pass. Their description of the
orbit stands. Their verdict ("strong evidence, not proved") is superseded.

## Verdict

**Never halts. PROVED: `check.py` PASS.**

    PASS BB8_m7_1RB0RA_0RB0LC.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE never halts (machine-checked, no axioms)

- **Proof file.** `bb8_list/proofs/BB8_m7_1RB0RA_0RB0LC.v` (27 KB).
  - It replaces the earlier partial file. Its 407 rule lemmas are no longer needed.
  - The old file is kept as `bb8_m7_0RB0LC_ctl/old_partial_BB8_m7_1RB0RA_0RB0LC.v`. Its generators are in
    `bb8_m7_0RB0LC_opus/gen2/`.
- **Compile.** 464 s with coqc 8.20.1 at Idle priority (`final_compile.log`). Almost all of it is two `vm_compute` runs of the
  check: once in the tactic and once in the kernel at `Qed`.
- **Record question.** No record: the machine never halts.

## The closed family P (an n-gram closed position set)

A configuration (state q, scanned symbol m, left side l, right side r) is in P when three conditions hold:

1. **Left windows.** Every window of 10 consecutive cells of l, at every offset, is in a fixed set LS of 867 windows. Windows
   are read from the head outwards.
2. **Right windows.** Every window of 14 consecutive cells of r is in a fixed set RS of 1216 windows.
3. **Local configuration.** The tuple (q, m, first 10 cells of l, first 14 cells of r) is in a set C of 2,856,392 local
   configurations.

P is closed:
- The blank start is in P.
- No member of C scans H/0, the only undefined transition.
- Every member of C steps into C. After a move, one unknown cell enters the far end of the shifted window. Both values of that
  cell are tried, and a candidate is kept only if its window is in LS or RS.

This is the NGramCPS decider of the BB(5) proof, rebuilt for busycoq's 8-state setup:
- **`check`** is a boolean test of the closure conditions.
- **`nonhalt_of_check`** proves `check LS RS C = true -> ~ halts tm c0` for every LS, RS and C. The proof goes through
  `inv_step` and `inv_init`, then busycoq's `progress_nonhalt`. It is about 150 lines and uses no axioms.
- **Data.** LS and RS are embedded as data: 2083 positive keys.
- **C is not embedded.** `bsearch`, a depth-first search from the blank tape with at most 2^23 steps, recomputes it inside Coq.
  `check_ok` then runs `check` on the result by `vm_compute`.

### Window lengths

Lengths were scanned with `ngcps2.exe MACHINE nL nR`. The 14-cell right windows are essential.

**Lengths that fail** (a halting local configuration becomes reachable):
- symmetric n = 3..13 (n <= 10 by the previous agent; 11, 12 and 13 here);
- nL/nR = 6/14, 8/14, 9/14, 9/15, 9/16, 10/12, 10/13, 11/13, 14/6 and 14/10.

**Lengths that close:**

| nL/nR | local configurations |
| --- | --- |
| 10/14 (minimal) | 2,856,392 |
| 10/15 | 4,374,104 |
| 10/16 | 6,694,239 |
| 11/14 | 4,970,435 |
| 12/14 | 8,668,966 |
| 14/14 | 27,205,746 |

The joint set C is necessary. A product form, with independent left and right window sets per (q, m) (`ngprod.cpp`), fails for
every length up to 20/20.

## Approaches that did not close

The order follows the brief.

1. **Family of macro-configurations (round catalog).**
   - **Tool.** `rounds.exe` diffs consecutive B-frontier tapes (head in state B on the blank right of the tape).
   - **Finding.** Every round is a local rewrite at a turning point, plus a shift of the accumulator `(10)^k` and of the tail.
     The tape left of the turning point is untouched.
   - **Data.** The faithful orbit (K = 1591 and the third-epoch start `[0,3,1^2413]`) was rerun with `shadow2.py` and `DUMP=`.
     Its literal stretches over about 550 events (`dump/`, `catalog.py`) gave 154 distinct round shapes, still growing.
   - **Tail forms.** The forms in front of the final `1| 1.` include `8|`, `3| 6|^j`, `3| 1|^k`, `9|`, `7|`, `4|`, `5| 3|^k`
     and `X|`.
   - **Why it was dropped.** An explicit P would need one lemma per round type, likely several hundred mexp lemmas.
2. **Meet-in-the-middle tape languages** (left summary, q, m, right summary).
   - **mxdys `RWL_mod`.** Settings n = 1..3, H up to 24, tail anchors tH 2..10, maxT up to 3e7. All failed.
   - **mxdys `NG` with tail anchors.** Also failed.
   - **Own searchers.**
     - `rctl` uses run-length summaries.
     - `tctl` uses run-token summaries with repetition counts.
     - `nctl` uses cell n-grams with exact anchors at the tape ends; it was also seeded at step 2133.
     - With small windows they hit spurious halts; with larger windows they do not converge (20M abstract configurations,
       20k side states, still growing).
   - **Failure mode.** The left and right summaries recombine transient patterns (for example `000` left by an A-sweep) into
     unreal tapes.
3. **"Chaos left of the tail" model** (`chaos.py`). An arbitrary left part with an exact tail window is not closed: a G0 at
   the boundary followed by H reading 0 already halts.
4. **Plain NGramCPS with long windows: closes** (the method above).

## Reproduction (scratch dir `bb8_m7_0RB0LC_ctl/`; g++ -O2 -std=c++17; python = venv311)

- **Closure search.**
  - Command: `ngcps2.exe 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE 10 14 cert_10_14.txt` (about 2 s).
  - It prints `NONHALT nL=10 nR=14: 2856392 configs, 867 left windows, 1216 right windows`.
  - With `NOC=1` only the window sets are written.
- **Coq file.** `python gen_ngcps_v.py cert_10_14.txt OUT.v 23` writes the proof file exactly as committed.
  - `test_proof.v` is a smoke test with small fuel. It compiles in about 25 s and shows `Print Assumptions nonhalt_of_check`
    = closed.
  - `test_t18.v` is a timing probe: fuel 2^18 gives 325,961 configurations in 8.7 s of `vm_compute`.
- **Other tools.**
  - `ngprod.cpp`: product-form test.
  - `rctl.cpp`, `tctl.cpp`, `nctl.cpp`: MitM searchers.
  - `rounds.cpp`, `catalog.py`, `shapes_lib.py`: round catalog.
  - `chaos.py`, `tailvisit.py`, `tailvisit2.py`, `sync.py`: tail experiments.
  - `rend.cpp`: right-end window census.
  - `runmx.py`: mxdys decider runner.

## Cost

About 520k tokens.
- About 60%: the round catalog and the CTL experiments that did not close.
- About 25%: Coq.
- About 15%: report and bookkeeping.
- CPU: up to 8 Idle-priority processes for about 3 hours in total. All were stopped.

---

# Appendix A: the earlier Opus report (orbit structure; its "not proved" verdict is superseded)

Opus continuation (inv-m7-0RB0LC, 2026-10-07). Scratch: `bb8_list/investigations/bb8_m7_0RB0LC_opus/` (tools listed at the end).
The earlier Sonnet report is kept below as an appendix; where it disagrees with this section, this section wins.

## Verdict (earlier, superseded by the PASS above)

**Record question: NO record.** The second epoch of the real orbit does not end in a halt. Followed from the configuration the run
actually reaches (n = 11 old digits, K = 12B+7 degraded digits with K = 1591 mod 3528), the second epoch ends in a rebuild into a third
epoch, the champion-type list `[0, 3, 1^N]`, r = 2 (N astronomically large), tail `1^8 (00 1^6)^j 00 1 00 1` (j huge). There is no halt
in the second epoch, at its end, or in the part of the third epoch that was followed.

**Halting: never halts, STRONG EVIDENCE, NOT PROVED (no check.py PASS).**
- The only halting mechanism found is a right end `11 00 1 00 1` (run notation `2| 1| 1.`). It halts within 57 steps.
- Random searches over 120,000 reachable-like configurations found 755 halts. Every logged halt has this ending: all 239 halts of
  the fully logged search (hsearch4, 40,000 configs) and the 160 logged halts of hsearch3.
- The real dynamics never create it. Segments in front of the final `1| 1.` are only 8 or 6, and rebuilds create X = 3m+4 or no X.
- The machine is an unbounded tower of champion-like epochs: list -> clearing -> failure events -> rebuild into a much larger list.

The Coq file is extended (see "Coq status"). It still has no `nonhalt` theorem, so check.py does not pass it and there is no README row.

## Notation (run notation, used everywhere below)

A tape is written as its 1-runs: `k` = k ones followed by one 0, `k|` = k ones followed by 00, `k.` = the last run. `1^m` = m single
ones (each followed by one 0), `(1|)^K` = K "digits" `1 00`. Tokens D(m) = (10)^m 1 as in the champion. A B-frontier configuration
(head in B on the blank right of the tape) is parsed as `Q | list | tail`. The **list** is the segment after the last 00 before the tail,
parsed as D(t1)...D(tk) (10)^r 1^h. The champion prefix 11 is the tokens [0,0]: 11 = D(0) D(0). The **tail** is the pure 1-runs after it.
- Champion (first epoch): list [0,0,t1..tk], tail T0 = h=3, [1] (`111 00 1`).
- Second and later epochs: tail T1(j) = h=8, [6^j, 1, 1] (`1^8 (00 1^6)^j 00 1 00 1`).
- Examples: K0(n,b) = [0,0,1^(n+1)] r=3b+2 T0. M3 = `1^2 3| (1|)^(12b+7) (3n+7)| 1| 1.`

## Rules (each checked literally; "stable tail" = T0 or T1(j))

| rule | statement (tokens left to right, a-token last) | literal check |
|---|---|---|
| R1 | [.., m] r -> [.., m-3] 2r+4, m >= 3 (also 3 -> 0) | rulechk.py: 52 random configs with Q prefixes and all stable tails, 0 mismatches |
| R2/R3 | a-token 1: nearest token x != 1 with x >= 3 becomes x-3, the token right of it becomes 2r+3, r := 2 | same |
| R0 | a-token 0: [.., x+4, 0] r -> [.., x, 2r+3] 2 | same |
| R0' | [.., x+4, 0, 1^(k+1), 1] r -> [.., x, 2r+3, 1^(k+1), 1] 2 | tl.py checks; Coq lemma R0b |
| A2 | a-token 2: [.., x+3, 2] r -> [.., x, 2r+2, 2, 1] 2 | tl.py; Coq lemma A2 |
| D2 | [.., x+5, 2, 1] r -> [.., x] 4r+10, one more tail block (j+1) | tl.py (r = 1..6, x = 0..7); Coq lemmas D2a, D2b, D2 |
| failures | borrow reaches a 0/2 token or the list's left end (00 or blank): rebuild-type events, see below | shadow runs |

Every huge number in the orbit enters these rules only through residues. Towers stabilize: every accumulator produced by a clearing of
depth >= 2 is 20 mod 504.

## The real orbit (n = 11)

1. **Epoch 1** is the BB(7) champion on the 11-digit list. It ends at K(0^11; 0; B) with 2B+4 = 2^(13 arrows) 3.
   - Tower arithmetic (`towermod.py`) gives B = 1 mod 5, B = 6 mod 7, B = 6 mod 504.
   - Hence K = 12B+7 = 1591 mod 3528.
2. **R4A + M2 -> M3** (literal for n = 11, b = 0, 1, 2; Coq for R4A): `1^2 3| (1|)^K 40| 1| 1.`
3. **Digit-processing start**, the same for every K >= 19 (checked K = 19, 20, 31, 60).
   - The 40-run is split.
   - The digit block becomes K-9 zero tokens: `Q = 3 1^6 2^(K-9) 3 1^6 1| 5 1 1|`.
   - The first list is [2,8,1^4] r=2, which the champion clears to [2,2,1^4].
   - A short chain of failure events follows: [0^4, 2R+6, 2, 1] r=4, then D2, then A2.
   - At the end the zero tokens are turned back into K-12 digits.
4. **Seven-digit cycle.** Each cycle absorbs 5+1+1 digits and appends one token 94 (= 1 mod 3, a champion digit 31) to a list in Q:
   `[] r=45 -> [2,1] r=2 -> [8] r=2 -> (R1) [2] r=20 -> [] r=45`.
   About K/7 tokens are built this way: the "second list" of the Sonnet report.
5. **End of the digit block** (depends on K mod 7 and finer residues). The second list becomes active:
   - it is `[0,0,4,9,6,x,y, 94^q, 95, 90]`;
   - each 94 is consumed by one R0' borrow plus 30 champion borrows (the Ackermann recursion of the second epoch);
   - then nested failure events, a smaller nested digit block, and a long A2/D2 alternation follow (each pair lowers one token by 3 and
     adds 2 tail blocks).
6. **End of the second epoch:**
   - the chain is `[0,0,4,7,0,2] r -> [0,0,1,2] r' -> ... -> [0,3,1^N] r=2, T1(j)`;
   - this is a rebuild, i.e. the start of the third epoch: a champion list with N zero digits and one digit 1;
   - the third epoch starts by clearing it, which exhausts at the left end and rebuilds again into nested digit blocks.

How it was followed (`shadow2.py`):
- **Champion steps are applied symbolically, modulo 504** (`clearmod.py`).
  - Numbers below 504 are exact. Huge numbers are kept as representatives in [504, 1008).
  - The steps are R1 chains, R2/R3 borrows, and whole clearings of a borrowed token through k lower levels, iterated q times (cycle
    detection; all cycle lengths divide 168).
- **Every other situation is simulated literally** (fsnap.exe, exact TM) up to the next configuration with a stable tail.
- **The digit count K is a representative chosen to match the real residue.** It is 1591, the same as the real K mod 3528.

Checks:
- **Representatives.** With representatives in [1008, 1512), K = 282 gives the same event sequence, with the rebuilt block 4r-3
  shifted as expected.
- **Sweep.** The 14 residues K = 282..295 follow different routes after the digit block ends (the R0' route, long A2/D2
  alternations that add about 150-300 tail blocks, or period-3 token lists). Over about 9,100 shadow events none halts.
  - K = 282, 288, 292 reach the third-epoch rebuild `1^2 3| (1|)^(4r-3) 1| [0,1,2,1]`.
  - K = 286, 287, 289, 293, 295 reach the rebuild `[0,3,1^N]`.
  - The other six were still inside long phases at the event cap of 420-600.
- **Faithful run.** K = 1591 reaches `[0,3,1^2413]` at event 723. It was then followed for 975 more events into the third epoch, which
  has nested digit blocks.

## Why it does not halt (the mechanism)

- **Where the halt is.** H0 is the only halt and H is entered only through G0, so halting means F reads 0 with 00 to its right.
  - F reaches such a spot only through an F0/G1 chain started by a B1 event.
  - With the right end `1 00 1`, such a chain stops at the 00 (the G0 H1 E0 lockstep seen in every round).
- **Which endings are dangerous.** `tailgrid.cpp` tried endings h + tail.
  - h = 1 or 2 is dangerous.
  - A final segment 2, 4 or 5 is dangerous.
  - `2| 1| 1.` is dangerous.
  - Endings `8| (6|)^j 1| 1.`, `3| 1.`, and `X| (6|)^j 1| 1.` with X != 2 are safe.
- **Random searches.**
  - hsearch2: 3000 configurations with stable tails, no halts.
  - hsearch3 and hsearch4: 120,000 configurations including rebuild-like ones, 755 halts. Every logged halt (all 239 of hsearch4,
    and the first 160 of hsearch3) ends in `2| 1| 1.`.
- **What the real events produce.**
  - The segment in front of the final `1| 1.` is h = 8, a 6-block, or a rebuild value X.
  - Rebuild values are X = 3m+4 (4, 7, 10, ...). This was checked for every failure type in the catalog (`[0,0|0,1, 1^m, a]`, a = 0, 1, 2)
    and seen in all shadow runs. Some rebuilds have no X at all.
  - None of these endings is in the dangerous set.

## Correction to the Sonnet report

- For n = 0 the second epoch is a single token 93 (= 0 mod 3). Its end, [0,1,0] r, rebuilds into
  `1^2 3| (1|)^(4r-1) 7| 6| 1| 1.` (a third epoch), not a halt.
- For the real n = 11 the second epoch is not one ladder. It is the digit-processing machine described above.
- The "borrow seen once" for n = 1 is the standard R2/R3 (or R0) on these tokens.

## Coq status at that time (the partial file, now replaced; copy in `bb8_m7_0RB0LC_ctl/old_partial_BB8_m7_1RB0RA_0RB0LC.v`)
- The file is 274 KB with 407 lemmas. It compiles in place: `coqc` exit 0 in 602.6 s at Idle priority (Coq 8.20.1); log in
  `gen2/final_compile.log`.
- **Contents.**
  - R4A, from the Sonnet run.
  - R1/R2/R3/R0 for tail T0 and for tail T1 j (j free), each for all values of the variables (`gen2/gen_rules.py`, explored in
    0.2-1.4 s each).
  - R0b (borrow through a 0 token), A2 (a-token 2) and D2. D2 is proved from D2a (start to the h=9 waypoint) and D2b (an R1-like
    round to the target), joined by `progress_trans`.
  - All lemmas were generated by the mexp explorer.
- **Not proved:** init_reach, the champion epoch, M2 -> M3, the digit-processing and rebuild events, and the abstract glue.
- **check.py output (verbatim):** `FAIL BB8_m7_1RB0RA_0RB0LC.v: need exactly `Theorem nonhalt : ~ halts tm c0.` or `Theorem halt : halts tm c0.``
  This is expected, since the file has no theorem; it is not added to the README table.

## Precise remaining gap

1. **A family that covers every epoch.**
   - Q is a nested list of digit blocks and token lists; each epoch adds nesting.
   - Then one lemma per event type. The catalog in `shadow2` logs has about 15 types.
   - Then the abstract glue with residue invariants (mod 504 and mod 3528) and an induction over epochs.
2. **The failure events are not yet machine-level lemmas.**
   - Missing: the digit-cycle events, the rebuilds `[0,0|0,1, 1^m, a] r -> (1|)^(4r+c) X| ...`, and the a-token-2 event at a list
     boundary.
   - R0a ([x+4, 0, 1] r) is also missing. The explorer loops on it, so it needs a waypoint as D2 did.
3. **M2 -> M3** (the Sonnet gap) is still literal only; it is verified here for n = 11, b <= 2.
4. **An alternative route:** a closed-language (CTL) proof that the right end never becomes `2| 1| 1.`. Plain n-gram CPS fails for
   n <= 10 (`ctl/ngcps.cpp`), and the mxdys portfolio did not run on this build.

## Reproduction (scratch dir bb8_m7_0RB0LC_opus/; C++ with g++ -O2 -std=c++17 -static, python = venv311)

- **Run printers:**
  - `tsnap.exe` / `tshape.exe MACHINE RUNSPEC N`: run-structure snapshots, shape changes only.
  - `fsnap.exe MACHINE RUNSPEC N [hmin] [maxQ] [ncfg]`: family parse `Q g= T[..] r= h= tail[..]`.
- **Rule probes:** `python tl.py "toks" r [h] [tail] [n] [steps] [Qword]`; `python rulechk.py SEED N`.
- **Shadow orbit:** `NORESET=1 COMPACT=70 python shadow2.py "1^2 3| (1|)^1591 40| 1| 1." 3000`.
  - Logs are in `sweep/K*.txt`; `sweep/K1591.txt` and `sweep/K1591_b.txt` are the faithful run.
  - `python condense.py LOG` collapses periodic stretches.
- **Halting-mechanism searches:** `hsearch3.exe` and `hsearch4.exe MACHINE SEED N STEPS`, `tailgrid.exe`.
- **Residues:** `python towermod.py`.
- **Coq generators:** `gen2/gen_rules.py OUT.v T0|T1`, `gen2/gen_events.py OUT.v [R0b A2 D2a D2b]`, then
  `gen2/merge.py BASE OUT r_t0.v r_t1.v ev.v`.

## Cost
About 670k tokens and about 200 tool calls.
- About 250k: structure (run notation, family parser, rule and event probes, halting-mechanism searches).
- About 200k: the shadow driver, modular clearing, and the K sweep.
- About 120k: Coq generation, merge and compiles.
- About 100k: report and bookkeeping.
- CPU: up to about 16 Idle-priority processes for about 2 hours. All of them were stopped.

---

# Appendix: the earlier Sonnet report (unchanged; superseded where the Opus section above disagrees)

Scratch dir: bb8_list/investigations/bb8_m7_1RB0RA_0RB0LC/ (literal tools in the root, explorer scripts in gen/).
Partial proof: bb8_list/proofs/BB8_m7_1RB0RA_0RB0LC.v (compiles; lemma R4A only; no nonhalt theorem; NOT in the README table).
Investigator: Sonnet 5.5, about 330k tokens, about 115 tool calls.

### Verdict

**UNRESOLVED. Not proved (no check.py PASS). No halt was observed anywhere; the structure found is a nested champion-like recursion, not a cycler.**
Not a record claim: no halting run exists, and the halting pattern (below) never occurred in any run.

Answer to "what does the used-up list do?": the first epoch is the BB(7) champion's (E0, G0 and H are never read in R1-R3). At the exhaustion
K(0^n;0;b) the machine does NOT rebuild a clean K list (unlike the champ12/m7 rebuilders) and does NOT enter a cycler (unlike the sibling
1RB0RA_..._1RH1LG, whose proof is finished). It rebuilds a **degraded list** M3 = (10)^2 111 (001)^(12b+7) 00 1^(3n+7) 00 1 00 1 and then runs a
**champion-like ladder** (R1 with accumulator r = c+7) on tokens of that list, forever as far as any run can show. The end of the second epoch
(halt / rebuild again / bouncer) is not reachable by simulation (Ackermann timescale) and I found no family description for it.

### Machine facts (exact, from the table)

- Transitions: A 1RB 0RA | B 1LC 1LF | C 1RD 0LB | D 1RA 1LE | E 0RB 0LC | F 1RG 1LD | G 0RH 0RF | H --- 0RE.
- **Halt condition (H0 is the only halt).** G is entered only by F0 = 1RG. F is entered by B1 = 1LF (then G meets the 1 that B just left behind: no halt) or by G1 = 0RF.
  So H0 is read iff the head in F reads 0 at p with p+1 = p+2 = 0; equivalently G reads a 1 at q and q+1, q+2, q+3 are all 0
  (for instance E0 at q-1 followed by B reading the LAST 1 of the tape, blank beyond: B1, F0, G1, F0, G0, H0).
  The normal R4 path is G0 (0RH), H1 (0RE), E0 (0RB): it erases the 1 of a "0 1 0" pattern and needs a 1 three cells after the G-read 1.
- Literal usage from K(0^11;0;0), 2e8 steps (usage.cpp): G0 = 12269, H1 = 12269, E0 = 12273 (the 4 extra E0 are at the start), **H0 = 0**; G0, H1, E0 occur in lockstep
  (every G0 is followed by H1, then E0). The same pattern persists in the ladder phases: E0 is used in every round there (so the ladder is not the plain champion R1,
  which never reads E0).

### Stage R4A (first stage of the exhaustion): machine-checked for all n, b

K0(n,b) = 0^inf 11 (101)^(n+1) (10)^(3b+2) 111001 B>  (n zero digits plus the a-token 0, i.e. the champion K(0^n;0;b))

    R4A:  K0(n,b)  -->+  M2(n,b) = (10)^(6b+4) 0 111 (001)^(n+3) B>      in  36 b^2 + 252 b + 166 + n (48 b + 36)  literal steps

- Literal: exact snapshot match for n = 0..4, b = 0..3 (m2chk.py, 20 cells, the step formula fits all 20).
- Symbolic: mexp.explore(START, M2) succeeds in 0.1 s (gen/x1.py): three loops on b, and a loop on n with a nested loop on b.
- **Coq: lemma R4A (forall b n) compiled** (gen/gen_r4a.py -> gen/r4a.v, 100 s at Idle priority; copied with a TODO header to proofs/BB8_m7_1RB0RA_0RB0LC.v).
- Same M2 shape as the sibling used-up transient (its U1/U2 target (10)^(6b+4) 0 111 (001)^14 is the n = 11 case), but the two machines differ at F1 and the literal
  runs from K0 differ from step 8 on (cmp.py), so the sibling later lemmas do not transfer.

### Stage 2: M2 -> M3 (literal only)

    M3(n,b) = (10)^2 111 (001)^(12b+7) 00 1^(3n+7) 00 1 00 1 B>   reached after 324 b^2 + 888 b + 562 + n (48 b + 58) steps  (n = 0..4, b = 0..3: 20 cells exact, m3chk.py)

(12b+7 degraded zero digits "001" and a stack of 3n+7 ones from the old n digits; for the real orbit n = 11: 1^40.) The symbolic crossing of the run (10)^(6b) after M2
(gen/x2.py) works for nine round-loops and then stops at  0^inf 1 1 (10)^(6b) <C (110)^k 0 0 1 0 0 1 0 (010)^n 1  (C bounces at the end of the run): the same obstacle as in the
sibling. The result of the direct M2 -> M3 exploration (gen/x3.py) is at the end of this report.

### The ladder (second epoch), literal facts

From M3 the machine runs a chain of B-frontier rounds. In the n = 0, b = 0 orbit (list of 7 degraded digits) the tape at B-frontier snapshots is

    11 0 11 (01)^x (10)^y 11 (01)^z 00 1^8 00 1 00 1  B>      (first one with x = 93 = 12*7+9 at step 18878, y = 5, z = 1)

Rounds: (x,y,z) -> (x, y-1, z+2), cost proportional to the tape length (quadratic in total); at y = 0 the token drops: x -> x-3 and c = 2y+z -> 2c+11. Data (n = 0, b = 0): c = 77, 165, 341, 693, 1397
at x = 87, 84, 81, 78, 75. With r = c+7 this is exactly the champion R1 (m, r) -> (m-3, 2r+4). Left of the active token sit more tokens (1 D(1) D(x)... with D(m) = 1 (01)^m).
The n = 1, b = 0 orbit shows the same ladder on the second token ((10)^y: 19, 16, 13, 10, 7, 4 over 4e9 steps, each phase about 4x longer) with the first token 6 waiting
(n1b0_long.txt). Growth is Ackermann-type: after the a-token reaches 1 the borrow (R2/R3 analogue) should refill the a-token with about 2r+3, so the next chain is astronomically long
(the borrow itself was not reached literally, see the end note).
Probes from boundary-like tapes  11011 (01)^x 11 (01)^z 0011111111001001  (x, z = 0..12, 169 starts, 1e7 steps): no halt; small x start new ladders (token about 22-25) and
blocks "(01)^94 (10)^94 11" (the constants 93/94/95 appear for every z) or "(01)^4 (10)^4 11" (x = 4: a growing bouncer, width about sqrt(t)): a multi-level recursion, not a single cycler.

### Evidence of non-halting (all literal, none a proof)

- sim9.exe, 2e10 steps each from K0(0,0), K0(11,0), K0(11,1): no halt (long_*.txt; at 1e10 steps width 1.8e5, ones 9e4; for n = 0 the token falls 93 -> 57).
- 169 ladder-boundary starts x 1e7 steps: no halt.
- The halting pattern needs "G reads a 1 followed by 000"; it never occurred in 1.2e4 G0/H1/E0 lockstep events.
- The earlier probes (bign_all.tsv: n = 11..49, b in {0,1,2,3,4,5,8,13}, 2e7 steps: NO-HALT) are consistent but only reach the first ladder phases.

### Variants (E0 = 1LG, E0 = 1RG; same G0, H, F)

They are NOT token-level identical to the target. B-frontier snapshot sequences (first 800 snapshots, n = 0,1,2,3,5,11, b = 0,1,2): E0 = 1RG equals the target for n = 0, 3, 11
(all b tested) and for n = 1, 2 with b >= 1, but differs for (n,b) = (1,0), (2,0), (5,b); E0 = 1LG equals the target only for n = 0 and (1,1), (1,2), (2,1), (2,2) and differs from
snapshot 10 on for n = 11. Not investigated further; no proofs written for them.

### Borrow seen literally (n = 1, b = 0, snap.exe to 1.9e10 steps, n1b0_long.txt)

The second token (10)^y went 19 -> 16 -> 13 -> 10 -> 7 -> 4 -> 1 and at step about 1.6e10 the tape is  11 0 11 (01)^6 1 0 11 (01)^52225 (10)^75764 0 1^8 00 1^6 00 1^6 00 1 00 1 :
the a-token seems to have reached 1 ("1 0") with the first token 6 = (01)^6 to its left; the expected next event (not yet seen: the snapshots up to 1.9e10 still show inner rounds) is the champion
R2/R3 borrow (6 -> 3, a-token about 2r+3 with r about 2e5), after which the chain is about 6e4 phases long. So the n = 1 run looks like a second copy of the champion recursion on the degraded list; its end is not reachable.

### Precise remaining gap (for an Opus continuation)

1. Stage M2 -> M3 as a machine-level lemma (the waypoints are exact; the plain explorer is stuck at the C bounce unless aimed at M3; see the end note), then M3 -> the first ladder
   configuration (for n = 0 the first token is x = 93 = 12K+9 with K = 7, so presumably x = 12(12b+7)+9 = 144b+93; the rounds (10)^y 11 (01)^z are an inner loop over y).
2. A family for the second epoch: tokens D(m), accumulator c with r = c+7, tail 1^8 00 1 00 1 (n = 0) or 1^8 00 1^6 00 1^6 00 1 00 1 (n = 1, 2; depends on the old digits), rules R1
   (verified numerically only), R2/R3/D2 borrow analogues (borrow seen once, above). The sibling proof (proofs/BB8_m7_1RB0RA_1RH1LG.v, opus/glue.v.in) is the model for the glue.
3. The fate at the end of the second list (halt / rebuild / bouncer) and an invariant excluding "G reads 1 followed by 000". Without it the record question (a halt after a rebuild
   of size 12b+7 with b of champion size) stays open: such a halt would be far beyond 2^^11 2^^11 3; nothing in the literal runs suggests it.
4. init_reach: blank -> K(2,0^10;0;0) at step 2133 (watcher), then the champion epoch; the proof needs the champion rules R1-R3 on this machine (same engine as the sibling and champ12: gen_all.py and
   gen_rules.py regenerate them for any transition table; not done here).

### Reproduction (python = third_party/venv311/Scripts/python.exe; C++: C:\msys64\ucrt64\bin on PATH, g++ -O2 -std=c++17 -static)

- snap.exe MACHINE WORD HEAD B N FAC FIRST : RLE tape at B-frontier snapshots (geometric sampling). K0 word = 11 + 101*(n+1) + 10*(3b+2) + 111001, head = word length.
- usage.exe MACHINE n b N : transition usage and first-use steps. shape1.exe: first ladder-shaped snapshot. m2chk.py, m3chk.py, kstage.py, cmp.py: exact waypoint and variant checks.
- grid_x.py MACHINE N : 169 ladder-boundary starts through sim9.exe.
- gen/x0.py (symbolic walk from K0), x1.py (K0 -> M2 exploration), gen_r4a.py + coqc_idle.py (the R4A lemma), x2.py (after M2), x3.py (M2 -> M3 attempt).
- Proof file: proofs/BB8_m7_1RB0RA_0RB0LC.v compiles (94.6 s at Idle priority, exit 0); it has no nonhalt theorem, so check.py would FAIL it and it is not in the README table.

### Cost

About 340k tokens, about 120 tool calls: 70k reading the sibling/record/rebuilder material, 130k literal exploration (the K parser of the sibling fails here because the
ladder tail is not 111001), 60k explorer and Coq for R4A, 40k variants, checks and this report.

### End note: the M2 -> M3 exploration (gen/x3.py) FAILED, and why

mexp.explore(M2, M3) stops, after the nine crossing loops, at  0^inf 1 1 (10)^(6b) <C (110)^k 0 0 1 0 0 1 0 (010)^n 1  with "stuck without loop" (same as x2.py).
The literal M2 -> M3 stage (turns.py n b thr prints the tape at every sweep reversal) is a left-end bounce loop exactly like the sibling Z-stage: for n = 0, b = 1 the reversals at the
left end are at steps 506, 600, 684, 770, ... (about 80 steps each) with tapes

    11 (01)^x 00 1 0 11 (0 11)^k 00 1 00 1 0 1  (state D)   /   111 (01)^x 00 1 0 11 (0 11)^k 00 1 00 1 0 1  (state A)       x = 10, 9, 8, ..., 4 (x starts at 6b+4), k grows by 1 per round

(the run (10)^(6b+4) of M2 is eaten one unit per bounce and a block 0 11 is appended on the right), then a long sweep (step 1334 -> 2038) rebuilds the (001) list and ends at M3
(step 1774 is the B-frontier snapshot M3 for b = 1). So the missing machine-level piece is, as in the sibling proof (opus/gen_tr.py, ZR + hand induction ZIT), one round lemma
Z(x+1,k) -->* Z(x,k+1) for general x,k plus the hand induction and the exit sweep; the waypoints above are literal and exact for the n = 0, b = 1 orbit (check the other (n,b) with turns.py first).
