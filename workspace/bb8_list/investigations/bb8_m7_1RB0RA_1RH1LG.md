# BB(8) m7-subtree NOBOUNDARY machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF

Scratch dir: bb8_list/investigations/bb8_m7_1RB0RA_1RH1LG/ (generators in gen/). Partial proof: bb8_list/proofs/BB8_m7_1RB0RA_1RH1LG.v
(compiles; no nonhalt theorem; NOT in the README table). Investigator: Sonnet 5.5, about 300k tokens, about 150 tool calls.

## Verdict

**NEVER HALTS: strong evidence, NOT proved (no check.py PASS).** Not a record candidate: there is no halt and no sigma.
The question about R4 is answered completely at the rule level, every rule is checked literally, and the machine-level Coq lemmas for all rules
except one family (the used-up transient, below) are generated and compile. The remaining gap is that one family of lemmas plus the abstract glue.

Summary of R4 (all numbers literal; the rebuild formula is proved in Coq):

1. **Rebuild (Coq, proved): K(0^n; 0; b) -->+ P-less list [6b+5, 1^(n+2)], accumulator r = 2.** The halt of the champion at E0 is replaced by a rebuild.
   First clean configuration after 36 b^2 + 432 b + 396 + n (60 b + 66) literal steps (n <= 4, b <= 7, plus b = 100).
2. The new list is processed by the same champion rules R1-R3 (now on a family WITHOUT the left end 11). The one residue-2 token T = 6b+5 behaves
   like a digit (borrowed 3 at a time). When T reaches 2 a **D2 stage** deletes it: [.., 2, 1^k] -> [2r+3, 1^(k-1)], r := 2 (no mod-5 or other
   arithmetic condition, unlike the D2 stage of the BB(9) record).
3. After that all tokens are residue 1 and the champion recursion runs until the list is used up (all tokens 1, a-token 1). The machine then
   enters a **translated cycler** (period 70 steps, two new 1s per period, the head never goes left of it) and runs forever.
   So the used-up list neither halts nor rebuilds.

Hence the whole orbit is: champion epoch on the 11-digit list (identical to the BB(7) champion; R1-R3 never read E0) -> R4 rebuild ->
Ackermann-type champion recursion on the rebuilt list -> D2 stage -> more recursion -> used-up -> cycler. E0 (the only possible halt) is never read.

## Configuration families (tape left to right; head in B on the blank right of the word, nothing to the right)

Tokens D(m) = (10)^m 1, accumulator (10)^r, tail S = 111001. K0 ds a b = 0^inf 11 D(3 d_n+1) ... D(3 d_1+1) D(3a+1) (10)^(3b+2) 111001 (the
K family of the champion, template R,B,P=11,u=10,S=111001). K1 = the same WITHOUT the leading 11 (blank directly left of the leftmost token), tokens
arbitrary m >= 1 with m not = 0 mod 3. This is the notation of the BB(9) record (Kt with t = 0); its mexp.py was reused unchanged.

## Rules (token form: list left to right, a-token last, r the accumulator run)

| rule | statement |
| --- | --- |
| R1 | a-token m >= 4: (m, r) -> (m-3, 2r+4) |
| R2/R3 | a-token 1; t = nearest token != 1 (t >= 4, incl. 5): t -> t-3, the token right of it (a 1, or the a-token) -> 2r+3, r := 2 |
| D2 | same shape with t = 2 (always the leftmost token): t deleted, the token right of it -> 2r+3, r := 2 |
| REBUILD (K0 only) | all tokens 1 (n+1 of them incl. a = 0), r = 3b+2: -> P-less [6b+5, 1^(n+2)], r = 2 |
| used-up (K1 only) | all tokens 1: translated cycler, never halts |

In digit terms R1-R3 are the rules B(a; b+1, ...) -> B(2a+4; b, ...) and B(a; 0^k, 0, n+1, ...) -> B(0; 0^k, a+2, n, ...) of the wiki, with a = r.

### Literal verification (exact simulator, gen/gk3.cpp, gen/absgrid*.py)
- Blank tape: first family configuration K(2,0^10;0;0) at step 2467 (as the watcher said). 27 successive family configurations (up to step 8.06e8,
  3e9 steps run) equal the abstract R-successor: 26 of 26 consecutive pairs (gen/chk_traj.py). Same K sequence as the BB(7) champion (champ12 report).
- Level 0 (P = 11): 109 random configurations (up to 7 tokens, r up to 14): 0 mismatches (absgrid0.py).
- Level 1 (P-less; T leftmost residue 2, and plain lists): 148 random configurations: 0 mismatches (absgrid2.py). A residue-2 token that is NOT
  leftmost is never produced (and behaves differently; not needed).
- REBUILD: n = 0..4, b = 0..7 and (0,100): the first clean configuration is exactly [6b+5, 1^(n+2)], r = 2.
- Used-up lists [1^j], r = 2..50, j = 1..13: all end in the cycler (tail c 1^4 c 0 a1 0 1 with the 1-run before it growing by 2 per 70 steps, checked to 6e5 steps).
  The transient has several left-end shapes (c = 110, a1 = 10): j = 1: c a2 c^(4r-4) 1 c a1 0 1 c 0; j = 2: c a2 c^(4r-1) a1;
  j odd >= 3: a2 1 c 0 (a1 0)^(3r) a1 11 (c 00 1)^((j-3)/2) c 0; j even >= 4: c a2 c^(4r-1) a1 c 1 (c 00 1)^((j-4)/2) c 0; each followed by c 1^N c 1^4 c 0 a1 0 1.
- First epoch of the real orbit: K(2,0^10;0;0) -> ... -> exhaustion K(0^11; 0; B) with B the huge accumulator of the champion (champion rules); the rebuild then gives
  [6B+5, 1^13] with r = 2.

### How it was found (so the next person can skip it)
snapraw.cpp (B-at-frontier snapshots) showed c a_x c a_y c a_z 0 1 c 0 1 with quadratic cost and x falling by 3 per round: a long R1 chain of the champion on a
token of value 43 (b = 0), which looked like an endless R4. The key step was a K parser WITHOUT the leading 11 and with arbitrary token values (gk3.cpp): the first
K configuration after R4 then appears after only 396+ steps and the rest follows. (The earlier detectors, blank.cpp and probe2, require P = 11 and m = 1 mod 3,
which is why every nob_screen R4 cell timed out.)

## Coq status (proofs/BB8_m7_1RB0RA_1RH1LG.v, generated by gen/gen_full.py; see its TODO header)
Machine-level lemmas, all generated by mexp.py (BB(9)-record investigation, TM and t = 0 tail swapped in; 0.2-3 s each) and compiled:
R1, R2, R3 (context 1 :: l left of the tokens, covering level 0 and every non-leftmost borrow at level 1), R2B, R3B (leftmost token, blank to its left),
D2A ([2,1] -> [2r+3]), D2B ([2, 1^(k+2)] -> [2r+3, 1^(k+1)]), and REBUILD : forall b n, K0 (1^(n+1)) ... -->+ K1 ([6b+5] ++ 1^(n+2)) ... (41 lemmas).
gen/cycle.v: CYCLE : forall N l, (tail ... [1]^^N *> 0 >> l) B> -->+ same with two more 1s (1 lemma; compiled, 21 s).
Compile of the whole partial file proofs/BB8_m7_1RB0RA_1RH1LG.v: exit 0, 241 s at Idle priority (208 generated lemmas, 8 rule lemmas; CYCLE is not in it, it is in gen/cycle.v).
check.py would not accept the file (no nonhalt theorem); it is deliberately absent from the README Proved table.

### Precise remaining gap (for an Opus continuation)
1. **Used-up transient**: K1 (1^j) 1 (3b+2) -->* cycler configuration (N = 0), for j = 1, j = 2, j odd >= 3, j even >= 4 (loop over zero pairs).
   Target shapes are in gen/gen_cyc.py (ITEMS T1..T4). mexp.explore FAILS on them. For T1 the stage START -> (10)^(6b+4) 0 1 c 0 a1 0 1 (S1) and the last stage (S4)
   succeed instantly; the two middle stages (gen/gen_t1.py S2, S3; run dbg_s2.py) do not: the first loop is found (the run (10)^(6b) is moved to the right of the
   head, a stack of (10)^6 blocks grows on the left), then the explorer is stuck at  0^inf 1 1 (10)^(6b) <C (101)^k 0 0 1 0 1  and recurses on b without finding the
   second loop (C bounces at the end of the run; the round crosses its own explicit stack, so match_side_multi needs a hint, or the stack must be given as a run in the start configuration).
2. init_reach: c0 -->* K0 (2::0^10) 0 0 in 2467 literal steps (do 2467 steps; see init_reach in BB8_m7_1RB0RA_1RG1RF.v).
3. Abstract glue (about 250 lines; model: bb9_record_1RB0RA_1LI0LC_coq/abstract.v.in without tails and bounds): step_fam for K0/K1 with progress_nonhalt_cond.
   No ordering argument is needed (every family configuration has a successor: R1, R2/R3/D2, REBUILD, or used-up -> cycler -> infinite).
   Invariants: K1 tokens are not = 0 mod 3, only the leftmost may be = 2 mod 3, r = 2 mod 3.
4. python check.py BB8_m7_1RB0RA_1RH1LG.v (the compile of the partial file alone takes several minutes: the crossing-lemma header dominates).
   A second attempt (gen/gen_t1b.py, phase A with a free count y: (10)^(2y) 0 1 c 0 a1 0 1 -> a2 1 c 0 (a1 0)^(3y+4) 11 c 0 a1 0 1) also fails: the first loop turns the run into
   (100)^(4y) (blocks of 4 units) and then the head D bounces at the right end of that run; the natural period of that second loop is probably not a divisor of the 4-unit block,
   which is the block-size lesson of the champ12 report (use single units or 3-unit blocks, and state the intermediate targets with the same block size).
   Best diagnosis so far (gen/dbg_manual.py 10 x 6 3, single-unit run (10)^x as the start of the used-up transient, state B at the frontier with tail 0 1 c 0 a1 0 1): the explorer finds
   THREE loops in a row, each moving the run across the head and rewriting it:  (10)^x on the right of B  ->  (10)^x on the left under C  ->  (110110)^x on the right
   ->  (100100)^x on the left (loop lemmas of x single units, found automatically), and then is stuck with D bouncing at the right end of (100100)^x:
   0^inf 1 0 1 0 1 1 (100100)^x <D 1 1 1 0 0 1 0 0 1 0 1 0^inf.  After that the (100)-run is consumed 3 units per 2 while a 1-run grows (the shape a2 1 c 0 (a1 0)^(3y+4) 1^N c 0 a1 0 1, x = 2y).
   A hand-written loop lemma for this last pass (peel (100100), insertion on the right) is what is missing for phase A; phase B (conversion to c^(4r-4)) is similar.
Alternative for item 1 (unexplored): a regular-invariant proof for the transient (all configurations reachable from used-up lists avoid reading E0).

## Comparison with known machines
Same engine as the BB(7) champion (and the champ12/m7 rebuilders) but the halt at the exhausted list is replaced by: rebuild into a P-less list with one big
residue-2 token, a D2 stage with no arithmetic condition (the D2 stage of the BB(9) record halts only when k = 1 mod 5), and a cycler at the very end.
Growth is Ackermann-type; no sigma; non-halting by structure.

## Reproduction (python = third_party/venv311/Scripts/python.exe; C++ needs C:\msys64\ucrt64\bin on PATH, build with g++ -O2 -std=c++17 -static)
- blank.exe MACHINE 3000000000 (first-epoch family configurations), python chk_traj.py (against the abstract successor).
- gk3_s.exe MACHINE WORD B N maxprint [P]: first clean K configurations of any word (pw.py "[tokens]" r [P] builds a word, kw.py builds K(ds;a;b)).
- python absgrid0.py SEED N (level 0), python absgrid2.py SEED N (level 1), lastsnap_s.exe MACHINE WORD B N + tok2.py (cycler).
- Proof pieces in gen/: python gen_full.py ../../../proofs/BB8_m7_1RB0RA_1RH1LG.v ; python coqc_idle.py FILE.v (Idle priority).

## Cost
About 300k tokens, 150 tool calls: 90k to find the R4 structure (much of it on token-level inspection before the P-less K parser), 60k literal rule checks,
70k on generators and explorer failures for the used-up transient, 30k report.
