---
name: bb9-f3-0rc-candidate
description: "!!! 2026-10-19 BB(9) lead f3_0RC = M8 with H0 = 0LI, I = 0RC 1RF (y1-fable F3 screen): bigger 2nd escalation, then M8's cascade; claimed to beat M8 in EVERY class if parametric; checks pending"
metadata:
  type: project
---
f3_0RC = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_0RC1RF (twin f3_1RD: I0 = 1RD). Found by y1-fable's F3 screen (M8 with H0 = 0LI, I1 = 1RF, I0 free; 36 machines; runs in bb9_y1_fable/runs/f3_B6). In world B=6 it halts at H1 at step 6.7e8.
- Mechanism: exh#1 goes via I0 to a top rebuild with R'' ~ 2^^9(1.7B), then a second top rebuild with R2' >> M8's 2B+4. Then EXACTLY M8's cascade and endgame, with L0' = (108 R2'+47)/5. Claimed all-class lower bound f_w(12 R2' - O(1)) > f_w^2(12B+27), still at the f_w^2 level.
- Why the y1-fable "no faithful 9-state beats M8" theorem doesn't apply: it diverges from M8 at H0, before M8's halt.
- f3_1LC = ..._0LI---_1LC1RF: two more alternating rebuilds, possibly f_w^4. Second priority.

**Why:** this would be a BB(9) entry beating M8; currently BB(9) has no entry of its own.
**How to apply:** the lead's checklist was sent 2026-10-19: parametric over B in 11..126 (B = 1 mod 5); no far-left H0 in all 9 route worlds; argue the residue class of R2' for every real R2'; no early halt; add to OPEN_CANDIDATES. Then an independent re-check and Coq reusing the C04/M8 endgame. Related: [[m8-bb8-c04-collapse]], [[bb9-y1-class-dependent]], [[open-candidates-log]].
- 2026-10-19 STRONG EVIDENCE (y1-fable REPORT section 7):
  - Parametric for B = 6..126 in both R classes. Phases P1: [0 1 (6B-2) 13|1*5]; P2: [0,0,7|1*(12R''+11)]; P3: top stop with k' = (108R''-78)/25.
  - Residues: every accumulator has 2R+4 = 2^e, e = 16 mod 20, so R = 16 mod 25, even, 0 mod 3. Then L0' = (324R''-359)/25 is odd and 1 mod 3, so M8's endgame applies and every class halts.
  - 9 route worlds: identical halts to M8, no far-left H0, exactly one H1 event.
  - FGH: inner argument ~6*2^^9(2B) instead of 12B+26, so it still sits in f_w^3(12)..f_w^3(13); it beats M8 exactly.
  - f3_1LC is not parametric (on hold).
  - Launched: f3-check (Opus, bb9_f3check, independent sim) and f3-coq (Opus, bb9_f3_coq, PLAN first, reusing the C04 casc_keyU).
- 2026-10-19 USER: unsure f3 is "publishable" since it is at M8's FGH level, but put it on the repo anyway (as the BB9 entry once the Coq proof passes); keep searching other leads. The lead launched redir9 (Opus, bb9_redir, 2 cores): (A) an 8-state top-rebuild re-entry without a spare state; (B) the f3 relay pattern on other engines.
- 2026-10-19 f3-check (independent wsim.cpp) CONFIRMED all phases on parameter grids; all 9 classes halt with ones identical to M8's counts at the cascade entry.
  - Correction: L1' = (108R''+47)/5 uses R'' (before the FIRST top rebuild), not R2'; the parked list is 12R2'+8; forwarded to f3-coq.
  - Score: sigma > f_w(f_w(12R''+12)) with R'' >= 2B.
  - f3-coq: auxiliary 11-state X = C04 + E0 relay, step = one C04 step so C04's scripts compile unchanged; final statement on a genuine 9-state machine in the Defs/Statement layout.
