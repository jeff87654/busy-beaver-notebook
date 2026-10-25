# BB(8) m7-subtree NOBOUNDARY machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF

Scratch dirs: bb8_list/investigations/bb8_m7_1RB0RA_1RA0LC/ (Sonnet investigation, tools listed at the end) and its opus/ subfolder (Opus
continuation: generators of the proof). Proof: bb8_list/proofs/BB8_m7_1RB0RA_1RA0LC.v. Investigators: Sonnet 5.5 (about 350k tokens; macro
structure, all rules checked literally, skeleton proof), then Opus 5.5 (the Coq proof).

## Verdict

**NEVER HALTS: proved (Coq, check.py PASS, no axioms).** Not a record candidate (no halt, no sigma).

    PASS BB8_m7_1RB0RA_1RA0LC.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF never halts (machine-checked, no axioms)

(compile time 5635.5 s wall, at Idle priority on a fully loaded PC; the generated machine-level lemmas take almost all of it.)

After the champion's first epoch the used-up list is REBUILT (neither halt nor cycler) through a fixed lifecycle of nonstandard tokens into a
STANDARD 3-token champion list, which the champion rules process again, and so on forever: the token count (left of the a-token) goes
11 -> 3 -> 3 -> ...

## The proof (Opus continuation, 2026-10-07/08)

Family (nearest-first lists, as in the sibling proof BB8_m7_1RB0RA_1RH1LG.v):
`K P11 ds a r = 0^inf 11 D(ds..) D(a) (10)^r 111001 B> 0^inf`, D(m) = (10)^m 1. Closed family with `progress_nonhalt_cond` (every state has a
successor, no ordering argument), three kinds of state:
- `Std ds a r`: the champion's family; all tokens = 1 mod 3, a = 1 mod 3, r = 2 mod 3, length ds = 11 or 3, and "a = 1 and r = 2 imply some
  token != 1" (so a used-up list always has r = 3c+5, i.e. b >= 1: it arises from R1, r -> 2r+4 >= 8). Steps: R1, R2, R3 (the champion's rules,
  context 1::l), and the used-up list (n = 11 or 3) -> `Life (7+12c) 762 2 T`, T = 3n+13 (lemmas KUSED11, KUSED3).
- `Life k a r T` = `[T, 21, 1^k, 0, 1 | a] r` with k odd, a = 0 mod 3: R1 while a >= 3; at a = 0 STAGE (k -> k-2, a := 2r+2, r := 2) or,
  at k = 1, ENDA -> `Fin (2r+2) 2 T`.
- `Fin a r T` = `[T, 20, 1 | a] r`, a = 0 mod 3: R1 while a >= 3; at a = 0 ENDB -> `Std [2r+3, 16, T] 1 2` (3 tokens, contains 16).

The used-up rebuild, for n in {3, 11}, r = 3c+5 (`KUSEDn`, composed of machine-level lemmas, waypoints found from literal traces and checked
with `python wp.py check N`):
1. `UAn`: used list -->+ Z_n(6c+10, 1), where Z_n(x, k) = B on the blank left end of `0 (01)^x 00 (101)^k (100)^(n+2) 101` (the head has
   run the whole list into this "bounce" form; the old tokens became (100)^(n+2) 101).
2. `ZRn`: Z_n(x+1, k) -->+ Z_n(x, k+2) (one bounce); `ZITn` iterates it by induction: Z_n(6c+10, 1) -->* Z_n(0, 12c+21). This loop is
   the quadratic part of the transient; the explorer cannot find it inside one exploration because x = 6c+10 is a run of 12-cell
   blocks while a round peels 2 cells, hence the explicit waypoint.
3. `UBn`: Z_n(0, 21+m) -->+ C1 = `[T+3, 1^(11+m), 2, 0, 3 | 3]` r = 2 (linear in m, for any m; used with m = 12c).
4. `C12`: C1 -->+ C2 = `[T, 21, 1^(9+m), 0, 0 | 19]` r = 2 (any leftmost token 3+x); six R1 steps (19 -> 1, r: 2 -> 380);
   `C23`: `[x, 21, 1^(9+m), 0, 0 | 1]` r = 2+3q -->+ C3 = `[x, 21, 1^(7+m), 0, 1 | 2r+2]` r = 2 (q general, used with q = 126: a = 762).
The lifecycle rules STAGE, ENDA, ENDB are stated with r = 2+3q (with r = 1 the explorer finds a halt: the residue mod 3 matters).
`init_reach`: 2117 literal steps from the blank tape to `Std (1^10 ++ [7]) 1 2` = the champion's K([2, 0^10]; 0; 0).

Generators (opus/; python = third_party/venv311/Scripts/python.exe):
- `python gen_final.py full0.v` explores and proves all 14 machine-level lemmas with mexp.py (copied from
  ../bb8_m7_1RB0RA_1RH1LG/gen/, plus an optional MEXP_TRACE progress print) and appends the hand-written glue `glue.v.in` (+ `used.v.in`);
  `python assemble.py full0.v OUT.v` re-attaches the current glue to an existing generated part; `assemble.py ... stub` replaces the
  generated lemmas by Admitted stubs to test the glue quickly (DEV ONLY, never a proof).
- `wp.py` (waypoints UA/ZR/UB/C12/C23, literal checks with `validate.reaches`), `gen_rules.py` (R1-R3), `gen_life.py` (STAGE/ENDA/ENDB),
  `tr2.py` / `ksnap.py` / `zprobe.py` (literal traces: the bounce loop, Z(0,k) -> C1 for all k >= 15).
- `bg.py` starts a command at Idle priority; `coqc_idle.py`, `check_idle.py` compile / check at Idle.

Lessons: the Sonnet macro description was exactly right; the only obstacle for automation was the quadratic bounce loop, solved by one
waypoint (Z(6c+10, 1)) and a hand-iterated round lemma, as in the sibling 1RH1LG proof (whose ZR/ZIT has the same shape: there TOK =
(100)^13 101, here (100)^(n+2) 101).

## Setting and notation (same as the sibling reports)
Tape (head in B at the right end, nothing to its right), K-form:  P D(m1) .. D(mk) (10)^r 111001, P = 11, D(m) = (10)^m 1, last token = a-token, r = run.
Standard list = all tokens = 1 mod 3 (digit d <-> token 3d+1), r = 3b+2. Champion rules (also valid for this machine):
R1: a >= 4: (a, r) -> (a-3, 2r+4); R2/R3: a = 1, t = nearest token != 1 (t >= 4): t -> t-3, the token right of t -> 2r+3, r := 2.
This machine differs from the champion in E0 = 1RA (no halt there), F1 = 1LE, G0 = 0RH, H = ---0RF. The ONLY halting transition is H0, reached iff the
right-moving F/G/H sweep lands on a 0 followed by two more 0s (e.g. G erasing the rightmost 1).

## Verified facts (all literal)
1. **First epoch = champion**: the blank tape reaches exactly K0([2;0^10], a=0, b=0) at step 2117 (exact tape equality, first.py). 27 consecutive K
   snapshots (4e9 steps) satisfy the champion successor, 26/26 pairs (chk_first.py). 1472 random standard lists (up to 8 tokens, tokens in
   {1,4,..,22}, r in {2..20}): 0 mismatches with R1/R2/R3 (chkstd.py). So the first epoch ends in the used-up list K0(0^11; 0; B), n = 11 (12 tokens), B huge (b >= 1).
2. **R4 depends on n mod 4** (K0 used-up list of n+1 tokens, r = 3b+2; ex.py, ex2.py, ex3.py; b = 0..3, n = 0..15):
   - n = 2 mod 4: rebuild into the standard list [3n+13, 1^(12b+6)] (r = 2) (n = 2, 6, 10, 14 checked); then n' = 12b+6 = 2 mod 4 again (a different stable loop, NOT the real one).
   - n = 3 mod 4, b >= 1: the nonstandard lifecycle below (**the real case, n = 11**). For b = 0 it is different (K[3n+13, 17] r = 30, then an R1 chain).
   - n = 0 mod 4: n = 4 gives [5,30,18,757,1^3] after 8.3e5 steps (b = 1), n = 12 gives [6,10,3094,1^12] after 1.3e7 steps; n = 8 and n = 1 mod 4: no K snapshot within 3e8 steps (not needed).
3. **Unified token view.** K-form tapes with ARBITRARY nonnegative tokens (0, 2, 21, ...) are all deterministic: from the very start of R4 the machine
   is the same engine acting on nonstandard tokens (note D(a) 0 111001 = (10)^(a+1) 111001, so the "additive" snapshots with tail 0111001 are K-form snapshots with a shifted a-token/r split).
   Rules for the last tokens (r = 2 mod 3 always; probe tables probe5/6/7 in the scratch dir):
   a >= 3: R1 (any residue); a = 0, 1, 2 with t the nearest token >= 3: t -> t-3 (t-4 for a = 0 with a 0-token in between), the token right of t -> 2r+3 (2r+5 for a = 2), r := 2;
   small tokens 0/1/2 between t and a change the output pattern (see probe7.py, e.g. [t,1^k,0] -> [t-3, 2r+3, 1^k]).
   Sampling: 30000 random K-form configurations (1..7 tokens in 0..12, r in {2,5,8}, 1e6 steps): 29457 returned to K-form, 543 timeouts (long used-up transients), **0 halts**; 60 of the timeouts rerun to 2e8 steps: no halt.

## The lifecycle for n = 3 mod 4, b >= 1 (T = 3n+13)
All r values are 2 mod 3. Checked at n = 3, 7, 11, b = 1..6 and n = 3, b = 10, 25, 50 for C1-C3 (evs.py); chkB.py / chkC.py for the rest.

| phase | from | to | check |
| --- | --- | --- | --- |
| used-up transient (quadratic, loops over b) | K0(1^(n+1)), r = 3b+2 | C1 = [T+3, 1^(12b-1), 2, 0, 3, 3] r = 2 | first K snapshot at step 324 b^2 + (336 n + 2658) b + 9 n^2 + 385 n + 2212 (fits all measured points, e.g. n = 3, b = 50: 996748) |
| R1 on a = 3 (a -> 0, r = 8), left bounce over the 1-run (linear in b) | C1 | C2 = [T, 21, 1^(12b-3), 0, 0, 19] r = 2 | steps 12292 (n=3,b=1), 18946 (b=2), ... |
| R1 x6, then the "1 1 0 0 1" rule | C2 | C3 = [T, 21, 1^(12b-5), 0, 1, 762] r = 2 | [T,21,1^k,0,0,1] r -> [T,21,1^(k-2),0,1,2r+2] r = 2 for T = 22,34,46, k = 2..11, r = 2,5,8,380 (120 cases, 0 bad) |
| R1 chain 762 -> 0 (254 steps), then STAGE (repeated) | [T,21,1^k,0,1,0] r | [T,21,1^(k-2),0,1,2r+2] r = 2, then R1 chain on a = 2r+2 = 0 mod 3 (a -> 0, r -> 2^j (r+4) - 4) | T = 22,34,46, k = 1..11, r = 2,5,8,14 (132 cases, 0 bad) |
| end of the loop (k = 12b-5 is odd, so it ends at k = 1 after 6b-3 stages) | [T,21,1,0,1,0] r | [T,20,1,2r+2] r = 2 | same table (k = 1 row) |
| end | [T,20,1,0] r | **[T,16,2r+3,1] r = 2** | T = 22,34,46, r = 2..26 (18 cases, 0 bad) |

The last list is STANDARD (T = 1 mod 3, 16, X = 2r+3 = 1 mod 3, a = 1, r = 2): digits ds = [(T-1)/3, 5, (X-1)/3], a = 0, b = 0, n = 3 (4 tokens). The champion
recursion preserves the token count, so its exhaustion is a K0 used-up list with n = 3 (3 mod 4) and b' >= 1 (the last step of an exhaustion is an R1 or a borrow that produced r >= 8),
and the lifecycle repeats with T = 22. So **n = 11 -> 3 -> 3 -> ...: an infinite sequence of epochs** (tower-type growth, no halt).
Every configuration on this orbit has a successor in the family, so the proof needs no ordering argument (progress_nonhalt_cond), as in the sibling proofs.
Parity point that makes the loop uniform: the 1-run has odd length 12b-1, 12b-3, 12b-5 for every b.

## Evidence against halting beyond the above
- The only halt is H0; the lifecycle never produces a right sweep that reaches the blank (every literal arrow above ends in K-form).
- n-gram closed position sets (../bb8_m7_0RB0LC_ctl/ngcps2.exe, my scan ngscan.py, log ngscan.log): every window pair tried (nL, nR in 10..18, even) either FAILs with a reachable
  local H0 configuration (e.g. 12/12 and 14/12 at 26-53 s) or times out at 90 s (10/16, 10/18, 14/14, 16/12, 10/20). Consistent with the queue verdict OPEN: local windows do not see the mod-3
  residues and token counts that the lifecycle depends on.

## Remaining gap

None: closed by the Opus continuation above. Not needed and not checked: n = 0, 1 mod 4 and the b = 0 branch of the rebuild (the
invariant shows n stays in {11, 3} and b >= 1). Note the proof's lifecycle starts from C3 with the 762-token, so the token tables of the
Sonnet report for C1 -> C3 are now machine-checked for every b.

## Comparison
Same engine as the BB(7) champion and the other m7 rebuilders; here the halt at the exhausted list is replaced by a rebuild through nonstandard tokens (0, 2, 21, 20) into a
4-token standard list. Differs from the siblings: P-less K1 lists with D2 and a final translated cycler (1RH1LG), degraded-list rebuild (0RB0LC), [2, 0^...] rebuild (1RG1RF).

## Reproduction (python = third_party/venv311/Scripts/python.exe; C++ needs C:/msys64/ucrt64/bin on PATH, g++ -O2 -std=c++17 -static)
- gk5.exe MACHINE WORD B N maxprint TAIL PFLAG: literal run, K-form snapshots (tokens >= 0). gk6.exe: batch of configurations (batch.py wraps it).
- first.py (blank -> K0 at 2117), chk_first.py (27 epoch configs), chkstd.py SEED N (standard lists), ex.py / ex2.py / ex3.py (R4 by n, b), seqk.py n b N (K-form events), evs.py n N b1,b2,..
  (first three lifecycle events), chkB.py (stage, k=1 and end rules), chkC.py (C2 -> C3), probe5.py / probe6.py / probe7.py (small-token rule tables), rand1.py / rand2.py (random states, halts),
  ev_from.py "[tokens]" r N (events from a given K-form state), absim.py (semi-abstract simulator, unfinished), ngscan.py (n-gram window scan).
- Re-run: python evs.py 3 300000000 1,2,3 ; python chkB.py ; python chkC.py ; python chkstd.py 1 1500.

## Cost
- Sonnet: about 350k tokens (60k reading the siblings and tools, 120k token-level inspection, 90k rule tables and checks, 50k lifecycle end
  and the n = 3 cycle, 30k report).
- Opus continuation: about 330k tokens (reading the report and the sibling generators, waypoints of the rebuild, glue, two stub compiles and
  the final check; most of the wall time was coqc at Idle on a saturated PC).
