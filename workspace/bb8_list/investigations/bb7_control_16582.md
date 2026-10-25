# Control investigation: BB(7) holdout `1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG`

Source: holdout of mxdys's enumerator (ccz181078/TM @ a41db6c), BB(7) subtask 16582. Our growth ranking picked it
as the one outlier among 1,509 holdouts from 12 random BB(7) subtasks (2 / 10 / 40 CPU-s gave
2,246 / 7,097 / 14,793 digits, and digits per loop rose 0.91 -> 1.68 -> 2.13).

## Verdict

**The machine never halts.** It is a non-halting counter whose tape grows roughly doubly exponentially per
"super-step". It has no sigma or score. The growth-ranking flag was a false positive.

**Confidence: proved, computer-assisted.** Five rules were proved symbolically for all parameter values with a
small prover written for this job (`symsim.py`). All five were then re-checked by an independent literal simulator
on 1,920 small cases. The machine was also checked to reach the family's start configuration from the blank tape.
Caveat: `symsim.py` is new, unreviewed code. Its soundness arguments are short and are listed below, and a
human-readable transcript of every proof step is in `bb7_control_16582/proof_transcript.txt`. If you distrust the
tool, treat this result as "very strong evidence".

**Community status (control check):** the machine is **not a known halter and has no published score.**
- It is a bbchallenge BB(7) **holdout** (undecided). I confirmed it verbatim in Iijil's Phase 1 files
  `7x2_holdouts_01xxxx.txt.gz` (line 672890) and `Decider 1/7x2_2_holdouts_01xxxx.txt.gz` (line 518947).
- It is absent from `7x2_2_halt_00xxxx`, `7x2_2_halt_01xxxx` and `7x2_2_infinite_01xxxx`.
- The web-check subagent also reported it at line 82386 of the Phase 2 Stage 5 holdout list
  (`bb7_holdouts_20405295.txt.gz`). It also reported that the machine is absent from all Phase 2 `solved_halt`
  files and all Stage 6 `solved_infinite` files. I did not re-verify these, because the 258 MB file was deleted
  after grepping.
- The wiki BB(7) Phase 1 row covering it is
  `00-01xxxx | @Iijil | ... | 1RB0LE_1RC0RA_1RD0RC_1LE1LD_1LA0LF_0LA0LG_1RZ0RD | 10 ↑↑ 246.32`. That row's maximum
  belongs to a different machine.
- jhuang97/bb7x2 releases cover only 70xxxx and 71xxxx.

So this control cannot test whether we reproduce a published score. What it does show is that our pipeline plus
subagent analysis correctly resolves a champion-looking flag as a non-halter. It also shows that the
digits-per-loop signal can mislead (see "Lessons").

## Configuration family

The rules are written in plain binary, with no fixed block alignment. `[A0]` is the head, in state A, reading 0.
`(u)^n` is n copies of u. The tape is blank beyond both ends.

```
beta (x,j,k,t) = [A0] 0 (100)^x 1010 (100)^j 1010 (110)^k 10100 (10)^t 1101
gamma(x,j,m,t) = [A0] 0 (100)^x 1010 (100)^j 10   (100)^m 00100 (10)^t 1101
```

- x is the big counter.
- j is an accumulator that grows by 2 per round.
- k and m are the stage counters that fall by 1 per round.
- t is a trail of `10`s that grows by one per super-step and is **never read again**. In every rule the head stays
  at least one cell left of the trail.

## Rules (all proved for x>=1, j,k,m,t>=0; walls mean the tape beyond is never read)

| rule | statement | symbolic proof | literal check |
|---|---|---|---|
| L0 | `000 [A0] 0 (100)^j 1010 (110)^(k+1)` -> `[A0] 0 (100)^(j+2) 1010 (110)^k` (one "bounce") | 20 macro steps | used inside the rows below |
| L0* | `[A0] 0 (100)^j 1010 (110)^k` -> `[A0] 0 (100)^(j+2k) 1010` (left blank) | induction on k from L0 | same |
| R1 | beta(x,j,k+1,t) -> beta(2x+3, j+2, k, t) | 87 macro steps | 768/768 cases |
| T1 | beta(x,j,0,t) -> gamma(2x+3, 0, j+1, t+1) | 99 macro steps | 192/192 |
| R2 | gamma(x,j,m+1,t) -> gamma(2x+3, j+2, m, t) | 85 macro steps | 768/768 |
| T2 | gamma(x,j,0,t) -> beta(2x+3, 0, j, t) | 77 macro steps | 192/192 |

The literal checks covered x=1..8, j=0..5, k,m=0..3, t=0..3. Each rule was run with no acceleration until its
target first appeared. No run halted. The longest single rule instance took 1,090 steps.

Mechanism: each round does the same three things.
1. The head sweeps right, turning `(100)^x` into `(110)^x`.
2. It takes one unit off the stage counter and adds 2 to j.
3. It comes back and "bounces" the x blocks back to the left, 2 blocks for every block consumed (L0*). This gives
   x -> 2x+3.

**Initial segment.** From the blank tape, literal simulation reaches beta(1021, 0, 6, 0) at step 2,801,540
(`check_initial.js`). Nothing halts before it.

## Recurrence and growth

One super-step is:

beta(x,0,k,t) -> (R1 applied k times) -> (T1) -> (R2 applied 2k+1 times) -> (T2) -> beta(x',0,4k+2,t+1),
where x' + 3 = 2^(3k+3) (x+3).

Starting from beta(1021,0,6,0), after s super-steps:

- k_s = (20·4^s - 2)/3, giving 6, 26, 106, 426, 1706, 6826, 27306, ...
- log2(x_s + 3) = 10 + s + 20(4^s - 1)/3, giving 2^31-3, 2^112-3, 2^433-3, ...
- ones = x_s + 2k_s + s + 9. Steps are about Θ(x²), because every bounce re-crosses the growing left run.

Cross-checks:
- A concrete accelerated run that uses only crossing and L0*, not R1/T1/R2/T2, gives exactly x = 2^31-3, 2^112-3,
  2^433-3 with k = 26, 106, 426 (`check_superstep_concrete.py`).
- Quick_Sim's own trace independently shows the stage counters 7, 27, 107, 427, 1707, 6827, 27307 (= k+1 in its
  3-block alignment) at loops 237 ... 4671.
- The pipeline's numbers fit: 14,793 digits at 40 s lies between s=6 (≈8,223 digits) and s=7 (≈32,900 digits).

Non-halting then follows by induction on s. Every transition between consecutive beta/gamma configurations is a
proved rule with no halt, x stays ≥ 1021, and k grows without bound.

## Lessons for the pipeline (candid)

- **The digits-per-loop signal was misleading.** Quick_Sim applies a proved exponential rule at most
  `--max-num-reps`=10 times per loop, which here is 10 doublings, so at most 10·log10(2) ≈ 3.01 digits per loop.
  - The rising sequence 0.91 -> 2.13 is just the approach to that ceiling as the stage counters grow.
  - The champion's 0.84 -> 2.26 may be bounded by the same ceiling, so a 40 s horizon probably cannot tell
    tetration apart from "doubling with growing counters".
  - Suggested fixes: treat ~3.0 digits/loop as a ceiling, not as a champion signature. Look at whether the prover's
    exponents themselves are ever used as counters. Alternatively, run a cheap check for a growing untouched trail.
- **Quick_Sim's rules were usable, but only up to a point.**
  - Its Diff rules were correct and located the doubling mechanism, e.g.
    `110^(a+1) (111)C> 110^(b+2) ... -> a+2, b-1`.
  - The `--verbose-simulator` trace was the main data source.
  - However, its fixed 3-cell block alignment shows the single super-step as three different-looking families
    (`<G (001) 001^X 101^n`, `<D (100) 100^X 110^n`, `<A (010) 010^X 011^n`). This happens because the active region
    drifts 2 cells per super-step against the fixed trail.
  - Re-tokenising the tape in binary with free alignment exposed the single beta/gamma structure.
  - Quick_Sim proved no infinite rule. Ligocki CPS with block sizes 1-12 was inconclusive (`cps_plain.txt`).
- **The subagent process worked.** The symbolic proof
  needed a custom tool because none of the available deciders closed it.

## Reproduction (run from `bb8_list\investigations\bb7_control_16582`, Python = `..\..\..\third_party\venv311\Scripts\python.exe`)

- `python prove_nonhalt.py`: symbolic proofs of L0, R1, T1, R2, T2. Writes `proof_rules.json`.
- `python proof_transcript.py`: writes `proof_transcript.txt`, which has every macro step and the single-block
  crossing facts used.
- `python check_rules_literal.py`: the 1,920 independent literal checks. Writes `check_rules_literal.json`.
- `node check_initial.js`: blank tape -> beta(1021,0,6,0) at step 2,801,540.
- `python check_superstep_concrete.py`: numeric check of three super-steps.
- `python test_symsim_concrete.py 2000000`: checks `symsim.py` in concrete mode against a plain literal simulator
  (43 checkpoints up to 2.0M steps, 0 mismatches).
- Quick_Sim traces: `qs_prover.txt`, `qs_verbose_sim.txt` (1,500 loops) and `qs7000_short.txt` (7,000 loops,
  step counts stripped). The last is from
  `Quick_Sim.py --recursive --max-loops=7000 --verbose-simulator <TM>` (about 230 s).

## Soundness notes on `symsim.py`

- **Literal cells** are stepped exactly.
- **Crossing a run** `u^e` in one move is allowed only if one isolated copy of the block (rotated so the head's
  current cell is its first or last cell) is entered in state q and exited on the far side in the same state q.
  The whole run then follows by induction on e, for every e ≥ 0.
- **Peeling** a copy off a run needs e ≥ 1 to be provable from the parameters' lower bounds.
- **Normalisation** uses only string identities: merging, absorbing copies into runs, `a(ba)^e = (ab)^e a`, and
  compressing literals.
- **Lemmas** apply only on exact token matches.
  - Lemmas proved with a wall never look past it.
  - Lemmas proved with a blank side apply only where that side really is blank.
- **Rule proofs** end only when the configuration, token for token, equals the target relative to the right wall.

## Open questions

- Independent review of `symsim.py`, or a certificate in a format bbchallenge accepts (e.g. a Coq/decider-checkable
  proof), before announcing "holdout 016582 decided non-halting".
- Five other holdouts in `7x2_2_holdouts_01xxxx` share the prefix `1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---` and
  differ only in state G. They may yield to the same method.

Operational note: I once mistakenly set three unrelated Python processes (`render.py --scene s05_debride`) to Idle
priority. They were restored to Normal within about a minute.

## Formal proof

**Result: machine-checked.** `bb8_list/proofs/BB7_16582_1RB1LD.v` (busycoq, Coq 8.20.1) proves
`Theorem nonhalt : ~ halts tm c0.` and **PASSES** `python check.py BB7_16582_1RB1LD.v`: the table matches the
machine string, and `Print Assumptions` reports "Closed under the global context". It compiles in about 70 s. This
replaces the "unreviewed `symsim.py`" caveat in the verdict above.

Structure:
- `beta x j k r` and `gamma x j m r` are the two families above. The untouched tail `(10)^t 1101` is folded into an
  arbitrary right part `r`, which the rules never read.
- There are six run-crossing lemmas, each proved by induction on the run length:
  - C and A moving right across `100` and `001`;
  - A, D and G moving left across `011`;
  - E moving left across `110`.
- `L0` is one bounce and `L0s` is L0*, both with a blank tape to the left.
- `rule_R1`, `rule_T1`, `rule_R2` and `rule_T2` are the four rules as `-->+`.
- `init_reach` goes from the blank tape to `gamma 61 0 3 (1101 0^inf)`.
- `progress_nonhalt_simple` is applied over the whole family, with no side condition.
- The rule proofs are scripts of `execute`, `follow <crossing>` and `align_lpow` rotations, with fixed step counts.
  They were generated by a small planner (`bb7_control_16582/coq_scratch/planner.py`, `explore_rules.py`) that
  mirrors busycoq's `execute` on tapes with symbolic runs.

Where the formalization differs from or sharpens the informal proof (no rule or recurrence was wrong):
- **No lower bounds are needed.** All four rules hold for all x, j, k, m ≥ 0 (informally x ≥ 1), and L0* holds for
  all k ≥ 0 (`proof_rules.json` says k ≥ 1).
  - The reason: each rule applies L0* one bounce earlier than the transcript does, at `(100)^1` with x+1 blocks of
    `110` left, instead of at `(100)^3` with x blocks.
- **The family is entered much earlier.** The first member reached from the blank tape is gamma(61,0,3,0), at step
  11,331. The report used beta(1021,0,6,0) at step 2,801,540. That configuration follows from gamma(61,0,3,0) by
  R2, R2, R2, T2; literal simulation confirms the intermediate configurations at steps 44,432, 176,173 and 701,786.
  - Only 1,047 literal steps are executed in Coq.
  - The four bounce phases of the initial segment start at steps 143, 361, 1,040 and 3,441, with k = 2, 6, 14 and 30.
    Each is jumped over with L0*.
- **The trail parameter t is unnecessary.** Each rule is proved for every right part r. T1 just prepends `10`.
- **Different crossing alignment.** Crossings are stated in the alignment in which the machine first reads a run.
  This differs from `symsim.py`'s block choice, so the transcript's macro-step counts (87/99/85/77) do not carry over.
  Explicit rotations `(x::xs)^^n *> x >> ys = x >> (xs++[x])^^n *> ys` are needed in these places:
  - before L0* in each rule: one rotation in R1, T1 and R2, and two in T2;
  - once more in T2, where the head reads only one cell into the (110)^{j+1} run before turning back.
