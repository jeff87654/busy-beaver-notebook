# Halt redirect of the BB(9) record at 10 (and 11) states: structural answer

Opus investigator inv-bb9rec-redir10, 2026-10-07/08. Scratch: `halt_redirect/r10/` (tools, tables), `r10/n11/` (11-state slice).
Base: BB(9) record `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---` and its twin `..._0RH0RE_0LH---`.
Scope after the lead's redirect: the NMAX=10 space belongs to the other session's inv-bb10-rec9-ext (`bb10_rec9_ext/`);
this report answers the structural omega-level-2 question with targeted literal experiments and enumerates the 11-state
slice that the answer points to. My early NMAX=10 follower runs (copied pre-fix fext.py, start state B) are discarded.

## Verdict
- **No BB(10) record candidate found.** At 10 states, the gadgets that can reach omega-level 2 provably never halt.
  The 10-state gadgets that can halt stop exactly at the event where the level-2 rebuild would happen, except for one
  route (the true left-end REBUILD) that only the other session's follower can settle.
- **The level-2 mechanism exists and is concrete.** A one-transition J gadget can "repair" the record's REBUILD at an
  internal D0 block. The repaired event turns the accumulator into the length of a list of ones, about 2*min(r, X),
  where X is the token left of the block.
- **At 11 states there is one machine that combines the mechanism with a reachable halt** (machine C below). It halts at
  roughly one D2 event in six. Whether its real run rebuilds at level 2 before such an event is undecided. It would be a
  BB(11) item, not a BB(10) one.

## 1. Structural facts (exact, from the transition table)
1. **I is entered only by E0 = 1LI.** E is entered by D1 = 1LE or H1 = 0RE.
   - Via H1, H wrote 0 at the cell I then reads, so I reads 0 (I0 = 0LH, the champion rules).
   - Via D1, D was entered from C0 = 1RD or F1 = 1LD. Via C0, E reads the 1 that C wrote (E1, not E0).
   - Hence every I1 event (the record's halt and every later redirect event) is the path F1 -> D1 -> E0 -> I1.
     With p = the cell where I reads 1, the cells p+1, p+2, p+3 all hold 1 (written by E0, D1, F1).
     The cell p-1 and everything further left vary with the event.
2. **Consequence for I1 = xRJ.** J reads p+1 = 1, always. So J0 is unreachable unless J's own transition re-enters J.
   - Every 10-state extension with I1 = xRJ, J1 -> an old state and J0 undefined never halts. This is a proof: its only
     undefined transition is unreachable.
   - With J1 undefined it halts one step after the old halt, with the record's score.
3. **Consequence at 11 states for I1 = xRJ, J1 = yRK.** K reads p+2 = 1, always, so K0 is unreachable. Such machines either
   halt at the first event (K1 undefined) or never halt. This settles that whole 704-machine slice (section 4).

## 2. The level-2 engine at 10 states (never halts)
An event probe ran the old machinery plus each gadget on literal event words, in the follower convention:
`D(0)^2 [4 21 2] D(X) D(Z) D(1)^k D(1) D(r) D(0)^6 (100 D(0)^5)^7 100 100`, with state A at the right end.
- Blocking token Z is D2, D3 or D0. The parameters were k = 0..30, r = 8, 14, 20, 26 and X = 38 (also 36, 37, 13, 7, 4, 1).
- The tool is `r10/src/hyb10b.exe`: hyb10 with an in-process batch driver. Spawning one hyb10 per job was CPU-starved by
  process-creation overhead on this PC.
- Output: `r10/bp_all.tsv`, 83,700 runs over the 225 non-halting 10-state extensions.

Five gadgets per base give identical outputs at every probed event; call them "the engine":
`I1=0RJ, J1=1LD`; `I1=0RJ, J1=1RB`; `I1=1RJ, J1=0LA`; `I1=1RJ, J1=0RA`; `I1=1RJ, J1=1LG` (J0 undefined).
Each is one fixed tape edit followed by an old state, since the cells it touches are the known 1s of fact 1.

The engine's event maps, from literal runs (`r10/bp_a.tsv`, `r10/bp_all.tsv`):
- **D0-block event (internal left end).** The record itself halts here (I reads 1).
  - The engine gives `[.., X, D0, 0^k | r] -> [.., X-r-1, D0, D4^(2r+k-3), D1 | D40 D8]` while r < X.
    Exact for X = 38, 37, 36 and r = 8..32, for example X = 38, r = 20 gives `17 0 4*37`.
  - When r > X it eats X and then the left context. The list stops at about 2X+k and the rest of r becomes a token,
    for example X = 38, r = 50 gives `4 16 25 4*77`.
  - **The list length is about 2*min(r, X).** With X and r both huge (omega-level 1), clearing this list is an
    omega-level-2 step.
- **D3 event.** `[.., X, D3, 0^k | r] -> [.., X, D0, D(2r), D4^(k-2), D1]`. This puts a D0 directly right of X. After the
  short list clears, the next event is a D0 event with neighbour X.
- **D2 event.** `[.., X, D2, 0^k | r] -> [.., X-2, D(2r+c), ...]`, depending on k mod 5 and mod 25.
  - X-2 has residue 0 when X has residue 2, as for D(2R2-2).
  - It later counts down to D3. That gives the D3 then D0 sequence next to its left neighbour.
- **Route to level 2 in the real run (argued, not followed).**
  - The real list holds D(2R2-2) (huge, residue 2) and later accumulator tokens D(2Rj-2).
  - A D2 event at a huge residue-2 token leaves a huge residue-0 token W.
  - W eventually hits D3. Its left neighbour is the previous huge token H.
  - The following D0 event then builds about 2*min(r, H) ones, which is omega-level 2.
- These ten machines (five gadgets times two bases) can never halt (fact 2). They are useless as candidates, but they show
  the mechanism.

## 3. 10-state gadgets that can both run the engine and halt
Only I1 = xLJ lets J read a variable cell (p-1). The engine is reproduced exactly by these gadgets:
- **A** = `..._0LH0LJ_---1RD`: I1 = 0LJ, J1 = 1RD continues, J0 halts.
- **B** = `..._0LH1LJ_---1RG`: I1 = 1LJ, J1 = 1RG continues, J0 halts.

Both exist for both bases. Evidence:
- `bp_all`: A and B match the engine at all 220 of 372 probed events where they do not halt, with 0 non-halt differences.
- They survive the real first event (p-1 = 1 there).
- Real-class grid at b = 16, 41, 216 and r = 20, 125 with budget 1e8: T.
- The variants that continue on J0 (`0RD---`, `0RG---`) halt one step after the old halt.

**The catch.** A and B halt at every D0 event with X >= 2 (`r10/bpAB.tsv`, 912 runs, four left contexts).
- The tape there is `..1010 1010 [1] 1111` with p-1 = 0, which is exactly the level-2 rebuild event.
- They continue only for X in {0, 1}: a double block, or a zero digit next to the block.
- With zeros or the true left end to the left, those events run the record's own left-end REBUILD and give lists of
  4r ones (for example context [1,1], X = 0 gives `0 3 1*(4r+4) 0`).
- They also halt at some D2 events: k = 6, 7, 16, 18, 19, 25, 30 within 0..30.
- **Open for the owning session:**
  - Does the real chain of A/B reach the true left end, after eating `[4, 21, 2]` through small-X D0 events, before its
    first big-X D0 event or halting D2 event?
  - If it does, the left-end REBUILD with a huge accumulator gives omega-level 2.
  - If it does not, they halt at omega-level 1, below the bar.
  - I flagged both classes to the lead rather than following them (not my slice).

## 4. NMAX = 11: the slices the mechanism points to
1. **Slice 1: I1 in {0RJ, 1RJ}, J1 = yRK, K with one transition, the other the halt (704 machines).**
   - Real-class grid (b16r20, b41r20, b16r125; 3e7 steps; `n11/g.tsv`): 438 halt within 1e5 steps of the old halt and
     266 run on.
   - By fact 1, K reads p+2 = 1 always. So the 266 never halt (proof) and the 438 score as the record.
   - The event probe (`n11/bp.tsv`, 38k runs) agrees: 88 run the engine and 0 have a halting event.
2. **Slice 2: engine-or-test (1408 machines).** This is A/B with J's halting slot replaced by a second test:
   I1 in {0LJ (J1=1RD), 1LJ (J1=1RG)}, J0 = yzK, K with one transition, the other the halt.
   - Grid: all 1408 run past 3e7 steps (`n11/g2.tsv`).
   - Big-X D0-event probe (`n11/bp2.tsv`): 13 rebuild at level 2. In 12 of them K reads p, which I1 fixed, so their halt is
     unreachable.
   - The one with a reachable halt is:

         C = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH1LJ_0LK1RG_---1RH   (11 states)

     I1 = 1LJ; J1 = 1RG continues; J0 = 0LK tests p-2; K1 = 1RH continues; K0 halts.
   - C equals the engine at every non-halting probed event (352/372 identical; the rest are T snapshots).
   - It rebuilds 2r+k-3 ones at big-X D0 events, exactly as the engine does.
   - It continues at every D0 and D3 event probed.
   - It halts only at D2 events. Among X = 36..38 and k = 0..105 (`n11/bpC.tsv`, `n11/bpC2.tsv`), the halting k are
     16, 18, 19, 30, 35, 43, 44, 53, 54, 55, 68, 69, 93, 94, 95. That is about 15%, with k = 18, 19 mod 25 recurring;
     it depends on 5-adic digits of k.
   - The twin-base version does not rebuild (H0 = 0RH changes the K1 = 1RH continuation).
   - **Status: mechanism candidate only.**
     - The real run makes many D2 events. Each halts with probability about 1/6 under the real 5-adic residues.
     - So C most likely halts at a D2 event before its first level-2 rebuild, at omega-level 1.
     - Deciding this needs the fixed follower (start state A, 5-adic depth 5^6, forced periods 25/125) on C's real chain.
       My tower.py gives B mod 5^j for any j: B = 202802491 mod 5^12.
   - C is an 11-state machine, so it is not a BB(10) record candidate in any case.

## 5. What was checked literally
- Record from the follower-convention D2-stage word (state A): halts in I reading 1 with ones 442/982/652 at
  b16r20/b41r20/b16r125. This matches 2*R1 + (108b+282)/5 (`n11/st.txt`).
- Early NMAX=10 literal grids, kept only as counts (the space belongs to the other session):
  - From gen.py's state-B word at b = 6..216: 400 extensions per pair of bases halt within 1e5 steps, 24 halt later with
    ones = record + O(b), and 224 run past 1e8.
  - The twin `..._0LH0LJ_---0LF` halts only for b = 11, 16 mod 25 (the real class is 16 mod 25), with record + O(b) ones.
  - These counts agree with the other session's "37 halt early, 123 followed" after deduplication.
- tower.py: B mod 18101949465600 = 16537583495166, equal to numres (independent check of the tower-residue code).

## 6. Cost
- About 360k tokens (Opus).
- CPU: about 12-15 core-hours at Idle on a saturated PC. Some of that was starved or killed: the discarded fext runs,
  and a per-process probe that spawned about 10k hyb10 processes and was replaced by hyb10b.
- Tools left for reuse in `r10/`:
  - `src/hyb10b.exe` (batched hyb10, `LABEL MACHINE @WORD HEAD STATE MAXSTEPS opts` per line).
  - `bprobe.py` (event probe over machine lists).
  - `d2map.py` (follower-convention words).
  - `tower.py` (B mod n via the infinite 2-tower).
  - `src/walk.exe` (runaway and J-visit statistics).
