---
name: w2-12state-search
description: f_(omega+2) 12-13 state search (started 2026-10-09): bases G6 (looper, rounds reload counter) and n1 (J0 gadget); brief + agents in investigations/w2_search/
metadata:
  type: project
---
User (2026-10-09): "find a 12-13 state one at the w+2 level" after n1's BB(10) success.
- Brief: bb8_list/investigations/w2_search/BRIEF.md. Tier 1 = halts after >= 2 full f_(omega+1) rounds (beats n1 hugely);
  Tier 2 = rounds ~ b or ~ accumulator (true f_(omega+2)).
- Bases: G6 (10-state non-halting, every exhaustion re-parks a ~0.8R counter = f_(omega+2)-shaped; needs outer counter d
  + halt; J1 free) and n1 (J0 = halt slot; event H already turns an accumulator into a counter).
- Opus agents launched 2026-10-09 ~13:00: inv-w2-g6 (w2_search/g6/), inv-w2-n1 (w2_search/n1/); reports REPORT.md there.

**Why:** next record tier after n1; BB17/18 champions show the layer template but spend 6 states on it.
**How to apply:** check REPORT.md files before relaunching; see [[bb17-bb18-champion-anatomy]], [[bb10-selector-c1-counter-grower]].

**Interim 2026-10-09 afternoon:**
- n1 slice: L12 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK0RC (J0=0LK) is a
  12-state CLEAN-ROUND LOOPER: the eater turns the far D2 run into digits, then n1's own no-far restart (counter 4R+3)
  runs; rounds at stages 0/47/94/141 (std follower, b0=6); works for k = 1,2 mod 3. No halt (every round ends in the
  same class mod 10080). Scaling with R not yet checked with the big policy (lead asked). Without far bits, n1 restarts
  rounds by itself: the far region is what makes it halt.
- G6 slice: no k-gram (k <= 6) is unique to round boundaries, so clone hooks of <= 5 states can't fire only there;
  far-left structure never survives a left event (it unpacks ~8R cells leftward).
- **G6 slice CLOSED NEGATIVE (inv-w2-g6, 2026-10-09 evening, w2_search/g6/REPORT.md):** the left-end unpack overwrites
  ~8R cells left of the list each round; 1530 far-left patterns all erased/merged; gs13 12-state capped enum 78,745 stage
  runs, 0 late halts. A G6 route needs >= ~6 states (marker pushed ahead of the unpack). Lesson: prefer bases whose
  counter refill is in place / engine grows one way (BB17). L12 inherits the same leftward-unpack wall.
- Session bb8-00 (user-directed) runs inv-w2-n1right (w2_search/n1right/, d parked RIGHT of the accumulator) and
  inv-w2-tier1 (w2_search/tier1/, L12 residue two-round halters), 1 process each, excluding g5s3 K0=0LA/0LC ns=3.
- n1 slice also found M13a = ..._0LK0LC_0LC0LL_0LA1RM_0RM0LE (13 states): restart counter = 2*depth-52 (depth-sized,
  big-policy checked), round 3 restarts too; uses every slot, never halts.

**Routes 2/3 launched 2026-10-09 ~16:05 (session bb8-00, user: "explore routes 2 and 3"), Opus, 1 compute process each:**
- inv-w2-n1right (w2_search/n1right/): can an outer counter d live RIGHT of n1's accumulator (left end proven dead)?
  Right-end survival test at big R, round-boundary-only hooks, then <= 13-state gadget enumeration.
- inv-w2-tier1 (w2_search/tier1/): the L12 residue route (round-2 counter class in J0 class, far k-class where the eater
  halts) = halt after exactly 2 rounds. Excludes the lead's genum5 ns=3 K0=0LA/0LC trees. Reports: REPORT.md in each dir.
- Route 1 (compress BB17's 6-state w+2 layer onto its one-sided A-G engine) is not launched yet.
- **n1 slice DONE 2026-10-09 ~23:10 (inv-w2-n1, w2_search/n1/REPORT.md): no Tier-1/2 halter.** ~160k follower leaves
  (ns 1-3, partial trees). STRUCTURAL NEGATIVE: after a clean restart every round ends identically mod 10080, so
  clean restarters (L12) cannot count rounds; n1's leftward unpack (~6R cells) forbids d on the left. Tier 1 needs
  class-varying restarts (M13a) + a slot read only at one class's round end (M13a at 14 states: cs14.py, ~52 variants).
  Tier 2 on n1 = 15+ states (d in the depth list or an in-place prefix). Remaining 13-state K0-seed sweep
  (n1/run_k0.sh; 0LA/0LC partial, no .done) handed to bb8-00's inv-w2-tier1 (not run by the lead).
- n1 slice FINISHED (w2_search/n1/REPORT.md). Structural negative: after a clean restart every round ends identically
  mod 10080, so a gadget cannot count restarted rounds. Tier 1 needs a round-1 vs restarted-round asymmetry (round 1
  counter 12b+7 vs restart 4R+3) or class-varying restarts (M13a). The J0=0LK K0-seed sweep (n1/run_k0.sh, genum5 ns=3;
  0LA/0LC unfinished, no halts) was handed to inv-w2-tier1.
- **Route 2 CLOSED NEGATIVE 2026-10-09 23:26 (inv-w2-n1right, w2_search/n1right/REPORT.md):** the right end is where the
  tape grows; each stage ends exactly at its rightmost cell (word end +2R+c, c = 4/6 period, 10 eater, 14 restart), jumps
  overrun anything right (bits at gap 10^4 read by A1/G1); first reader is always H1/G1 (core) = no hook. With G6's
  left-end result, n1 has no side for d; only the far region (destroyed by L12's eater). Side lever (exact): (10)^j at an
  odd gap right of the no-far restart word -> counter 4R+3+2j, depth kept; j = 7 keeps class 9 mod 14, shifts k2 mod 3.
  Passed to inv-w2-tier1. g++ lives at C:/msys64/ucrt64/bin/g++ (not on Git Bash PATH).
- **tier1 interim 2026-10-09 (inv-w2-tier1):** jump outputs are always r = 19 mod 2520, so the left-event R cannot be
  steered. Restart counter c2 = 4R+3+delta(P), where P is the digit prefix the eater leaves (delta in {0,1,2,3,5,7,8,16}
  for prefixes <= 3 digits). c2 mod 14 picks the round end: 9 = standard J0; 5/8/11 = J0 on another tail; 1/4/6 = J0
  with no far region; 10 = irregular k. **PITFALL:** the real k1 is huge (k1 = 17 mod 8640), so an eater that works only
  at k = 17 is a false positive. Example: T13 ..._0LM0LC_0LK0LL_0LK1RA_0LK--- "halts after 2 rounds" at b0 = 6, but it
  halts in round 1 for k = 29/41/77/137. Std-policy k-tests are faithful only for k up to ~45. Re-test every eater hit at
  k in {29, 41} (std) or {77, 137} (big policy). L12 passes (k = 17, 49, 77, 137).
- **n1right CLOSED NEGATIVE (bb8-00's inv-w2-n1right, w2_search/n1right/REPORT.md):** the right end is n1's growth
  frontier: every stage moves the word end +2R+c, every jump +2R' (f_omega-sized); patterns at gaps 1-8 are all read
  (merged/junk), first divergence H1/G1 (core engine). n1 has NO side where an outer counter d can sit.
- **SCREENING CAVEAT (inv-w2-tier1):** the real round-1 far-run length k1 = 17 mod 8640 is huge; std-policy k-tests are
  faithful only up to k ~ 45. Before counting any eater/genum5 hit, re-test at k in {29, 41} (std) or {77, 137} (big).
  Example: T13 ..._0LM0LC_0LK0LL_0LK1RA_0LK--- halts after 2 rounds at b0=6 but its eater halts in round 1 at
  k = 29/41/77/137 (false hit). L12 passes (k = 17, 49, 77, 137).
- n1 follow-up (23:33): L12 reload SCALING CONFIRMED (big r=2539: counter 10159 = 4R+3, depth 13613; shrink same):
  genuine accumulator-reloaded rounds. M13a at 14 states (cs14.py, 52 clone-splits x 300 stages): negative; open
  only: 7 never-read variants need 1000+ stages (rounds too short for detector). Exact tree coverage in n1/NOTES.md.
- **In-place reload route (user approved 2026-10-09 late): Opus inv-w2-inplace, w2_search/inplace/** (<= 2 Idle procs,
  alongside bb8-00's tier1). Idea: n1's engine only grows RIGHT within a round (far tail stable); only the reload
  (leftward ~6R unpack) breaks the left side. Screen for restarts that never write left of the far tail + big counter +
  spare slot, then marker-survival over >= 2 restarts, then use the spare slot as outer counter d. Seed: M13a
  (depth-sized counter, '78 6' prefix survived round-3 restart). Fallbacks: BB17 layout on n1's A-H engine (~14-16 st).
- 2026-10-09 late: w2 lead session launched inv-w2-inplace (w2_search/inplace/): n1 + J0 gadgets whose restart rebuilds
  the counter IN PLACE (M13a-style, surviving '78 6' prefix) so a left marker/outer counter survives restarts.
- **tier1 interim (SCREENING ONLY): k-robust delta-steering eater D1** = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_
  1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK1LM_1RJ1RM (13 states, all 7 new slots read; restart c2 = 4R+4 = class 10 for
  k = 2 mod 3, robust at k = 17/29/41 std and 17/77/137 big). **H14** = D1 with K0 = 0LN, N = 1RD--- (14 states):
  b0 = 6, round 1, clean restart c2 = 80, full round 2, then HALT N1 at stage 141; holds on crafted round-2 starts.
  The big-policy round-2 end has not been checked (over 2e9 steps). A 14-state f_(omega+1)^2 halter would beat the BB(14)
  champion (f_(omega+1)).

**Route 3 / tier1 (inv-tier1, 2026-10-09 evening, w2_search/tier1/REPORT.md):**
- Residue rule: every huge jump output r = 19 mod 2520 (base fixed point), so the restart counter is c2 = 4R+3+delta,
  delta set by the eater's leftover digit prefix / stray far-left bits (one '1' at gap 2 -> delta 2). R2 itself can't
  be steered. Round end type depends on c2 mod 14 (9 std J0; 5/8/11 other tail; 1/4/6 no far; 10 irregular; 12 = round 1).
- SCREENING PITFALL: std-policy eater tests are faithful only for k up to ~45 (R-rep 19); real k1 = 17 mod 8640 is huge.
  Always re-check eaters at k = 29, 41 (std) or 77, 137 (big). Two false Tier-1 hits (T13, m66 clone) were k=17 accidents.
- D1 = L12 with L1=1LM, M=1RJ1RM (13 st, all slots used): first k-robust delta-1 eater (c2 = 4R+4).
- H14 = D1 + clone N (K0 -> 0LN, N = 1RD---): 14-state Tier-1 SCREENING candidate (b0=6: 2 full rounds, halt N1 after a
  messy post-round phase); no 12-13 state hit in ~250k scan leaves (partial coverage).
- **Route 3 FINISHED 2026-10-10 02:05 (inv-w2-tier1, w2_search/tier1/REPORT.md): no 12-13 state Tier-1 halter.**
  R2 can't be steered (every huge jump output = 19 mod 2520, base property); c2 = 4R+3+delta, delta from the eater's
  left remnant (seen 0-8, 16; never 14/28), so the n1-notes "R = 5/12 mod 21" route is closed; c2 mod 14 table in report.
  ~372k leaves, 0 halts after a restarted round (e2_a ~40% of J0=0LK 12-state, e2_b part of J0=1LK, b3/d1c complete,
  d1c2 partial; M1-free subtree of D1 open). Best = H14 = ..._0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD--- (14 states,
  K0 = 0LN): 2 full rounds then HALT N1 at stage 141 (b0 = 6), screening only; weak point = messy post-round-2 phase
  (big policy infeasible); needs independent verification (round-1 eater at k = 2897 with bigk >= 3, then event rules).
- tier1 leads (2026-10-09 late, tier1/NOTES.md): D1 = ..._0LK0LC_0LC1LL_0LK1LM_1RJ1RM (13 st), k-robust delta-1 eater
  (c2 = 4R+4); post-round in-place restarts behind a SURVIVING growing prefix, but short (collapse in ~6 stages).
  **H14 = D1's 14-state clone (..._0LN1LL_..._1RD---) halts after 2 full rounds in screening** = Tier 1 at 14 states
  (f_(omega+1)^2; CORRECTION: BB15 is already f_(w+1)^2) -- needs k re-tests + verification. Forwarded D1 to inplace.
- 2026-10-10 (user: "explore 1 and 2 but defer 3"): launched Opus inv-h14-verify (w2_search/h14verify/: independent
  adversarial check of H14, own simulator, eater at real k1, residue-tracked round-2 end) and inv-w2-d13
  (w2_search/d13/: 13-state D1-mechanism search: M1-free subtree, shared-state hook, leaner 3-state eater, other deltas),
  1 Idle process each. Route 1 (compress BB17's w+1/w+2 layers on its one-sided engine) DEFERRED by the user.
- tier1 DONE (w2_search/tier1/REPORT.md): no 12-13 state halter; best = H14 (14 st, halts after 2 rounds, screening).
  bb8-00 follow-ups (user-approved, 1 Idle proc each): inv-h14-verify (w2_search/h14verify/, adversarial check of H14 at
  real k1 + post-round-2) and inv-w2-d13 (w2_search/d13/, 13-state D1 delta-1 variants: M1-free subtree, freed L/M slot,
  leaner eaters). Split with inv-w2-inplace: d13 = D1 subtrees; inplace = in-place/marker-survival criterion only.
  BB17-layer compression route deferred.
- tier1 follow-up 2026-10-10 03:27: H14's halt is NOT residue-decided. After round 2 a chain of mini-rounds maps depth
  z -> ~(3z-r)/5 (r by z mod 5) until small, then halts (N reads 1) or junk (z = 3, 30 seen). 233/233 large depths and
  3/3 realistic size-order cases (realistic.sh) halt. Provable only if junk endpoints have bounded/avoidable preimages;
  otherwise it is a Collatz-like gamble. Round 1 is safe for k = 14..44 std and 17..1001 big. tier1 still runs
  k0sweep.sh (ns = 3, J0 = 0LK, its own k-robust scanner; new 7-slot delta-1 eaters, no halts).
- **!!! TIER-1 SCREENING HITS (inv-w2-inplace, 2026-10-09 late):**
  T12a (12 st) = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF--- : in-place
  restart at round-1 end, c2 = (4R-19)/3 (big: 3379), full round 2, HALT L1 at round-2 end; std k 17/29/41, n
  41/329/371/2849, real start std (restart st 51, halt st 63), big k=17. One undefined slot spare (K1 or L1 = halt).
  H13c (13 st) = ..._0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ--- : c2 = (4R-10)/3, HALT M1; passes std+big k 17/77/137, real start.
  DEPTH CAVEAT: real round-1 end depth = 35 mod 42 (std real start 329); n=41 is the wrong class; re-test n in
  {329,371,2849}. Independent verifier inv-t12a-verify (w2_search/t12a_verify/, 1 proc) launched; inplace -> 1 proc.
- **inv-w2-inplace Tier-1 SCREENING HITS (w2 lead, 2026-10-10):** T12a (12 states) = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_
  0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF--- and H13c (13) = ..._0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ---, both with an
  in-place accumulator-sized round-2 reload; inv-t12a-verify (lead session) is verifying them. **PITFALL #2:** the real
  round-1 end depth n = 35 mod 42 (std real start gives 329); n = 41 (genum5 ns = 3 and other screens) is the WRONG
  class. Depth-eating gadgets are fragile (H13b passed at n = 329, failed at n = 77..2849). Re-test hits at
  n in {329, 371, 2849} plus k = 29/41 std and 77/137 big.
- tier1 depth re-test 2026-10-10 03:34: all 9 delta-1 restarters (D1, its variants, K0 = 1RI families, H14's eater) give
  counter 80 at n = 329/371/2849 x k = 17/29 (tier1/depthcheck.txt), so they don't eat depth. H14 evidence already used
  n = 329 and swept all residues mod 28. k0sweep restarted at n = 329 (old n = 41 tree in tier1/old/n41/). CAVEAT: the
  earlier negative scans (e2_a/b, hm, b3, d1c, d1c2) all ran at n = 41 and could have missed depth-sensitive halters.
- **H14 VERIFY 2026-10-10 03:50 (inv-h14-verify, h14verify/REPORT.md): the screening halt is an ARTEFACT; halting is OPEN.**
  Rounds 1-2 hold (round 1 = n1, Coq; eater affine in k1, two J0 passes eat 7 then 5 D2s; restart counter 4R+4 = class
  10; round 2 by the Coq PERIODS lemma). After round 2: in reality D' = (9D + 10U + C_r)/15 with a FRESH huge U each
  iteration (C_r = -415/-319/-388/-412 for D = 0..3 mod 5; class 4 takes another path), so D GROWS. The follower's
  fixed U = 19 made it shrink and halt. Real D mod 5 sequence 0,0,2,2,3,2,3,4: no halt through 8 iterations. Class 4
  needs residues mod 8 and 7; the verifier was told to continue. **PITFALL #3:** post-round halts must be re-derived with
  symbolic huge accumulators and exact tower residues (k1 << depth << acc); vary U, not only n and k. Tools: h14verify/
  stage.cpp, numth.py, ures.py, rtest.py. Warned the lead session (T12a/H13c) and d13.
- **FIXED-U ARTEFACT (inv-h14-verify, h14verify/REPORT.md):** H14's post-round-2 halt was an artefact of the follower's
  fixed accumulator stand-in (U = 19). True order k1 << depth << accumulator: chain D' = (9D+10U+C_r)/15 GROWS, halt
  never fires (open). std/big policies vary n, k but NOT U. Any post-round-2 halt must be re-derived with symbolic huge
  accumulators + exact tower residues (h14verify/stage.cpp, numth.py, ures.py, drive.py, rtest.py). Forwarded to
  inv-t12a-verify and inv-w2-inplace for T12a/H13c.
- **inplace DONE 2026-10-10 04:00 (w2_search/inplace/REPORT.md):** T12a / H13c halt DIRECTLY at round-2 end (J0 on a
  different tail, class 5 / 8 mod 14), no post-round chain; real start std+big pass; c2 fit at R = 2539/5059/7579.
  Gaps: big trimmed c2 to class mod 42 (full-size round 2 never replayed; round-2-end D2 run k2 is huge in reality);
  LEAD CHECK: n1-notes real residue 49612750485498 = 18 mod 2520 (not 19) -> (4R-19)/3 non-integral: likely an r vs
  r+1 convention, verifier must settle. M13a's round-2 restart is NOT in place (writes 230/20394 cells left).
  P11 (11 st, ..._1RK0LC_1RC---): 2R-3 restart, prefix digit borrowed at class-7 round end = only automatic d seen;
  Tier 2 needs a borrow-class cycle (none found). Markers left of far tail survive but are never read (d reach >= 14 st).
  Searches: 12-st J0=1RK 37,070 leaves (partial), J0=0RK 22,881 (partial), 11-st J0=1RK 309 (complete).
- inplace final (04:25): T12a real-start BIG passes (restart st 51 c=3379 depth 40674, HALT L1 st 63, ~1e11 steps);
  order.py size-order test (U ~ 100,840 > depth) unchanged halts. H13c halts directly at exhaustion (st 13 -> 16);
  T12a after one absorption pass folding the depth list into the far region (st 22 -> 26): verifier must check that
  fold with accumulator-sized k2. D1 restart 1 is NOT in place (~8R left unpack). Coverage for d13: J0=1RK done
  through K0=1LL; J0=0RK through part of K0=0RL; J0=0LK/1LK not run.
- **VERIFIED (screening) 2026-10-10 05:13 (inv-t12a-verify, w2_search/t12a_verify/REPORT.md):** T12a CONFIRMED (no
  residue condition at the round-2 end); H13c CONFIRMED with r = 1 mod 9 needed at round-2 end (real r = 19 mod 27 ok).
  Own literal sim lsim.cpp 0 mismatches; new states read only in literal stages; c2 = (4 r7 - 19)/3 exact; sweeps:
  n 1..700, k >= 7, P 0..200, z <= 20002, all-big run (241 periods) halt. Real residue: follower r = (3T-10)/2 =
  49612750485499 mod Q/2 = 19 mod 2520 (selector R = r-1 convention explains the 18). sigma >~
  f_(omega+1)(f_omega(f_(omega+1)(JJ))). Gaps: jumps trusted; huge params by sweeps not induction.
- Coq: Opus inv-t12a-coq launched (investigations/bb12_t12a_coq/, proofs/BB12_T12a.v + _bound.v, report
  investigations/bb12_t12a_coq.md), plan = t12a_verify REPORT "Recommended next step". Verify any PASS with check.py.
- **CORRECTION (lead, 2026-10-10):** the verifier's CONFIRMED verdict used fixed-U follower runs only. The TRUE-ORDER
  test (h14verify absim/drive, exact tower residues, k1 << w << f << fresh U, from Coq HALT_B config) was started
  after the report: t12a_verify/tdrive.py, log tdrive_t12a.log (H13c next). T12a is NOT confirmed until it finishes.
  Coq agent told to do round 1 + restart first, round-2-end halt events last.
- **d13 DONE 2026-10-10 05:30 (inv-w2-d13, d13/REPORT.md): C13a 13-state Tier-1 SCREENING candidate** =
  1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0RL1RM_0RI0RK_1RD--- (J0 = 1LK eater; M = C-clone,
  M1 = halt). Round 2 starts 2^(k-4) 1 5 (R-2) 2 5 1^(2R+5) 0^3 9 1^z (c2 = 2R+5, class 1 mod 14) and halts just after
  round 2's left event. Robust in std across k, n, c, z and p up to 5057; the big-policy round-2 end is infeasible.
  OPEN RISK: in reality the prefix digit R-2 is much smaller than round 2's accumulators (size-order artefact risk).
  Siblings C13b (..._1LM0LC_0RL0LB_0RI0RK_0RL---). D1's core cannot host a 13-state hook (its fill loop uses all 1-slots).
  The n = 41 trees can miss real-class eaters (re-screen at n = 77). Unscanned: rest of the j1 tree (J0 = 1LK), J0 = 0RK,
  non-in-place J0 = 1RK. inv-h14-verify was redirected to C13a (H14 class-4 step paused).
- bb8-00's inv-w2-d13 DONE (w2_search/d13/REPORT.md): C13a = ..._0LJ0LI_1LK0LC_0RL1RM_0RI0RK_1RD--- (13 st, Tier-1
  screening): J0 = 1LK eater keeps R as a prefix digit, restart counter 2R+5 (class 1), HALT M1 right after round 2's
  left event. inv-h14-verify redirected to verify it (exact residues, varied U).
- Lead CLAIMED (deferred until T12a true-order result / a free CPU slot): unscanned 12-st trees J0 = 0RK (beyond
  inplace's partial coverage in K0 = 0RL) and non-in-place J0 = 1RK, at depth n = 35 mod 42, k >= 29. Tell bb8-00 on start.
- 2026-10-10 ~05:45: the w2 lead session CLAIMS the unscanned 12-state trees (J0 = 0RK beyond inplace's K0 = 0RL, and
  non-in-place J0 = 1RK, at n = 35 mod 42, k >= 29). It holds them until CPU frees (T12a true-order test + t12a-coq
  running). Don't launch them from bb8-00. The tier1 k0sweep was told to pause (resumable via .done markers).
- tier1 FINAL 2026-10-10 05:33: k0sweep stopped. K0 = 1RI at n = 329 reached 152,752 leaves (partial, no seed finished;
  a resume restarts the seed). 0 halts after a restarted round; 13 delta-1 restarts (all 7-slot), 8 prefix restarts.
  tier1's H14 view ("halts in every realistic case") is SUPERSEDED by inv-h14-verify (fixed-U artefact, halting open).
- **T12a Coq PAUSED (2026-10-10 05:34):** inv-t12a-coq stopped when a safety classifier blocked its output while writing
  spec.py (event-spec -> symbolic-shape helper); it deleted the file and stopped. Resume is the USER's call (don't route
  around the block). Done: proofs/BB122.v + Individual122.v (12-state setup; state L shadows direction L -> tables use
  TM.L/TM.R), check.py extended to states A..P (lead re-ran check.py on BB8_016582_1RB0RC_G0_1RB.v: PASS), base
  lemmas compile (investigations/bb12_t12a_coq/dev/Base.v). Its independent event-level rebuild agrees: c2 = (2A-23)/3,
  round 2 = n1's P1-P4 with left context, round-2 end: depth -> m = n+1 blocks (3 2 0), eaten 2/round, outcome depends
  ONLY on m mod 6 (not on A or X), 3 end classes all HALT L1 (m = 14..19). Plan in bb12_t12a_coq/NOTES.md.
- inv-w2-t12scan launched (w2_search/t12scan/, 1 proc): J0 = 0RK beyond inplace coverage + non-in-place J0 = 1RK.
- 2026-10-10: the w2 lead launched inv-w2-t12scan (w2_search/t12scan/: J0 = 0RK beyond inplace, non-in-place J0 = 1RK).
  The T12a Coq agent stopped partway (output blocked while writing a spec helper; paused pending that session's user).
  It left proofs/BB122.v + Individual122.v (12-state setup), and proofs/check.py now handles 12-16 states (TM.L/TM.R
  direction tables; still PASSes an 8-state proof).
- 2026-10-10: user APPROVED resuming inv-t12a-coq ("I approve the subagents action, let's resume"); resumed same agent,
  told: plain evs/mexp-style helper, if blocked again stop + report (no rewording around it); hold round-2-end halt
  events until true-order result; re-run check.py on BB10_n1.v (10-state regression).
- **C13a WITHDRAWN 2026-10-10 05:38 (d13):** fixed-U artefact like H14. With U = 2539 (d13/bigend.py, 6e10 cap) the far
  region grows to ~300k bits; there is no left event and no halt through stage 29 (stage 35 for C13b). Its J0 = 1LK eater
  (counter 2R+5, k- and n-robust) stays valid. d13 complete scans: s1 194k, s2 18k, e2r 136k, n77 192k, j1 41k
  (partial); 0 halts after a restarted round. Untried 13-state idea: the (10)^j lever eater, with a halt decided at the
  round-2 end itself. Every screen must vary U. inv-h14-verify was sent back to H14's class-4 step.
- C13a WITHDRAWN by bb8-00 (fixed-U artefact like H14: halt list sized by stand-in; U = 2539 -> no halt through st 29);
  its J0 = 1LK eater is real (2R+5, class 1, k/n-robust). d13: 12-st J0 = 0LK tree has six accumulator-sized restarter
  families (2R+3/9/11/17, (8R-5)/3), none hookable with 1 state; untried 13-st idea = (10)^j lever eater.
- T12a TRUE-ORDER progress (22:38 local): absim/drive reproduces the in-place restart symbolically at stage 24:
  round-2 start 2 5 1^((2U7-23)/3) 0^3 9 ... = c2 = (4r-19)/3 with symbolic U. Stage 26 timed out at 2e10 steps;
  verifier continuing from tdrive_t12a_s25.pkl (tdrive_t12a_b.log). Round-2 end still pending.
- Coq agent B-form fresh-accumulator check (2026-10-10): round-2-end eat outcome depends only on m mod 6 (m = final
  depth + 1), not on A, X, P; 768 combos of independently varied fresh CLR outputs (m = 14..19) all HALT L1 -> no
  fixed-U artefact at B-form level. Plan: prove all three m-classes (avoids depth mod 12 tracking). Lead lifted the
  hold on round-2-end events.
- **DEPTH CLASS CORRECTION 2026-10-10 05:56 (inv-h14-verify, exact Coq residues):** the real round-1-end depth is
  29 mod 42 in the follower's convention, NOT 35 mod 42; 329/371/2849 are the WRONG class. T = arrow 37 2 3 ≡ 23 mod 49,
  JJ ≡ 1 mod 7, real k1 ≡ 29 mod 42 (the follower's k1 = 17 is 3 mod 7). b0 = 6 matches B only mod 2520 (B ≡ 34 mod 49).
  Use h14verify numth.py/ures.py (exact residues mod 49, reps matched mod 840/1050). Relayed to the w2 lead (T12a, t12scan).
- H14 chain: the exact map is D' = 3/5 D + 2/3 U4 + c_r, with U4 a fresh tower (~2^^65534+) built by CLR from
  exact small structure. So D never gets small; the z = 3/30 junk and the stage-141 halt are representative effects.
  The real D mod 5 classes are 0,0,2,2,3,2,3,4; class 4 (iteration 8) is unresolved and needs reps fixing mod 8.
  The eater and restart were re-checked at depths ~3000-4000 in the real class: uniform. The verifier was told to run
  the class-4 path.
- **DEPTH-CLASS CORRECTION (inv-h14-verify addendum):** real T = 23 mod 49 -> JJ = 1 mod 7, real k1 = 4JJ-3 = 29 mod 42,
  real round-1-end depth = 29 mod 42 (follower convention); 35 mod 42 / n = 329/371/2849 / k1 = 17 are follower-class
  artefacts (b0 = 6 matches B only mod 2520; B = 34 mod 49). Use n = 323/365/2843, k1 = 29/71. Lead check: real r = 5
  mod 7 = 19 mod 7, so T12a c2 class 5 mod 14 unchanged; verifier's n 1..700 / k >= 7 sweeps cover it. Forwarded to
  t12a-verify (explicit re-run), t12scan (switch starts), coq (FYI). Q = 54305848396800 is NOT divisible by 49.
- Incident 2026-10-10: inv-t12a-verify killed ALL stage.exe by image name, incl. bb8-00's (PID 1095748, likely
  inv-h14-verify); bb8-00 told (resume via drive.py RESUME=file:stage from PKL). Rule for all agents: kill only own
  recorded PIDs, never by image name.
- Lead verified: 2-tower T (height >= 4) = 23 mod 49 -> JJ = 8 mod 21 (= 1 mod 7): depth correction CONFIRMED. 
  extra value 12616 was mod 17640 (mislabelled 88200), consistent: T = 65536 mod 88200, 11 mod 25, 23 mod 49 (resolved),
  h14verify never used it; it will assert T = 11 mod 25, 23 mod 49.
- **Coq progress (inv-t12a-coq):** round 1 + in-place restart + all round-2 periods MACHINE-CHECKED (no axioms):
  investigations/bb12_t12a_coq/dev/R.v `reach_round2_end : exists p k J n a w, c0 -->* Per (lfr [p;3] (FarR k)) (4J+1) 3
  n a /\ Inv n a /\ 6 <= k /\ iter (2JJ+1) F 34 <= w /\ F w <= 7J+9 /\ iter (2J) F w <= n` (FarR k = 0 0 D8 D1 D2^k);
  c2 = 14J+3 (5 mod 14) proved via arrow_mod7; specs evs12.py, dev/M.v 981 lemmas (345 s). check.py PASS on
  BB10_n1.v (10-state regression OK). Remaining: round-2-end events + halt + bound file (hold lifted).
- LEAD RE-VERIFIED 2026-10-10: probe (job tmp/probeR) `Print Assumptions reach_round2_end` = Closed under the global
  context; M.tm table == T12a string exactly. Busycoq path for probes: -Q Downloads/bb8/third_party/busycoq/verify BusyCoq.
- **T12a Coq STOPPED again (2026-10-10 ~06:42):** inv-t12a-coq blocked by the safety classifier 2 more times (3 total),
  both on round-2-end work (after the hold lift / go-ahead). It stopped, noted in NOTES.md, suggests a fresh agent or
  session from bb12_t12a_coq/NOTES.md. Lead did NOT hand off (that would route around the block); asked the user.
  Remaining: round-2-end specs (E20, depth->blocks, 6-case eat by m mod 6, 3 continuations, HALT L1), assemble
  proofs/BB12_T12a.v + check.py, bound file, report.
- **H14 HALTS: STRONG EVIDENCE (inv-h14-verify, 2026-10-10 07:03; h14verify/REPORT.md top).** The verifier's earlier
  "D grows" was a RANK BUG: the in-iteration CLR outputs (small exact inputs d=2, n=2, A=4, then depths 2/4) are FIXED
  constants U*, far below the round-2-sized D. Fixed via re-atomization in absim.py. Chain D' = (9D + 10U* + C_r)/15
  shrinks. Real D_1..D_8 mod 5 = 0,0,2,2,3,2,3,4. Iteration 8 (class 4): 12 stages, then N reads 1 (~5.9e6 steps +
  affine), D_8 still astronomically large. sigma ~ f_omega(D_8), D_8 ~ (2/5)(3/5)^7 a15, a15 >= f_(w+1)^2(~2^^363), so
  the f_(w+1)^2 class = BB(14) RECORD CANDIDATE. Not proved: non-Coq stages are affine fits on 6-9 reps; prefix
  independence was checked only at iteration 8. Coq route: n1's CLR/PERIODS + ~8 eater + ~12 round-end + 4x~14 class +
  13 class-4 lemmas + tower-residue lemmas mod 5^9.
- **PITFALL #4 (ranking):** the big policy (every accumulator = 2539) and the old absim rank rule both put in-iteration
  constants ABOVE the depth, the wrong order. So C13a's withdrawal (d13 bigend.py) is suspect: C13a is OPEN again, and
  inv-h14-verify is checking it with exact residues. Warned the lead session: the T12a true-order test reused the old
  absim.
- **REVERSAL 2026-10-10 (bb8-00, h14verify/REPORT.md):** absim/drive rank-rule BUG: it ranked every new CLR output above
  everything, but CLR outputs from small exact inputs inside an iteration are fixed constants U* << depth. Fixed via
  re-atomization in absim.py -> **H14 HALTS (strong evidence)**: chain D' = (9D+10U*+C_r)/15 shrinks; at iteration 8
  (D = 4 mod 5) N reads 1 while D is still huge; sigma ~ f_(omega+1)^2 = BB(14) record candidate. Big-policy (U = 2539)
  checks share the flaw -> C13a's withdrawal is VOID, open again (h14verify checking with exact residues).
  LESSON: "fixed-U artefact" can cut both ways: in-iteration accumulators from small exact inputs are SMALL constants.
  Asked inv-t12a-verify to re-run T12a true-order with current absim.py (bug can only give false no-halts).
- **T12a TRUE-ORDER PASSED (inv-t12a-verify, 2026-10-10 ~10:00, t12a_verify/REPORT.md "True-order symbolic
  re-derivation"):** absim/drive from Coq HALT_B, exact residues, ~10 rank-ordered rep sets: restart (4 r7 - 19)/3,
  J = (U7-40)/21 periods, end = uniform depth->(2 0 3)^X loop, CLR d=3 n=3 -> constant U24, regroup by 6 (all classes
  halt), U24 mod 9, CLR d=2 n=3, HALT L1 identical in all 10 sets. H13c: all 6 depth classes HALT M1 (own lsim, true
  order). Residue-decided, no backward tree needed. Asked to confirm current (rank-fixed) absim was used.
- **!!! C13a HALTS: STRONG EVIDENCE (inv-h14-verify, 2026-10-10 09:59; h14verify/REPORT.md C13a section).** 13-state
  f_(w+1)^2 Tier-1 candidate; d13's withdrawal was the big-policy rank artefact. Exact residues, corrected ranking, real
  classes (k1 ≡ 29 mod 42). Round 1 = n1 (Coq). Eater (5 stages) -> round 2 = 2^(k1-4) 1 5 (X4-3) 2 5 1^(f+3) 0^3 9
  1^(w+5) | 4. The prefix digit X4-3 = U3 - f/2 - 3 is LARGER than round 2's counter (not "R-2") and never read. Round 2 via
  PERIODS ends in class 1, remainder 13. Round-2 end: a long (2 0 3)-block loop (jumped symbolically), then HALT M1 at
  stage 67. The list 1^(2/3 U14 + 22/3), U14 = iter 3 (U 3) 4 (a constant), is << the far region (same order as std).
  The halt is uniform over 11-12 rep sets and both size orders. Gap: stage 61 was only checked with compact spacing
  (wide spacing 14M cells, >1e11 steps). sigma >= ~f_omega(a), a >= f_(w+1)(f/7). Not proved: affine fits, prefix
  PERIODS extension, loop-jump extrapolation. Logs c13a_*.log, c13a_traj_final.pkl.
- **C13a HALTS (strong evidence; inv-h14-verify exact residues, corrected ranking, real k1 = 29 mod 42;
  h14verify/REPORT.md C13a section):** round 2 prefix digit X4-3 = U3 - f/2 - 3 (> counter, never read); end loop of
  (2 0 3) blocks jumped symbolically; HALT M1 at stage 67; the list beside the far region comes from constant U14 =
  iter 3 (U 3) 4 << far region (d13's big-policy no-halt was the rank artefact). sigma ~ f_(omega+1)^2. Unproved bits:
  affine fits, prefix-PERIODS, loop-jump extrapolation, stage 61 (compact spacing only).
- Candidates now: T12a (12 st, Coq through round 2, true-order pass), H13c (13 st), C13a (13 st), H14 (14 st).
- **T12a re-run with CURRENT (rank-fixed) absim (t12a_verify REPORT "Addendum 2", tdrive_t12a_h.log, snap2/,
  stage_t12v.exe): HALT L1 at stage 76, all 10 rep sets**; only small-input CLRs are stages 71/75 (constants U24/U25);
  real-class follower k1 {29,71,113,1457} x n {29,71,113,2129}: T12a 16/16, H13c 16/16. Leftover absim gap: deep
  d=3 CLR U8 < U7 but ranked above (no effect on T12a restart). inv-t12a-verify done, nothing running.
- T12a (lead session) re-run with the CURRENT absim: still HALTs at L1, stage 76, in 10/10 rep sets (t12a_verify/REPORT.md
  Addendum 2). The small-input CLRs at the round-2 end (U24, U25) sit in the constant tier, and the end is decided by
  X23 mod 6 and U24 mod 9. Real-class follower: T12a and H13c each 16/16 halts. T12a Coq is machine-checked through
  round 2 (reach_round2_end); the round-2-end Coq is paused (lead session's user to decide). Residual rank gap: absim
  ranks a deep d=3 CLR above an earlier, really larger one. inv-h14-verify was asked to audit H14/C13a for it.
- **RANK AUDIT 2026-10-10 10:50 (inv-h14-verify, REPORT.md "Rank audit"): H14 UNAFFECTED (still strong evidence);
  C13a halt RETRACTED, OPEN.** C13a eater stage 5 had ranked U3 = iter 2 (U (w+7)) 4 above f (round-1 acc). In truth
  f >> U3, so the eater does NOT eat the far D2 run (a gap of 2f-4U3 opens), and the real round 2 starts
  2 5 1^(2U3-1) 0^3 9 1^(w+5) | 4 (class 9). The stage-67 M1 halt does not happen. The true-order checkpoint is
  c13a_min_geo.pkl; the ures.py mode ranks each CLR output just above its inputs. The verifier was asked to follow the
  real continuation. LESSON: rank every CLR output relative to its own inputs, never by a global "newest is largest" rule.
- **C13a halt RETRACTED again (bb8-00 rank audit, h14verify/REPORT.md "Rank audit"):** eater-stage U3 = iter 2
  (U (w+7)) 4 (CLR at depth-derived n) was ranked above round-1 accumulator f, but f >> U3: eater doesn't eat far D2
  run, round 2 starts in class 9 not 1, no stage-67 halt; C13a OPEN (h14verify following). H14 unaffected (strong).
  ures.py has an inputs-based ranking mode (CLR output just above its own inputs). Asked inv-t12a-verify for a final
  pass on T12a's post-round-2 stages (restart + round 2 are Coq-exact, so ranking can't affect them).
- **Rank-audit pass DONE (t12a_verify REPORT Addendum 3, snap3/, endrun.py, RANKMODE=min + magnitude overrides):**
  T12a end game unchanged -> HALT L1 (true order k1 << k2 << P << N << U22; only constants U24/U25 in the end game;
  X14/n16/X20 CLRs consumed inside Coq-proved round 2). H13c: earlier ordering had been WRONG (U14 < U16/U17), re-run
  in true order: end stages identical, final stage literal under 6 true-order sets -> all HALT M1 (1.6-2.1e10 steps).

## C13a final (2026-10-10, true-order run): does NOT halt (strong evidence)
In true order (f >> U3) the eater leaves the far D2 region as inert debris (gap 2f-4U3-18). Round 2 starts with counter 2U3-1 (class 9 mod 14) and runs as a full PERIODS round to the standard class-9 end. Each eater pass repeats rewrite for rewrite, adding one debris block; U is always 40 mod 2520, so the class never changes. Followed to the start of round 4 with no read of M1. Not a candidate. Logs: h14verify/c13a_true.log, c13a_true2.log; checkpoint c13a_true_r4.pkl. Gap: sampled affine stages plus induction over 3 literal repetitions.
- **C13a FINAL: does NOT halt (strong evidence, bb8-00, h14verify/REPORT.md C13a, c13a_true*.log, c13a_true_r4.pkl):**
  true order f >> U3: eater leaves far D2 as inert debris; round 2 counter 2U3-1 (class 9), standard class-9 end,
  each pass repeats + adds a debris block, U stays 40 mod 2520; followed to round 4, M1 never read = clean-restart
  looper (like L12). H14 unchanged (halts N1, chain iteration 8).
- Lead applied bb8-00's mixed-sign safeguard to t12a_verify/endrun_t12a.log: every end-game exponent is a single atom
  + constant (k1-7, U12+2, (4U7-139)/21, U22-7, N-6, N/6-4/3, U5/9-40/9 with U5 a huge constant): nothing to flip;
  HALT L1 in all 10 sets.
- 2026-10-10: user "Let's finish the T12a proof" -> fresh Opus inv-t12a-coq2 launched from bb12_t12a_coq/NOTES.md
  (round-2-end specs, 3 m-classes, proofs/BB12_T12a.v + check.py, then bound + report). Rule: if the classifier
  blocks, stop + report (no rewording). Verify any PASS with check.py myself.
- **2026-10-10 (user: "move forward with routes 1 and 2"; new numbering from the strategy review): two Opus agents, 1 Idle
  proc each.** inv-w2-farcount (w2_search/farcount/): the FAR RUN as the outer counter d (bounded eater per round, class-
  invariant in-place restart, halt when the eater meets the far tail; rounds ~ k1/delta). Seeds D1/H14 eater, L12, T12a
  spare slot. inv-w2-borrow (w2_search/borrow/): P11's prefix-digit borrow made class-invariant (post-borrow reload
  aR'+b with 19a+b = 7 mod 14, or a class cycle avoiding junk). Both screen by SCALING (rounds vs k / vs prefix d), not
  a fixed round count; 13-16 states allowed (CORRECTION 2026-10-11: BB15 is f_(w+1)^2, BB16 f_(w+1)^3). Old "route 1" (BB17 layer
  compression) still deferred. Reports: REPORT.md in each dir.
- **T12a PROVED in the dev build (inv-t12a-coq2, 2026-10-10):** dev/E.v `halt : halts tm c0`, dev/B.v `beats_n1`
  (ones N > BB10_n1_exact.score_value + 1) and `sigma_lower_bound` (F^(2J)(w) <= 6N+11, F w <= 7J+9,
  w >= F^(2JJ+1)(34)): LEAD-PROBED all three Closed under the global context (job tmp/probeR/probeE.v). End-game
  specs evs_end.py (E20, CONV/CONVS induction, Z0/Z1, EAT0..5, SM3, F23, F24, G1-3, HALT1/2; A24 = 40+9y proved);
  mexp loop-matcher max gap raised 64 -> 200 for the 78-cell junk unit. Single file proofs/BB12_T12a.v (2.6 MB)
  compiling at Idle (~3 h), then check.py -> lead must re-run check.py on it.
- CPU incident 2026-10-10 ~13:30: T12a single-file coqc (PID 317212, Idle) starved by 20 Normal-priority workers
  (18 zf/reduce ils/anneal/vmscan from the "BB(9) search" session; enum12/benum from bb8-00's farcount/borrow agents).
  Owners set them Idle (zf pinned to cores 0-3, <= 4 workers). Durable fix: scripts call SetPriorityClass(IDLE) on
  themselves at startup so children inherit. Ask owners first; don't change other sessions' processes yourself.
- **farcount DONE 2026-10-10 ~20:50 (w2_search/farcount/REPORT.md): route "far run as d" = STRUCTURAL NEGATIVE at 12
  states (screening).** Every restarter eats a constant delta of far D2s ONCE (T12a 7, H13c/F12 12, Q12a 6, P11 14) or
  the whole run (L12/D1/H14); 2373 restarters x 6 rounds: far count drops at most once. Each round builds its own D2
  run right of the old far; only CLASS-12 round ends walk back to the old far tail (idx 22), but every class-12-reaching
  restarter leaves a blocking prefix (digit >= 3 gets borrowed instead). Per-round far counter needs a transparent
  class-12 in-place restart + a delete-one-D2-and-restore-tail gadget (~15+ states est.; 13-14 not searched). Class-12
  gadget enum: J0 -> base complete, 0LK ~17k / 1LK ~22.5k partial, 0RK/1RK not run (CPU-starved). Looper
  ..._0LJ0LI_1LK0LC_0LL0RA_1LL0LI re-supplies its borrowed digit 7 each round (never halts). No processes left.
- **!!! T12a PROVED (2026-10-10 ~23:25): proofs/BB12_T12a.v check.py PASS, no axioms -- LEAD RE-RAN check.py: PASS.**
  Bound proofs/BB12_T12a_bound.v (compiled 967 s): sigma_lower_bound (iter (2JJ+1) F 34 <= w, F w <= 7J+9,
  iter (2J) F w <= 6N+11), score_ge_exact (F (F Wf) <= 6N+11, Wf = n1's exact round-1 depth), beats_n1
  (N > BB10_n1_exact.score_value + 1). Report investigations/bb12_t12a_coq.md. Single file took 5 h at Idle; check.py
  rebuilds at Normal if .vo deleted. sigma ~ f_(w+1)(f_w(f_(w+1)(X))): beats wiki BB(14)/BB(15) champions by FGH
  reasoning (not formalized), below BB(16) (f_(w+1)^3) and BB(17)/(18) (f_(w+2)).
- **borrow interim 2026-10-10 evening (w2_search/borrow/NOTES.md): route "prefix-digit borrow" NEGATIVE at 12-13 states
  (screening).** P11's class-7 borrow is a COUNTER-TRIM ARTEFACT: inplace's big run kept c mod 42 (k = 9); untrimmed,
  class 7 borrows only at k = 9/17; real k = 9 mod 1440 (e.g. 1449) -> n1 growing-far junk cycle, d untouched (untrimmed
  P11 big run queued to confirm). PITFALL #5: never trim a counter to its class mod 42 when testing round ENDS; the end
  depends on k at true size. At true k the only clean borrow reaching J0 = class 12 with k = 9 mod 12 ('[d-3] 0 1^w | U'
  = n1 halt shape), but the left walk unrolls d-3 into (111110)^((d-4)/3) marks before J0. Exhaustive ns <= 2 gadget
  enums on class-7/12/2 borrow tapes + 300k-node 13-state slice: 0 keep d as nearest digit (d-varied check); copy-loop
  restarts always lay a fresh accumulator digit nearest; class-12 d-dependent gadgets re-roll marks into the COUNTER.
- **borrow FINAL 2026-10-11 (w2_search/borrow/REPORT.md): route NEGATIVE at 12-13 (screening).** P11 is NOT an automatic
  d (trim artefact; erratum appended to inplace/REPORT.md). Untrimmed P11 big run reached stage ~150/2200 (~40 h est.),
  stopped; junk end inferred from crafted ends. Every in-place restart COPIES (fresh U-derived digit nearest the
  round). Coverage: ns<=2 exhaustive on class-7/12/2 tapes (341k/366k/349k), 13-st slices 250-300k, 2734 mined
  leaves: 0 double borrows of one digit. Est. 13-16 states for a class-12 version (re-roll marks into a digit, MOVE
  restart at k = 9 mod 12, left check, halt at d < 3). Next step if pursued: a pure-MOVE restart gadget from the
  class-7/8 pre-J0 tape first. Both n1-based d routes closed -> next = BB17-layer compression (deferred, user's call).
- Lead probe 2026-10-11: BB12_T12a_bound beats_n1 / sigma_lower_bound / score_ge_exact all Closed (job tmp/probeR/probeB2).
- bb8-00 farcount + borrow agents DONE: routes 1/2 NEGATIVE at 12-13 states (w2_search/farcount/, borrow/ reports);
  P11's prefix-digit borrow was a counter-trim ARTEFACT (erratum appended to inplace/REPORT.md) -> no automatic d known.
- **PRIORITY BUG:** `ctypes.windll.kernel32.SetPriorityClass(GetCurrentProcess(), 0x40)` FAILS SILENTLY on 64-bit
  Python (returns 0, stays Normal); ~37 project .py files use it (ilib.py, nfol.py, tdrive*.py, *_coq/common.py).
  Fix: w2_search/borrow/idle.py (GetCurrentProcess.restype = HANDLE, SetPriorityClass.argtypes = [HANDLE, DWORD]);
  import it first. Children launched with creationflags=0x40 are Idle regardless.
- **T12a FULLY PROVED (2026-10-11; lead session's inv-t12a-coq2; report investigations/bb12_t12a_coq.md).** I re-verified:
  check.py PASS on proofs/BB12_T12a.v (no axioms; run at Idle via scratch run_idle.py wrapper), and a scratch compile
  of BB12_T12a_bound.v: sigma_lower_bound, score_ge_exact (F (F Wf) <= 6N+11), beats_n1 all "Closed under the global
  context". T12a = BB(12) champion candidate, f_(omega+1)^2; rows 13-15 should blank, not 16 (BB16 = f_(w+1)^3; see [[wiki-champion-rows-convention]]).
