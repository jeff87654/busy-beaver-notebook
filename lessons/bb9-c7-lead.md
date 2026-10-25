---
name: bb9-c7-lead
description: "!!! 2026-10-20 BB(9) lead C7 = M8 with H0=0LI, I=1LC0RA (1RB0RA_..._0RG0RF_0LI---_1LC0RA): 11 top-level rebuilds then a class-independent 9-step cascade halt, ~f_w^6(11); strong evidence; c7-check + c7-coq + c7-triage agents launched 2026-10-21"
metadata:
  type: project
---
C7 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA (twins ..._1LI---_0RC{1RA,0RF,1LG}), found 2026-10-20
by agent bb9-redir re-screening halt_redirect/c7/mf_out.tsv TIME rows (c7fam.py had hard-coded t=0) with pkf8 --cnt
(bb9_redir/runs/c7_1undef_w150_cnt.tsv, c7_multi_w150_cnt.tsv). Claim (OPEN_CANDIDATES.txt entry C7-0LI-1LC0RA):
J1..J11 rebuilds, each clearing a depth linear in the previous accumulator (R_1 > f_w(5B), R_2 > f_w(12R_1), ...),
then L_0 has a FIXED 5-adic residue (all accumulators are 2^^M, same residue), the cascade runs exactly 8 sub-steps and
halts at H1 on step 9 -> class-independent, score > 24 R_10 > f_w^5(5B) > f_w^6(11). Beats f3_0RC and M8 by far.

2026-10-21 (lead, this session): nothing was running; the CPU-cap governor was dead and was restarted (pid 10540).
Launched Opus agents: c7-check (bb9_c7check, independent simulator, Coq-ready spec), c7-coq (bb9_c7_coq, reuse the
bb9_f3_coq X-machine template on C04), c7-triage (bb9_c7triage: rank the other ~880 HALT rows + STOP rows, finish
bb9-redir's interrupted 8-state screens s8r_F/cov_F, re-screen MAXSTAGES/WIDE/LOOP rows of mf_out).

**How to apply:** check bb9_c7check/REPORT.txt and bb9_c7_coq/notes.txt before redoing anything; if the Coq proof
passes, C7 replaces f3_0RC as the BB9 entry (f3 PR by agent f3-package, branch bb9-f3). Related:
[[f3-0rc-bb9-candidate]], [[m8-bb8-c04-collapse]], [[open-candidates-log]].

!!! 2026-10-22 C7 COQ-PROVED, LEAD-VERIFIED: bb9_c7_coq/c7/probe.v re-run by the lead (exit 0, 2x "Closed under the
global context", 18 table eq_refl checks). Statement.v: c7_table, c7_halts, c7_lower (N > f_omega^4(6*arrow 13 2 3 + 3)),
c7_beats_m8_bound. Built on f3's X tree (X' = X with K = 1LC/0RA), Res.v tower-residue lemma (all accumulators and B
= 5059528974366 mod 2^5 3^4 5^14), c7/Sim.v. Corrections vs the original entry: L0 = 8136900 mod 5^10; counter loop
2R5+3 rounds; C7's own cascade map (c = -23,-14,-20,-32 for r = 1,3,0,4; r=0 not a stop); r=2 branch L = 15u+17 halts
iff u = 1,2 mod 5, real u = 2 mod 5. Proved bound f_w^4(12B+27) is weaker than the claimed f_w^5 but >> M8, f3.
Rebuild: python tools/sched.py 2 c7/probe.v (uses ../bb9_f3_coq/ext). TODO: repo packaging (BB9/verify_c7 on top of
verify_f3), clean from-scratch build, optional VsM8 file. Backup lead h003 (c7-triage) at a similar level.

2026-10-22 ~06:50 PT: ALL agents stopped on the weekly usage limit (resets 2pm PT). State at the stop:
- f3 clean build DONE (bb9f3_wt/BB9/verify_f3/compile_clean.log 29851 s, probe 5/5 Closed); package UNCOMMITTED in
  worktree C:\Users\jeffr\Downloads\bb9f3_wt (branch bb9-f3, still at 78bd08e); PR NOT opened. Resume f3-package.
- C7 clean build DONE (bb9c7_wt/BB9/verify_c7/compile_clean.log 6890 s, probe 5/5 Closed); commit 597f410 on bb9-c7;
  CI job text in bb9_c7_coq/pkg/ci_job.txt, to add after the f3 PR merges. Resume c7-coq.
- c7-check never wrote its final REPORT; c7-triage had ~105 STOP rows left; bb8-fw1-redirect had just started its
  enumeration. Still-running CPU jobs: triage7.py (BB(7) pre-filtered scan), c7-triage qrun/loopwatch, an orphaned
  c7-coq h0fit python check (pid 45592, not needed: proof done).
Resume agents by SendMessage to their names (f3-package, c7-coq, c7-check, c7-triage, bb8-fw1-redirect).

2026-10-22 afternoon: machine REBOOTED; old agents unreachable afterwards (new session), relaunched fresh with full
briefs: c7-lower5 (bb9_c7_coq: Task A = Coq f_omega^5(5B) via the J2 clear, user said "regardless of cost"; Task B =
C7 PR after PR #30 merges), topmap9b (bb9_topmap: h003-family top-map search + h003 vs C7 level comparison).
PR #30 (f3, branch bb9-f3) CI was in progress in the cloud (unaffected). Restarted after reboot: cpucap governor,
triage7.py run 2 (BB(7) scan, 84/339 chunks done, resumable). LESSON: after a reboot, SendMessage to old agent names
fails; relaunch with self-contained briefs pointing at their notes.txt.
!!! 2026-10-22 c7-lower5: C7 f_omega^5 PROVED, lead re-ran c7/probe5.v (exit 0, 2x Closed): c7_lower5 N > f_omega^5(2*arrow 13 2 3),
c7_lower6_12 N > f_omega^6(12) (three f_omega above M8's headline). New files x/dev/C7Score5.v, C7Final5.v, c7/Lower5.v,
c7/probe5.v. Pitfall: unifying Defs.f_omega with Score.f_omega at a closed argument evaluates f (16-19 GB) -> transfer at
a variable. Goes into the C7 PR (Task B, after #30 merges).
2026-10-22 PR #30 (f3) MERGED 60a24cc; PR #31 (narrow CI: workflow edits no longer run every job; zf253.yml runs only on
ZF/** changes; manual + weekly runs still run all) MERGED f4d567f — user decision: "We don't really need to rerun each
proof every time we upload a new one", "Let's apply the same filter" (zf253). User: keep old BB9 record (BB9/verify)
in place with superseded wording; NO n1 CI job. Next: C7 PR (c7-lower5), then repo-tidy PR (agent repo-tidy,
worktree repotidy_wt, branch repo-tidy; champions table README, BBn/README indexes).
!!! 2026-10-22 h003 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC CONFIRMED (h003-check, strong
evidence, bb9_h003check/REPORT.txt): halts at H1 in every class, sigma > f_w^6(12B+26) > f_w^7(12) on paper = ONE omega
level above C7 (C7 <= f_w^5(5.4B+12) on paper). Real orbit [4,3,1,1,0] from tower residues; exit = M8 from a D0f config
with y+1 (exact resync lemma), so M8's all-class endgame applies. Coq agent h003-coq launched (bb9_h003_coq; aux X3 =
C04 with E0=0LJ, J=0LK---, K=1RK1RC). C7 PR #32 open (CI only bb9-c7). If h003 proves, it takes the BB9 row from C7.
!!! 2026-10-22 C7 PUBLISHED: PR #32 MERGED 09295ab (BB9/verify_c7, CI job bb9-c7 36m46s, probe 8/8 Closed; c7_lower5
f_omega^5(2*2↑^13 3) and c7_lower6_12 f_omega^6(12)). C7 is the BB9 entry; f3 dominated. Next: repo-tidy PR; h003 Coq.
2026-10-22 topmap9b DONE (bb9_topmap/REPORT.txt, ~250k tokens): h003-family tree (4 E0/H0 variants x H1/I0/I1, 2812
machines, W3 + 129 long reruns): NO sibling with a longer real top chain; h003 stays best (~f_w^6(12B)), C7 + twins next
(~f_w^5(5B)); 0LA0RA/0LA1RI = exit-free top loop K'=24R+c but no halt branch (likely non-halting); 69 STOP rows with
<=1 top unresolved. Independent agreement h003 > C7 by one omega level (paper).
2026-10-22 PR #33 (repo tidy) MERGED: README 261->77 lines with Current entries / Consistency machines / Superseded
tables, BBn/README.md indexes, no moves. CI: coq.yml filters now predicate-quantifier 'every' = one brace-union glob +
'!**/*.md' per filter (a NEW entry filter must follow that form: an extra plain line is ANDed); zf253.yml paths
['ZF/**','!**/*.md']. Docs-only PRs run no proof job. Weekly + manual runs still run all (user may drop weekly).
!!! 2026-10-22 ~19:00 h003 COQ-PROVED, LEAD-VERIFIED (agent h003-finish after h003-coq; bb9_h003_coq, 65 files, ~8.4 CPU-h):
lead re-ran h/probe.v (exit 0, 2x Closed; 18 table eq_refl incl. E0=0LH, H0=0LI, I=1RI/1RC, H1 None). Statement.v:
h003_table, h003_halts, h003_lower f_omega^6(6*arrow 13 2 3 + 2) < N, h003_lower7_12 f_omega^7(12) < N,
h003_beats_m8_bound. Defs identical to C7's from "Counting ones". => new BB(9) entry (one f_omega above C7). Next:
package BB9/verify_h003 + PR (G_top1 unused, drop). Verify: python tools/sched.py 3 h/probe.v; python tools/cq.py h/probe.v

2026-10-23: h003 PUBLISHED PR #36 (merge 84b7d4e), CI bb9-h003 1h19m green; h003 is the BB(9) entry, C7 superseded.
