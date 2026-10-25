# BB(10) lead `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC`

Agent inv-bb10-lead-0LJ0LC (Opus 5.5), 2026-10-07/08. Tools and Coq sources are in `bb10_lead_0LJ0LC/`.
- Source: c35m14, the BB(8) record's TNF prefix plus 2 free states.
- Flag: dlscan3 graded it MULTI k=1 (`nested_detector/`).
- Independent literal check by the lead: `bb10_lead_0LJ0LC/lead_check/lead_check.py`, 0 mismatches. Session bb8-ab
  re-derived the formula independently.

## Verdict

**HALTS: machine-checked (check.py PASS), and it beats the BB(10) champion (also machine-checked).**

    sigma = 2 * (2^^L 5) + 2 L - 2,      L = 4 * (2^^27 3) + 17          (2^^k n = 2 ^(k arrows) n)

Verbatim check.py result:

    PASS BB10_lead_1RB0RA.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC HALTS (machine-checked, no axioms)

| file (bb8_list/proofs) | content | status |
|---|---|---|
| `BB10_lead_1RB0RA.v` | `Theorem halt : halts tm c0`: every rule for all parameters, plus the 3890-step start-up by execution | **check.py PASS** |
| `BB10_lead_bound.v` | `score_exact`: ones at the halt = 2 b2 + 2 (4 bf + 33) + 5; `bf_closed`: bf + 4 = 2^^27 3; `b2_closed`: b2 + 4 = 2^^(4bf+33) 5; `score_closed`: ones + 1 = 2 (2^^L 5) + 2L - 2 | built, Closed under the global context |
| `BB10_lead_vs_champion.v` | `candidate_beats_champion`: champion ones + 1 < ours + 1, against the champion's exact `BB10_champion_bound.score_exact` (b2c + 3 ones); `sigma_gt_f_omega2_25`: sigma > f_omega(f_omega(25)) | built, Closed under the global context |

Size: about f_omega(2^^27 3), i.e. f_omega applied to an f_28-level number. The champion's second exhaustion b1c is
at most F_26(48), below our first exhaustion b_f = F_26(F_26(0)). After that, both runs have one f_omega-type stage,
over lists of length about 4 b_f (ours) and about 0.75 b1c (the champion's).

## 1. Configuration family

The family is read at the right tape end, with the head in state G on the blank. Groups are listed far end first:

    N(n_1, ..., n_k) = 0^inf 1 ((10)^n_1 1) ((10)^n_2 1) ... ((10)^n_k 1) G> 0^inf

- n_k = 2b+1 is the accumulator b.
- n_2..n_{k-1} = 2d+1 are the digits.
- The far entry n_1 is either a digit (odd), or, after a rebuild, an even top entry whose zero is n = 0.

In Coq, `N a k g l` is an accumulator of a units, then k zero digits (`(10) 1` each), then a group of g units, then
the rest l of the word.

## 2. Rules

All rules were first checked by literal simulation, then proved in Coq for all parameters.

| rule | statement | literal checks (`verify_rules.py`, `verify_rebuild_halt.py`) |
|---|---|---|
| R1 | (.., d+1 \| b) -> (.., d \| b+2) | among 12,240 constructed lists, 0 mismatches |
| R23 | (.., x+1, 0^(k+1) \| b) -> (.., x, b+2, 0^k \| 0) | same set; it includes even tops 0..8 and random lists of up to 40 digits |
| R23 top | top entry 2 -> 0 (the word then starts 11) | same set |
| REBUILD | C(0^m \| b), with every digit zero (odd top), -> N(6, 0^(4b+m+6) \| 0) | 1,947 cases: m = 1..30 with b = 0..60, plus m = 27 with b up to 2048 |
| HALT | N(0, 0^L \| b), L >= 1 -> J reads 0 (J0 undefined); ones = 2b + 2L + 5 | 2,700 cases: L = 1..60, b up to 1000 |

The only exception is N(0 | b), a top entry 0 with **no** zero digits. It does not halt: it rebuilds into an odd-top
list. This is the start-up mechanism. The real run halts with L >= 33.

Clearing: F_0(b) = b + 2 and F_(j+1)(b) = F_j^(b+2)(0). A digit with u units at depth j maps b to F_j^u(b).
In closed form, F_(j+1)(x) + 4 = 2^^j (x + 4), where 0 arrows means multiplication.

## 3. The run

| step | configuration | event |
|---|---|---|
| 177 | N(6 \| 0) | start-up: top entry 6, no zero digits |
| 393 | N(0 \| 6) | after 3 R1 steps; this shape rebuilds |
| 3890 | N(5, 1^26, 1) = C([2, 0^26] \| 0) | first list: top digit 2 at depth 26 (27 digits) |
| | C(0^27 \| b_f), b_f = F_26(F_26(0)) = 2^^27 3 - 4 | first exhaustion |
| | N(6, 0^L \| 0), L = 4 b_f + 33 | REBUILD: even top 6, i.e. three units at depth L |
| | N(0, 0^L \| b_2), b_2 = F_L^3(0) = 2^^L 5 - 4 | the top entry is used up |
| | J reads 0, ones = 2 b_2 + 2L + 5 | halt: sigma = ones + 1 = 2 (2^^L 5) + 2L - 2 |

The top entry's parity decides between rebuild and halt.
- The first list's top is odd: 5 -> 3 -> 1, which is a zero digit. The all-zero list therefore rebuilds.
- The rebuilt list's top is 6. Three units take it to 0, and an all-zero list with top 0 halts.

This is dlscan3's chain "R F F H": one rebuild, the top units, then the halt.

No residue of a huge number decides anything. The rebuild is linear in b and m. The top parity is fixed: odd in the
first list, 6 after the rebuild. The Coq proof covers all parameters.

Further literal validation:
- `traj.exe 3e10` follows the real run for 3e10 steps. It sees 107,548 family events, each equal to the predicted
  successor. The only exceptions are in the start-up: the rebuild at step 3890 and one parse failure at step 2392.
- `fam.exe` end-to-end runs halt with exactly the predicted ones:

  | start | ones | halting step |
  |---|---|---|
  | N(6,1,1) | 63 | |
  | N(6,1,3) | 79 | |
  | N(4,1,1,1) | 131073 | 22,907,804,645 |
  | N(2,1,1,1,1) | 131075 | 22,908,853,404 |

## 4. Comparison with the BB(10) champion

The champion is `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ` (Racheline). Its exact score
is in `BB10_champion_bound.v`: ones = b2c + 3, so sigma = b2c + 4. The definitions:
- b1c = Tv 7 1 7, b2c = Tv (b1c/4) 1 7;
- Tv m j B = U(j+3m+2)(U(j+3m+2)(Tpre m j B));
- U 0 x = 3x + 7, U (j+1) x = (U j)^(x-2j) (X j).

The steps of `BB10_lead_vs_champion.v`:
1. `Dom`: U j x <= F_(j+1)(F_(j+1)(x)) and X j <= F_(j+1)^(4j+2)(0), by induction on j. The case x < 2j uses
   F_(j+2)(0) >= 4j + 8. This domination is tight: it costs at most one doubling of the arrow level, not two.
2. `Tpre_le` and `Tv_le`: Tv m 1 7 <= F_(3m+5)(6m+6).
3. `b1c_le`: b1c <= F_26(48) <= F_26(F_26(0)) = b_f, because F_26(0) >= 104.
4. `b2c_le`: with m = b1c/4 <= b_f, b2c <= F_(3m+5)(6m+6) <= F_L(F_L(0)) <= F_L(F_L(F_L(0))) = b_2. This uses
   3m+5 <= L and 6m+6 <= 4L <= F_L(0).
5. So our ones count, 2 b_2 + 2L + 5, exceeds b2c + 3. With the champion's `final_arith`, sigma also exceeds
   f_omega(f_omega(25)).

This proof does not use `BB10_champion_upper.v` (inv-bb10-champion's Lemma S: b1 <= 2^^25 49 and b2 + 4 <= 2^^N' (2N')).
That file is an independent second route to the same comparison.

## 5. How the proof is built (reproduction)

All of the following is in `bb10_lead_0LJ0LC/coq/`.
- `parts2.py` defines the waypoint shapes:
  - W(j,i), the walk of the accumulator to the left: `P (110)^j 1 1 (10)^(a+3) 1 E> 1 (101)^i`;
  - R(i,j), the return after a borrow: `Q (110)^i 1 1 G> 1 0 0 (101)^j`;
  - Y(u,i), the left-end rebuild loop: `(10)^u 1 E> 1 (101)^i`.
- `gen_all.py` explores each piece with `mexp.py`, a local copy of the BB(9)-record symbolic explorer, and writes the
  Coq lemmas. The pieces are R1, R2, R2z, PRE, WALK, BOR, BORz, BORn, RET, END, LASTW, YC, YEND and HEND.
- `glue.v.in` is hand-written. It contains:
  - the shapes and the inductions WALKS, RETS, YCS;
  - NR1, NR23, NR23z, REBUILD, HALTN;
  - the abstract part: F, CLR, CLRtop;
  - the run, with sealed constants bf and b2.
- `gen_halt.py` assembles the halting file. `bound.v.in` and `vs.v.in` are the other two files; `@LIB@` is BB8 in
  proofs/ and Dev locally.
- `coqc_bn.py FILE.v` compiles against busycoq, proofs/ and this folder (as Dev). It now runs at Idle. Most compiles
  of this session ran at BelowNormal: on the saturated PC an Idle coqc did not finish a trivial file in 15 minutes.
  The final build.py and check.py runs used their default priority.
- Final checks, from `bb8_list/proofs`:
  `python check.py BB10_lead_1RB0RA.v; python build.py BB10_lead_bound.v BB10_lead_vs_champion.v`

Literal tools, in `bb10_lead_0LJ0LC/`:
- `gparse.cpp` and `fam.cpp`: the family parser and a batch simulator. They report every parse failure.
- `verify_rules.py` and `verify_rebuild_halt.py`: rule sweeps that exit nonzero on any mismatch.
- `traj.cpp`: the real-trajectory checker.
- `reach.py` and `coq/ctrace.py`: traces used to find the waypoints.

## 6. Lessons

- **Explorer bug in `mexp.explore` (the BB(9) tool), fixed in the local copy only.**
  - Old behaviour: when a stage got stuck with no loop, the explorer split a variable v at the stage start.
  - Why that is wrong: in the v = 0 branch, earlier stages may already have run past the target, because the target
    check sees only the symbolic configuration. This produced spurious "stuck reading l" failures.
  - Fix: split at the node start.
- The R3 borrow over k zero digits, and the rebuild, were found only with waypoints. They are walk, borrow, return
  and left-end rounds, read off literal traces. With the waypoints, every piece explored in under 1 s.
- Always instantiate rewrites. `rewrite arrow_0` and `rewrite iter_add` without explicit arguments matched the wrong
  subterm.
- No tactic may see closed huge terms:
  - bf and b2 are sealed as Qed'd sigma types;
  - F is Opaque in the comparison file;
  - lia only ever sees variables or opaque atoms; `f_omega (f_omega 25)` is generalized before lia.

## 7. Relatives, open questions

**The J1 = 1RB relatives are weaker, not stronger. Not records.** At first they looked bigger, because the start-up
writes (0 11)^55 instead of (0 11)^28.
- (a) `..._1RE1RI_---1RB`: the start-up N(0|25) gives [8, 1^53 | 1] at step 12089, then [6, 5^52, 7 | 1].
- (b) `..._1RE1LI_---1RB`: it gives [6, 1^45, 3] at step 10285, then [4, 5^44, 7 | ..].

In both, the start-up rebuild already yields an **even** top entry, and an even top halts when it is used up. Checked
on (a) and (b): N(0,1,1,1|7) halts with J reading 0, while an odd-top all-zero list rebuilds. So there is no second
list and no f_omega stage. Their rules are base-3 (R1: digit -1 unit, accumulator +3 units; a borrow gives B+3), and
the score is about 3^^~50.

dlscan3's chain "R F F F H" for them starts from a constructed odd-top exhaustion that the real run never reaches.
What makes 0LJ0LC strong is the opposite parity: its start-up rebuild N(0|6) gives an ODD top 5, which forces one full
exhaustion followed by the f_omega rebuild.

Other relatives and open points:
- The J1 = 0LB relatives (`..._1RE{0LI,1LI,1RI}_---0LB`) show only about 20-24 digits.
- The step count was not computed; the score is exact.
