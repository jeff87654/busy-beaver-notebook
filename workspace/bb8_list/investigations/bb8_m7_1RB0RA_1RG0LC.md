# BB(8) m7-subtree NOBOUNDARY machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE  (E0 = 1RG)

Opus continuation (2026-10-08). Scratch and tools: `bb8_list/investigations/bb8_m7_1RB0RA_1RG0LC/opus/`.
The Sonnet report follows as an appendix. Its description of the orbit stands; its verdict ("strong evidence, not proved") is superseded.

## Verdict

**Never halts. PROVED: `check.py` PASS.**

    PASS BB8_m7_1RB0RA_1RG0LC.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE never halts (machine-checked, no axioms)

- **Proof file.** `bb8_list/proofs/BB8_m7_1RB0RA_1RG0LC.v` (57 KB), written by `opus/gen_coq.py`.
- **Compile.** 217 s under `check.py` on the loaded shared PC (a trivial file took 64 s to load at the same time). The `vm_compute` part is short: about 105k local configurations.
- **Record question.** No record: the machine never halts.

## The closed family (annotated n-gram CPS with a halting-reach component)

A plain n-gram closed position set fails for this machine at every window pair (Sonnet report, section 3). Two additions make it close with small windows.

1. **Writer annotations (ghost cells).** Every cell carries its symbol and the state that last wrote it, or "never written".
   - A cell is coded as c = bit + 2a, with a = 0 for "never written" and a = 1 + i for the i-th state A..H. There are 18 codes.
   - The annotations are existentially quantified in the invariant, so they need not be tracked by the real machine.
2. **Halting-reach component g on the right side.** g(r) is the set of states X such that the right-moving run of the machine started in X on the first cell of r halts before it turns.
   - It is computed cell by cell from the far end: g(x :: r) = {X : tm(X,x) undefined, or tm(X,x) moves right into some Y in g(r)}.
   - On the blank tape g = {E, F, G, H}.
   - This is the memory a plain n-gram lacks: whether a G/F/H/E sweep (G1 -> 0RF, F0 -> 1RG, G0 -> 0RH, H1 -> 0RE, E0 -> 1RG) started here would run off the end of the tape.

**Side automata.** A half-tape, read from the head outwards, is abstracted by a number:
- its first kL = 8 (left) or kR = 6 (right) annotated cells, 5 bits each;
- on the right, also g (8 bits).

`foldL` / `foldR` push one coded cell onto the near end of a side; they are deterministic. A side r **has state s** (`run fold S s r`) if there are states f(i) and codes cs(i) such that f(0) = s and, for every i:
- f(i+1) is in the learned set S;
- cs(i) is a code whose bit is r_i;
- fold(f(i+1), cs(i)) = f(i).

**Invariant.** A configuration (q, l, m, r) satisfies `Inv` if there are side states a and b such that:
- (q, m, a, b) is in the set C of local configurations;
- l has state a for (foldL, S_L);
- r has state b for (foldR, S_R).

**Closure (`check`, verified by `vm_compute`).**
- **Predecessor lists are complete.** For every learned s and every code c, (c, s) is recorded as a predecessor of fold(s, c).
- **Start.** The blank start (A, 0, zL, zR) is in C; zL and zR are learned and are fixed points of folding a blank cell.
- **Steps.** Every member of C has a defined transition and folds only a learned state. For every recorded predecessor (c, s') of the side it moves into, it steps into C. The written cell is coded with the writing state; the newly scanned symbol is the bit of c.
- **Soundness.** `inv_step` and `inv_init` prove, once and for all, that a successful `check` makes `Inv` closed under `tm` (busycoq `progress_nonhalt`). No property of g or of the annotations is used in the soundness proof; they only make the closure exist.

**Data.**
- The learned sets are embedded: |S_L| = 2986 and |S_R| = 66.
- Coq recomputes the predecessor lists and C: `bsearch` from the blank tape, 2^17 steps.
- |C| = 105,467.

**What the right states look like.** All 66 right states consist of cells written by left-moving transitions (B, C, D, E, F) or never written. Their g values:

| g | right states |
| --- | --- |
| {} | 31 |
| {H} | 19 |
| {G, H} | 10 |
| {E, F, G, H} | 6 (only near the blank end) |

### Window scan (`opus/ngann.exe MACHINE kL kR ANN G`)

**With writer annotations and g, these close:**

| kL/kR | local configurations |
| --- | --- |
| 8/6 (used) | 105,467 |
| 8/7 | 152,609 |
| 8/8 | 220,729 |
| 9/9 | 593,919 |
| 10/10 | 1,591,520 |

**These fail:** 4/4, 6/6, 7/7, 6/7, 7/6, 6/8, 7/8, 5/8, 8/5, 8/4.

**Without g**, writer annotations fail at 8/8, 10/10, 10/8 and 8/10. **With direction-only annotations** (ANN = 1) plus g, the search fails at 6/6, 8/8 and 9/9.
**Without annotations**, g alone fails at 8/8, 10/14 and 12/14. Exact tail memory of the tape ends (`opus/tcps2.cpp`, `tcps3.cpp`: the last M cells of each side, exact near-head stacks), with or without g, failed at every size tried, up to M = 24 with stacks of 32.
The reason: a pure digit block `(1|)^k 1.` at the right end does occur in the real orbit (e.g. step 933 from the blank tape: `1 1 3| (1|)^15 1.`). What must be remembered is the barrier `3|` in front of it, which is arbitrarily far from both the head and the end.

### Checks before Coq

- **Independent re-check** (`opus/pycheck.py cert_8_6.txt`). It reads only S_L and S_R, recomputes predecessors and C with exactly the Coq semantics, and finds the same 105,467 configurations.
- **Real-orbit validation** (`opus/realchk.exe cert_8_6.txt 2000000000`). It runs the machine from the blank tape for 2e9 steps with true writer annotations and checks at every step that the configuration is in C and every folded side state is learned. The result is `OK: 2000000000 steps covered, max tape 83808`.

## How the gap of the Sonnet report was closed

The Sonnet report (section 5) suggested tail memory. Experiments here showed why plain tail memory is not enough:
- While the head works at the right end, the end structure lies to the left of the head.
- An exact stack for that part still loses the barrier `3|`/`11` in front of an end digit block once the head leaves and returns.

The g component turns "a G-sweep may reach the end" into a deterministic, exactly propagated property of the right side. The writer annotations then separate real splices of windows from unreal ones: for example, a `1` written by D (a barrier) is distinguished from a `1` written by F or B. The two together close at 8/6.

## Reproduction (scratch dir `bb8_m7_1RB0RA_1RG0LC/opus/`; g++ -O2 -std=c++17 -static with `C:\msys64\ucrt64\bin` on PATH; python = venv311)

- **Closure search.** `TC_DUMP=cert_8_6.txt ./ngann.exe 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE 8 6 2 1`. It prints `NONHALT kL=8 kR=6 ann=2 g=1: 105467 configs, |S_L|=2986 |S_R|=66`, in under 1 s.
- **Re-checks.** `python pycheck.py cert_8_6.txt` and `./realchk.exe cert_8_6.txt N`.
- **Proof file.** `python gen_coq.py cert_8_6.txt ../../../proofs/BB8_m7_1RB0RA_1RG0LC.v 17` writes the file exactly as committed. Then run `python check.py BB8_m7_1RB0RA_1RG0LC.v` in `proofs/`.
- **Other tools.**
  - `tcps.cpp`, `tcps2.cpp`, `tcps3.cpp`: tail-memory CPS variants, which did not close.
  - `cmpp.py`, `cmpp2.py`, `showp.py`: abstract-path comparison with the real run.
  - `bfront.cpp`: B-frontier snapshots.
  - `simc.cpp`: literal runs from a concrete configuration.
  - `batch.py`: runner.

## Open questions

- **Other queue rows.** The annotated n-gram + g checker (`ngann.cpp` plus `gen_coq.py`) is generic in the machine except for the Coq `tm` table and the data. It may close other NGramCPS failures of the queue in which a sweep runs off a tape end. The generator currently asserts ANN = 2, G = 1, and the 5-bit cell layout.

## Cost

About 360k tokens (Opus).
- About 55%: tail-memory experiments that did not close and path diagnosis.
- About 25%: Coq.
- The rest: validation and the report.

CPU: a few Idle/BelowNormal processes for about 40 minutes in total. All were stopped or had finished.

---

# Appendix: the Sonnet report (orbit structure; its "not proved" verdict is superseded)

## BB(8) m7-subtree NOBOUNDARY machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE  (E0 = 1RG)

Investigator: Sonnet 5.5 (inv-m7-1RG0LC), about 400k tokens. Scratch and tools: `bb8_list/investigations/bb8_m7_1RB0RA_1RG0LC/`.
Sibling machines (same table, only E0 differs): E0 = 0RB (`proofs/BB8_m7_1RB0RA_0RB0LC.v`, n-gram windows 10/14) and E0 = 1LG
(`proofs/BB8_m7_1RB0RA_1LG0LC.v`, windows 4/9).

## Verdict

**No halt found; not proved. Confidence: strong evidence for "never halts", NOT proved (no `check.py` PASS, no proof file, no README row).**
**Record question: no halting run was found, so there is no sigma and no record claim.**

The main finding is negative and precise. **Plain n-gram closed position sets (NGramCPS) cannot close this machine at any window length.**
The reason is that the abstraction forgets the structure of the tape end between visits of the head; it is not a size problem. A proof needs either
(a) a CPS with exact memory of the tape ends (not built) or (b) a structural proof with rules and residues (not built). Details, data and a plan follow.

## 1. How E0 = 1RG relates to E0 = 0RB (verified by literal simulation)

E0 is read only at the end of an epoch and in the "G0 H1 E0" lockstep of the rounds.
- **E0 followed by 1.** Ours: E0 -> 1RG, then G1 -> 0RF. Theirs: E0 -> 0RB, B1 -> 1LF, F0 -> 1RG, then G1 -> 0RF. After 1 resp. 3 steps tape and state coincide (hand derivation,
  confirmed by the identical B-frontier snapshots below). Only the step counts differ.
- **E0 followed by 0.** Ours enters G0 (0RH) and then H (the lockstep continues along a (010)^k pattern, and H0 halts). Theirs enters B0 / C. The machines diverge only here.
- **Snapshot identity.** From M3(K,n) = `1^2 3| (1|)^K (3n+7)| 1| 1.` the sequences of B-frontier tape snapshots (run notation) of the two machines agree
  line by line for 6e7 steps for K = 7, 19 (n = 0), and for about 2000 snapshots for most K = 7..30 (n = 0..1), except the divergences of section 4.
- **Epoch 1 and M3.** The first epoch (champion digit-list recursion, E0 never read) is identical. The exhaustion gives
  K0(0^n;0;b) -> M3(12b+7, n) = `1^2 3| (1|)^(12b+7) (3n+7)| 1| 1.`, checked literally for n = 0..3, b = 0..2 (n=0, b=0: step 556).
  For the real orbit n = 11 (so the 40-run) and K = 12B+7 with B the champion's huge accumulator.

## 2. Evidence for "never halts"

- **Faithful shadow orbit** (`shadow/shadow2.py`, the 0RB0LC Opus driver with the machine swapped; champion rules done modulo 504, every other
  situation literal via `fsnap.exe`). Start `1^2 3| (1|)^1591 40| 1| 1.` (K = 1591 mod 3528, n = 11).
  - 337 events were followed (`runs/shadow_K1591_b.txt`; `runs/shadow_K1591_a.txt` has the first 376 events of an earlier foreground run).
  - Every event ends in a stable tail T1(j) = `1^8 (00 1^6)^j 00 1 00 1` with j growing to 197, the digit block (1|)^K shrinking by 5 per cycle
    (1584 -> 533 at EV337), and a second list `[0^2,4,9,6,966,14,10,(4,2,7)^q,..]` built in Q.
  - **No halt.** The run stopped at EV337 only because the driver's `literal()` returned None. That is an environment glitch
    (fsnap failed to start under memory pressure on the shared PC): the same kind of configuration, re-run alone (K=282, EV34), returns a valid stable configuration in 0.4 s.
  - EV1 equals the 0RB0LC run; **EV2 already differs** (ours `[0,1] r=2 ... 5 1^1052 2 1 1| 1.`, theirs `[0^4,1054,2,1]`), because E0 followed by 0 occurs there.
    So the orbit is not a relabelling of the 0RB0LC orbit, although the "seven-digit cycles" look similar.
- **Parameter sweeps, no halt** (`e0z.exe`, `multi.exe`): M3(K,n) for K = 7..46, n = 0..12 with 3e7 steps each (about 500 runs; 2 rows with empty output were environment glitches and re-ran OK);
  M3-like tapes with an arbitrary run length L = 1..70 instead of 3n+7, K = 7..40, 4e6 steps each: only L = 2 halts, trivially. So no residue of the run
  length mod 3 matters in the first 4e6 steps.
- **Random reachable-like starts** (`../bb8_m7_0RB0LC_opus/hsearch4.exe`, seed 31, 15000 configurations, 1e6 steps): theirs 0 halts, ours **86 halts**
  (`runs/hs4_ours_31.txt`). The halting right ends are `...00 1 00 1 1 00 1 00 1` (`2| 1| 1.`, the dangerous end already known for 0RB0LC) and,
  new for ours, **pure digit-block ends** `(1 00)^k 1`. In the real orbit the right end is always T0 = `3| 1.` or T1(j) (all shadow events), which is safe.
  So ours has more dangerous tape ends than theirs, but none is produced in the followed orbit.
- **Where the machines differ in reality** (`diverge.py`, section 4): the first difference is the failure event `... 2 1^40 1| 6| 1| 1.`
  (list end next to the first T1 block). Theirs keeps the 6-block (`2 6| 1| 1.`). Ours gives `1| 2^2 1 3| 1.`, i.e. **the tail T1(1) is rewritten to the
  first-epoch tail T0 = `3| 1.`**, and a champion-type run on a list with a `1|` separator follows. It was followed for 1.5e8 steps
  (K = 8, n = 0): list tokens `2^2 1^89 2 1^k 2 1^m` evolve by the champion rules, no halt.

## 3. Why n-gram CPS does not work (computed)

Tool: `ngfast.exe MACHINE nL nR` (hash-set version of `ngcps2`; env `NG_CAP`, `NG_START=N0`, `NG_TAPE=word` start from a given finite tape, `NG_NOFAIL=1` treats H0 as a sink,
`NG_HALTDUMP=pass` prints the halting configurations).
- **FAIL (a halting local configuration is reachable):** 6/6, 8/8, 10/10, 10/14, 12/12, 12/14, 14/14, 16/16 (after 84M configurations), 4/24, 5/26, 24/6, 26/8, 28/8, 30/10,
  6/20, 8/20, 8/16, 8/18, 10/16, 10/18. No verdict within 60M configurations or 100 s: 18/18, 20/20, 14/20, 20/14, 24/24, 6/24, 8/24, 12/20, 12/24, 10/24, 10/20.
  The queue row "BUDGET" (5718 s) is explained: no pair closed.
- **Starting later does not help.** A start at the concrete configuration of step 2467 (first K-family configuration) or at the family M3(K=40, n=11) (the real start of epoch 2,
  windows of the actual tape) still FAILs at 10/14, 12/14, 14/14. For comparison the same M3 start closes for 0RB0LC at 10/14 (2,852,584 configurations).
- **The abstraction is almost closed, but it is trapped by one local configuration.**
  With H0 as a sink the closure is small: 10/14 2,566,384 configurations (M3 start 2,563,094), 12/14 7,974,431, 14/14 24,453,255.
  At 10/14 there is exactly **one** halting local configuration, c* = `H0 | left 1001001010 | right 0^14` (blank to the right; the left window is read farthest cell first);
  at 12/14 it is `001001001010 H0 0^14`: the same shape. Its backward chain (`cone.exe`) is `H0 <- G0 <- F0 <- G1 <- E0 [1] 000 <- H1 <- G0 ...`: the "G0 H1 E0" lockstep
  sweeping a digit block (1 00)^k into the **end of the tape** (the last cell is a lone 1). **All 2,566,384 configurations of the closure reach c*** (backward cone = everything;
  start to c* in 88 abstract steps in the final graph). The first 17 path positions are dominators (the deterministic prefix); no later dominator was found, so there is no single
  unreal bottleneck to cut.
- **Mechanism.** The shortest abstract paths (`ngpath.exe`, `cmp_path.py`) leave the real orbit at the first guessed far cell:
  blank start 10/14 at step 133 (a left guess 0 where the real tape has 1), 14/14 at step 217; step-2467 start 10/14 at step 70 (the count of (110) blocks);
  M3 start at step 8 (the 40-run is guessed to end after 9 ones). After that the head sweeps back and forth, and **every sweep re-guesses the cells that had slid
  out of the window**, so the abstract tape end is not remembered: a stitched path contradicts its own earlier cells hundreds of times (`stitch.py`: 892 resp. 1470 conflicts).
  A digit block of any length followed by a bad end exists for every window size, because the block length is a counter that no n-gram can bound.
  Longer windows only move the divergence (133 -> 217) and multiply the configuration count (2.6M -> 8.0M -> 24.5M -> more than 84M).
  Per-state or per-side window lengths do not change this: the guess at the far edge is constrained only by sets that are themselves closures.
- **Verdict on route (a):** further window pairs are useless. The fix has to add memory, for example a CPS whose abstract state also carries the exact last M cells of the tape
  (tail memory, nondeterministic far/near mode as the head approaches) and likewise the left end. That multiplies the state count by the number of reachable tail forms; not attempted.

## 4. Where ours and 0RB0LC first differ (literal, `diverge.py`, B-frontier snapshots from M3(K,n))

| K, n | first differing snapshot | common | ours | theirs |
| --- | --- | --- | --- | --- |
| 8, 0 | 121 | `2^2 1^92 2 1^40 1| 6| 1| 1.` | `2^2 1^91 2 1^41 1| 2^2 1 3| 1.` | `2^2 1^91 2 1^42 2 6| 1| 1.` |
| 15, 0 | 205 | `3 1^94 2 1^92 2 1^40 1| 6| 1| 1.` | same pattern | same pattern |
| 22, 0 and 29, 0 | 289, 373 | same pattern, one more `2 1^k` block per 7 digits | | |
| 7, 1 | 43 | `2^2 1^6 2 1^40 1| (6|)^3 1| 1.` | `2^2 1^5 2 1^41 1| 2^2 1 8| 6| 1| 1.` | `2^2 1^5 2 1^42 2 (6|)^3 1| 1.` |
| 14, 1 | 127 | same pattern | | |

K = 7, 9..14, 16..21, 23..28, 30 (n = 0) and K = 8 (n = 1) show no difference through about 2000 snapshots (4e6 steps).
The event has the shape "list end `2 1^40`, then `1| (6|)^j 1| 1.`", period 7 in K. Ours turns the T1(j) tail into `8| 6| 1| 1.` (n=1) or `3| 1.` (n=0).
The number of E0-followed-by-0 reads is 0 for most small K and a few for some (`runs/sweep_K7_80_n0_12.txt`, last column).

## 5. Gap and recommended plan for an Opus continuation

1. **Structural route (b)** needs the catalogue of failure events of ours. Known so far: (i) the same epoch-1 exhaustion and M3 as 0RB0LC; (ii) the digit-processing start and
   the seven-digit cycles with tail T1(j) (EV1..EV337 of the shadow run); (iii) the rewriting event of section 4 (T1(1) -> T0 or `8| 6|`); (iv) what happens at the end of the digit block
   (K mod 7 and finer residues) is **not reached**. Continue the shadow run: `shadow/shadow2.py` with the machine swapped (`fam.py`) needs a retry when `literal()` fails (the glitch above)
   and a dump of the full Q so that a run can be resumed with the `CFG:` start. Then check, event by event, that the right end stays T0 / T1(j) / safe,
   and that no pure digit-block end and no `2| 1| 1.` end occurs.
2. **Dangerous ends for ours** (the invariant a proof must exclude): `...00 1 00 1 1 00 1 00 1` (`2| 1| 1.`), a pure digit block `(100)^k 1` at the end, and in general G scanning the
   last 1 of the tape (G1 then F0, G0, H0), or G0 followed by 0 (H0 at once).
3. **Route (a) variant:** an NGramCPS in which the abstract state carries the exact tail (last 24 cells) and the exact left end, with a nondeterministic near/far mode. The Coq soundness
   lemma `nonhalt_of_check` in `proofs/BB8_m7_1RB0RA_0RB0LC.v` has to be generalized (state = (q, m, l, r, tail, mode)). Expect tens of millions of configurations; the 0RB0LC proof with
   2.86M configurations needed 464 s of vm_compute, so the Coq check must be cut down.
4. Not useful: further window pairs, mxdys CTL/NG presets (they failed for the easier sibling), starting the CPS later.

## Reproduction (scratch dir `bb8_m7_1RB0RA_1RG0LC/`; g++ -O2 -std=c++17 -static with `C:\msys64\ucrt64\bin` on PATH; python = venv311)

- Literal tools: `sim.exe MACHINE WORD STATE N`, `e0z.exe MACHINE WORD STATE N` (counts E0 reads and E0-followed-by-0), `ectx.exe` (context census), `multi.exe MACHINE K0 K1 L0 L1 N`
  (M3-like sweep), `m3.py K n` (builds the M3 tape), `sweep_halt.py`, `diverge.py K0 K1 n0 n1 N` (uses `../bb8_m7_0RB0LC_opus/tsnap.exe`).
- CPS tools: `ngfast.exe MACHINE nL nR` (`NG_CAP`, `NG_START`, `NG_TAPE`, `NG_NOFAIL`, `NG_HALTDUMP` via `ngfast2.exe`), `ngpath.exe` (BFS path), `cmp_path.py PATH nL nR` (first divergence from the real run),
  `stitch.py` (consistency of a path), `dom.exe` (dominators), `cone.exe` (backward cone), `runfast.py T pairs...`.
- Shadow orbit: `cd shadow; NORESET=1 COMPACT=60 python shadow2.py "1^2 3| (1|)^1591 40| 1| 1." 4000` (`fam.py` holds the machine; `fsnap.exe` copied from the 0RB0LC Opus directory).
- Logs: `runs/` (shadow, sweeps, divergences, dom, hsearch) and `path*.txt` (abstract paths).

All background processes were stopped by PID before this report.
