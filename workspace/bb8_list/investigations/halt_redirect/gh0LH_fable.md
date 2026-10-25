# Fable second opinion: the D9-counter machine (2026-10-08)

Machine (9 states, I0 undefined = halt): `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH`
(G/H-swap sibling of the BB(8) record with E0 := 0LI, I = ---0LH).  Notation as in FINDING_9state_0LA.md
(D(m) = (10)^m 1, tail (10)^4, canonical state G).  I use the mini-follower's convention r = R+1 (R1: r -> 2r+5,
new digit 2r+5; huge accumulators have the universal residue r = 19 mod 2520, R = 18 mod 2520).

Tools (all in halt_redirect/fable/): gh_run.py (verbose follower built on mf35g.run_stage + follow2.jump with
several representative policies), st.py (one literal stage from a constructed token word), cmp_logs.py,
scan.py / run_start.py (whole runs from constructed start structures), t_*.py (corner tests).  Logs *.log, scans
scan_R1*.txt / scan_R2*.txt.

## Verdict

**HALTS** (confidence: high, ~90% for halting and the stage count, ~85% for the size class).  The real run is
~22.6 B stages long, of which ~8.8 B are full cycles (omega-level clearings at depth = remaining zeros, from
~4.8 B down to 0); the rest (phases B and C, ~13.8 B stages) are exponential-level.  The halt is in state I
reading 0 from the configuration `[2r+7, 8, 1^3, 0, 1, 3, 0, 2, 1^2 | 1 | r']`, exactly the mini-follower's
`k=12 z=2 -> H I0` ending of the b0 = 46 / 166 runs.  No rebuild, no second round.

Size: sigma = 2R_end + 2R'_end + 48 where R_end is the accumulator entering the last literal stage.  R_end is the
phase-A accumulator pushed through ~13.8 B further exponential/tower steps, so in FGH terms (H_d ~ f_(d+1); one
cycle at zero-depth d is r -> H_d^((2r+4)/3) ~ f_(d+2)(r)):

    f_(4.8B+2)^11(2)  <  sigma  <  f_(4.8B+3)(9B)      (B = the record's accumulator, 2B+4 = 2^^37 3),

i.e. roughly 2 ^(4.8B+2 arrows) (9B).  Write K = m_1 = (24B+191)/5 ~ 4.8B for the zero-list length; the
maximum clearing depth of this machine is K+1 (the first cycle), so sigma < f_(K+3)(9B).  Ranking (corrected
2026-10-08 after the lead's note): above our BB(9) record (one f_(12B9) application, B9 from 2^^13 3, K >> 12B9);
BELOW the three-cycle F/H sibling, whose stage 2 rebuilds D4^(m+40) with m = K (verify_fh.py, literal), so its third
clearing is one list clearing at depth K+41 from small a = 12, b = 6: sigma_3cyc ~ f_(K+42)(small), and
f_(K+42)(5) = f_(K+41)^5(5) >> f_(K+3)(9B) because the index wins over the number of cycles; and below the other
session's 10-state M3 if M3's analysis holds (four nested clearings at depth ~8B+50: f_(8B+51)^4).  My first
version of this report ranked the D9 machine above the three-cycle sibling by counting cycles (8.8B vs 3) and
ignoring that the sibling's third list is 40 longer than K; that was wrong.  The lead's "~f_(4.8B+1), ~22 stages per unit of b" is confirmed up to index conventions, with the
refinement that only ~8.8 B of the ~22.6 B stages are omega-level cycles.

## 1. Macro dynamics (derived from the representative runs, then checked in the real size ordering)

Start: stage 0 (literal) from the record's E0 configuration after K(0^35; 0; b), b = 1 mod 5:
`[9^u, 11, 1^(2u+36) | 1 | 2]` with u = (12b+8)/5 (D9 count); the first jump gives `[9^u, 8, 3, 1^(2u+35) | 1 | R]`.
Real values: u_1 = (12B+8)/5 = 16 mod 504 (= 100 mod 420, = 0 mod 8, = 16 mod 24), m_1 = 2u_1+35 zeros
= 67 mod 12096.  b0 = 6 is in B's class mod 2520 (B = 6 mod 2520); b0 = 46, 166 are not.

**Transient (stages 0-36):** three D9 are consumed (stages 2, 9, 20); the counter region settles to
`[9^(u-3), 6, 24, 24, 10, 0, 0]` (24 = 2r-14 of an early accumulator: a parked huge token, constant afterwards).

**Phase A (period 11 stages, 6 zeros per period, one huge token parked per period).**  With Z zeros and r the
accumulator (always the universal residue), the period from `[.., 17, 10, 0, 0, 43, 0, 0, 43, 1^Z | 1 | 1]`
(43 = 2r+5; the first 43 is the previous period's token) runs, K-moment -> jump:

    43 0 0 43 1^Z           -> J (clear 43 at depth Z+1, block at D0)   -> 43 0 0 1^(Z+1)
    39 2 0 42 1^Z           -> J (42 = 2r+4 counter -> 3 at depth Z+1)   -> 39 2 0 3 1^Z
    39 2 0 0 43 1^(Z-1)     -> J                                         -> 39 2 0 0 1^Z
    36 2 1 0 42 1^(Z-1)     -> J                                         -> 36 2 1 0 3 1^(Z-1)
    36 2 1 0 0 43 1^(Z-2)   -> J                                         -> 36 2 1 0 0 1^(Z-1)
    32 4 0 0 1 42 1^(Z-2)   -> J                                         -> 32 4 0 0 1 3 1^(Z-2)
    32 4 0 0 1 0 43 1^(Z-3) -> J                                         -> 32 4 0 0 1 0 1^(Z-2)
    32 1 3 0 0 43 1^(Z-4)   -> J                                         -> 32 1 3 0 0 1^(Z-3)
    29 4 0 1 41 1^(Z-3)     -> J (41 = 2r+3 -> 2)                        -> 29 4 0 1 2 1^(Z-3)
    25 6 0 0 44 1^(Z-3) | 1 | 2  -> J (non-standard r: 44 -> 41, 3)      -> 25 6 0 0 41 3 1^(Z-4)
    25 6 0 0 41 0 43 1^(Z-5) -> J                                        -> 25 6 0 0 41 0 1^(Z-4)
    17 10 0 0 43 0 0 43 1^(Z-6)   (next period; the parked 17 = 2r-21 is the old 43 after -4,-3,-4,-3,-4,-8)

Every jump of the period clears a 2r+c token sitting at the head of the zero list, i.e. H_(Z') applied (2r+c')/3
times: a full cycle at depth Z' ~ Z.  Phase A ends when the zeros run out: N_A = 11 m_1/6 + O(10) stages
(b0 = 6: 131-138, b0 = 46: 490, u = 520: 1977).  Parked region after phase A:
`[9^(u-3), 6, 24, 24, 10, 0, 0, (17, 10, 0, 0)^N]`, N ~ m_1/6 blocks, the parked tokens 17 = 2r_j - 21 strictly
increasing to the right (in the real run astronomically increasing).

**Transition A -> B (literal, 10 stages, b0 = 6 stages 131-141):** a chain of a-tokens 43 -> 89 -> 380 -> 891
-> 2121 -> 4415 (each 2r+c of the previous R1-round result: exponential-level), then one "far junk" stage that
re-encodes only the LAST block (`17 10 0 0 20 2 -> 17 9 0 <junk> 47 105`) and the next stage restores the token
form `(17 10 0 0)^(N-1) 6 205`.  All other tokens untouched (checked literally in the size-ordered run).

**Phase B (period 18 stages, consumes 2 parked blocks per period; 9 stages per block).**  One period, from
`[.., (17 10 0 0)_(k-1), 13 9 2 0 | 0 | r]` (b0 = 6 stages 146-164):

    13 9 2 0 | 0 | r         -> 5 (6r-2) | 1 | 1           [literal: the parked 13 = 2r_k-25 loses 8; 6r-2 is a digit]
      J: 6r-2 cleared at depth 1, the borrow continues into the parked 5 = 2r_k-33 (a counter) down to 2 -> 2 1 | 1 | R
    (17 10 0 0) 2 1 | 1 | r  -> 17 6 2 0 (2r+5) 1 | 1 | 2  ; J (non-standard) -> 17 6 2 0 (2r+2) 3
    17 6 2 0 40 3 | 1 | r    -> 17 6 2 0 40 0 | 2r+5 | 1   ; J -> same | 1 | R
    17 6 2 0 40 0 | 1 | r    -> 17 4 (2*40+3) 1 | 1 | 1    ; J (83 counter -> 2) -> 17 4 2 1 | 1 | R
    17 4 2 1 | 1 | r         -> 17 1 (2r+6) 1 | 1 | 2      ; J -> 17 1 (2r+3) 3
    17 1 41 3 | 1 | r        -> 17 1 41 0 | 2r+5 | 1       ; J -> | 1 | R
    17 1 41 0 | 1 | r        -> 16 (2r+2) 41 1 | 1 | 1     ; J (41 -> 2) -> 16 40 2 1
    16 40 2 1 | 1 | r        -> 16 37 (2r+6) 1 | 1 | 2     ; J -> 16 37 (2r+3) 3
    16 37 41 3 | 1 | r       -> 16 37 41 0 | 2r+5 | 1      ; J -> | 1 | R
    16 37 41 0 | 1 | r       -> 16 32 20 (5*41+16) | 1 | 1 ; J (221 -> 2) -> 16 32 20 2
    16 32 20 2 | 1 | r       -> 16 31 (2r+10) (5r+10) | 1 | 1 ; J (105 -> 3) -> 16 31 48 3
    16 31 48 3 | 1 | r       -> 16 31 48 0 | 2r+5 | 1      ; J -> | 1 | R
    16 31 48 0 | 1 | r       -> 11 (31+2*48+10r+1) | 1 | 1 ; J (317 -> 2) -> (17 10 0 0)_(k-2) 11 2
    (17 10 0 0) 11 2 | 1 | r -> 17 3 (2r+10) (5r+5) | 1 | 1 ; J (100 digit, then 48 -> 3) -> 17 3 3 1
    17 3 3 1 | 1 | r         -> 17 3 0 (2r+5) | 1 | 1      ; J -> 17 3 0 1
    17 3 0 1 | 1 | r         -> 13 5 0 0 | 2r+5 | 1        ; J -> | 1 | R
    13 5 0 0 | 1 | r         -> 13 1 2 0 | 2r+4 | 1        ; J (a-block at 3) -> | 3 | R'
    13 1 2 0 | 3 | r         -> 13 1 2 0 | 0 | 2r+5        ; J (a-block)
    13 1 2 0 | 0 | r         -> 5 (6r-17) | 1 | 1          (= the first line of the next period)

Every parked token is consumed by the champion process (a jump borrowing a counter down to 2), never by a literal
stage: the literal stages only subtract constants (-4, -8, ...).  No accumulator ever "pays" for a parked token.
After the last block the head `6 24 24 10 0 0` is consumed the same way (b0 = 6 stages 201-218).

**Phase C (the D9 counter; period 22 stages, 8 D9 per period):** after a 21-D9 transient (R1(40) stages
380-421, the same for every u >= 40), the period from `[9^v, 8, 0, 43 | 1 | 1]`:

    9^v 8 0 43 -> 9^(v-1) 5 10 0 0 | 43 -> 5 6 2 0 | 42 -> (a-block, R) -> 9^(v-1) 3 94 -> 9^(v-1) 0 43
    -> 9^(v-3) 5 11 0 0 | 43 -> 5 7 2 0 | 42 -> (a-block) -> 9^(v-3) 0 102 -> 9^(v-3) 0 0 | 43
    -> 9^(v-4) 5 2 0 | 42 -> (a-block) -> 9^(v-8) 8 12 1 117 1 -> 8 12 1 114 0 | 43 -> 8 11 113 41 1
    -> 8 11 110 44 1 -> 8 11 110 41 0 | 43 -> 8 11 105 20 221 -> 8 11 104 48 105 -> 8 11 104 48 0 | 43
    -> 9^(v-8) 8 9 403 -> 9^(v-8) 8 0 43.

Each jump here clears a 2r+c token at depth 0 or 1 (exponential / single tower level).  ~2.75 stages per D9.

**Endgame (v = 0 mod 8 at the periodic start, i.e. u_1 = 0 mod 8):**

    8 9 403 | 1 | 1  -> J -> 8 3 1 | 1 | R  -> 8 0 (2R+5) | 1 | 1 -> J -> 8 0 1 | 1 | R'
    8 0 1 | 1 | R'   -> [2R'+7, 8, 1^3, 0, 1, 3, 0, 5, 1^2 | 1 | 1]  -> J (5 -> 2 at depth 3) -> [.., 2, 1^2 | 1 | R'']
    -> HALT in I reading 0, ones = 2R'' + (2R'+7) + 2*3 + 35.

(For u_1 = 16 mod 504 the D9 count at the periodic start is u_1 - 24 = 0 mod 8.)

## 2. What the mini-follower hid, and why it does not matter here

* The b0 = 6 run ends differently (a REBUILD `[2r+189, 9^6, 8, 3, 1, 0, 0, 9, 1^13]`, then a second small round
  and a halt after 298 stages).  That is a small-u artefact: phase C needs 21 D9 for its transient and b0 = 6 has
  only 13 left.  Every u >= 40 with u = 0 mod 8 (u = 40, 64, 88, 112 (= b 46), 136, 160, 184, 400 (= b 166), 520)
  ends with the `[2R+7, 8, 1^3, 0, 1, 3, 0, 5, 1^2]` halt, and u = 520 is exactly the real class u = 16 mod 504
  (m = 1076; 4996 stages: phase A to 1977, phase B to 3621, phase C to 4996).  Across u = 0 mod 8 the tested set
  covers all residues mod 5, 7 and 9, so the endgame depends on u mod 8 only (plus m mod 6, fixed by m = 2u+35).
* The rebuild, where it occurs (small u), has u_2 = (X-11)/5, m_2 = (2X-17)/5 with X = 2r'+3 a huge accumulator
  token: in the real run such a rebuild would start a second omega-level round of depth ~0.8 r'.  So for OTHER
  residue classes (or if the phase-C transient were different) the machine would be much bigger (f_omega iterated)
  or possibly non-halting.  In the real class it does not happen.
* The representative world merges several literal stages into one whenever the intermediate accumulators are
  <= RCAP = 600 (stage35g's "small process" rule).  This is why the all-19 and all-2539 runs diverge in stage
  NUMBERS from stage 132 on (and why the standard run shows maps like `32 4 0 0 1 0 | 1 | 19 -> 29 4 0 1 | 89 | 1`);
  the dynamics are the same.  All my corner tests (t131/t132/t_end/t_end2/t_endC/t_halt) show exactly this
  granularity effect and nothing else.

## 3. Literal checks in the REAL size ordering (r >> every parked token, parked tokens increasing to the right)

* `gh_run.py --policy shrink`: every new accumulator is represented in the window [19+2520k, +2520) (k = 2: 5059,
  k = 3: 7579) while every parked token is kept in [19, 2539) with its residue mod 2520, so r >= 3 x (any parked
  token) throughout.  b0 = 6, k = 3 (shrink3_b6.log): the same event sequence as the standard run through phases
  A, B, C and the (small-u) rebuild, the same parked-token decrements (17 -> 13 -> 5 -> 2 ...), HALT at stage 327
  with ones 16064 = 2*7579 + 4*225 + 6 (the halting-stage formula).  R1(40) with k = 1 (r1_40_shrink1.log): the
  same D9 profile and the same endgame as the standard run, HALT at stage 525 (476 in the standard run; the
  difference is granularity), ones = 5164 = 2*2539 + 45 + 6 + 35.
* All-2539 run (`--policy big`, big1_b6.log): identical to the all-19 run for 131 stages with every huge-derived
  token exactly 2*2520 larger (coefficient 2 in r), the parked tokens included; then granularity splits only.
* Two-parameter corner tests, each at (parked P, r) in {P, P+2520, P+5040} x {19, 2539, 5059}: the stage-131 and
  stage-132 maps (t131.py, t132.py: output independent of P, affine in r), the rebuild/non-rebuild stage
  `[3 X 0 | 1 | r]` (t_end.py, t_end2.py, end_chain1.log: both granularity branches lead to the same
  `[2r+189, 9^((X-11)/5), 8, 3, 1, 0, 0, 9, 1^((2X-17)/5)]`), the final halting stage `[A 8 1^z 0 1 3 0 2 1^2 | 1 | r]`
  (t_halt.py: HALT for A in {45, 2565}, z in {3, 5, 216, 1500}, r in {19, 2539}; ones = 2r + A + 2z + 35; the step
  count 6015 is independent of z, so the head never visits the zeros), and the three endgame maps
  `[8 0 1 | 1 | r] -> [2r+7, 8, 1^3, 0, 1, 3, 0, 5, 1^2]` (z = 3 for every r), `[8 3 1 | 1 | r] -> [8 0 2r+5]`,
  `[8 11 P Q 0 | 1 | r] -> [8 9 1.5P+1.5Q+9r+4]` (t_endC.py).
* Where could an accumulator from a short clearing pay for a token from a long one?  Nowhere: the only consumers of
  parked (long-clearing) tokens are jumps (the champion process borrows them down as counters; the number of
  borrows is paid in time, not by another accumulator), and every literal stage subtracts constants from them.
  The M3 pattern (an unpack stage comparing R with x) does not occur: the only stage that unpacks an accumulator
  into a list is the rebuild, and it is never reached in the real residue class.

## 4. Counts and bounds (real run)

* zeros m_1 = (24B+191)/5 ~ 4.8 B; D9 u_1 = (12B+8)/5 ~ 2.4 B; parked blocks N ~ m_1/6 ~ 0.8 B.
* phase A: N_A = 11 m_1/6 + O(10) ~ 8.8 B stages = 8.8 B full cycles, the j-th period at depth m_1 - 6j.
* phase B: ~9 N ~ 7.2 B stages (exponential/tower level); phase C: 2.75 u_1 ~ 6.6 B stages (exponential level).
* total ~ 22.6 B + O(100) stages (fit from b0 = 46, 166: 22.6 b + 115).
* sigma = 2 R'' + 2 R' + 48 (R' = the accumulator entering the final literal stage, R'' = the last small jump,
  a tower of height 65535): between f_(4.8B+2)^11(2) and f_(4.8B+3)(9B) in FGH (H_d ~ f_(d+1)).
* Maximum depth K+1 = m_1+1: no list in this run is ever longer than the initial zero list (the rebuild, which
  would be, is not reached).  Hence the ranking: BB(9) record < D9 machine < three-cycle F/H sibling
  (f_(K+42)(small)) < M3 (10 states).

## 5. Agreement / disagreement with the lead's evidence

Agree: the stage chain, ~22 stages per unit of b, halting in I reading 0, omega-level 1 with index ~4.8 B;
the three-cycle sibling (depth K+41) is larger (lead's correction, accepted).
Refinements: (a) only phase A (~8.8 B stages) consists of full cycles, phases B and C are exponential-level;
(b) the b0 = 6 history is NOT representative of the real endgame (it rebuilds; the real class behaves like
b0 = 46 / 166 and u = 520); (c) the parked huge tokens are consumed by jumps, which is why the single-representative
follower is faithful here, unlike for M3.

## 6. Open points

* Everything above the literal level rests on follow2's jump() (the champion rules R1-R3 plus the counter/blocker
  treatment, Coq-proved only for the record's own contexts) and on the periodicity of the endgame in u mod 8 /
  m mod 6 (tested for u up to 520, including the exact real class mod 504).  A Coq proof would need the phase-A
  period as an induction, the phase-B period, the phase-C period and the endgame.
* The size bound is coarse (index 4.8B+2 vs 4.8B+3); a tighter statement needs the exact H-bookkeeping of the
  first few periods.

## 7. Comparison with the Opus verifier (inv-gh0LH-verify)

At the time of writing (2026-10-08, after my verdict) halt_redirect/gh0LH_verify.md does not exist.  The
verifier's working folder (halt_redirect/ghv/) only holds interim logs whose RESULT lines are failures of its own
symbolic follower: "non-affine dependence pos ..: 1 4" / "205 880" and "token count depends on huge #0 ...:
86 vs 1526; from 0 1^3 H[-6|18]".  The last one is the rebuild (its token count u_2 = (X-11)/5 grows with the
accumulator token X), the others look like the RCAP granularity merges described in section 2.  Both are
consistent with my analysis; no disagreement can be recorded until its report exists.  If it concludes
"halts, ~22 B stages, ~f_(4.8B+1)" we agree; if it reports a second omega-level round (rebuild), that would be the
small-u artefact of b0 = 6 (section 2), which the real class u_1 = 16 mod 504 does not reach.

## 8. Calibration of the 'big'/'shrink' timeouts (lead's note, 2026-10-08)

No conclusion in this report rests on a 'T' outcome.  The two timeouts I had (big1_b6.log: stage 137 at the
2e8 budget; r1_40_big1.log: stage 250 at the 1e9 budget) are both the A -> B transition, where the literal stages
carry a-tokens 2r+c, 4r+c, 8r+c ... of a 2539-window accumulator; the literal cost grows ~ r^2 (measured: r = 2539:
2.6e7 steps, 5059: 1.0e8, 7579: 2.3e8 for a plain 2r+5 stage).  The same transition was passed by the shrink runs
with a 1.5e9 budget (shrink2_b6.log, shrink3_b6.log, r1_40_shrink1.log), which then ran to HALT with the standard
run's structure.  So the only size-ordering divergence I ever saw is a timeout, not a different structure.
Calibration on 0LA's G/H twin (`..._1LC0RG_---0LA`, GHM env var in gh_run.py), budget 1.5e9: std -> HALT after 2 J
(ones 346); shrink bigk = 3 -> HALT after 2 J (ones 15466, final stage 2.4e8 steps); big bigk = 3 -> same.  At the
lead's 5e7 budget the r = 7579 stage cannot finish, which explains the T seen there.
