---
name: strategy-20261023-three-agents
description: "2026-10-23 strategy review (post h003/champ_231) and the three Opus agents launched: collapse-search (h003/C7/n1 state collapse), bb7-nonlist (BB(7) holdout non-digit-list residue), pocket-rescreen (roots_grade + unranked 8-state rows)"
metadata:
  node_type: memory
  type: project
  originSessionId: 5e92689a-bb4e-41de-a5bc-e6878af2c5a7
  modified: 2026-10-23T16:07:49.875Z
---

Ranked 2026-10-23 for the user ("highest yield areas for a new 7/8/9 state champion"), after all one/two-state
gadget routes to f_(omega+1) at 8-9 states were closed negative (fw1-counter9, fw1-hosts, fw1-hosts2, bb8_fw1_redirect,
c231ext, topmap-sweep):
1. Collapse search (no tool existed; M8 = C04 collapsed 9->8 by hand). Targets h003 -> 8 states (BB(8) by 4 omega
   levels), C7, n1 -> 9 states (f_(w+1) at 9), T12a, M8 -> 7. Agent collapse-search, folder
   bb8_list/investigations/collapse_search/. Positive control: the enumeration must find M8 from C04.
2. BB(7) holdout non-digit-list residue: pf7 passers with no dlscan2 template were never examined (all scans were
   digit-list templated; N2 proves segment codings exist). Agent bb7-nonlist, folder bb7_holdouts/nonlist/.
3. Never-queued pockets: champ12_subtree/roots_grade/dl2.tsv (1,814 rows) + 8-state graded rows never ranked by
   rank8 (only 21 ranked). Agent pocket-rescreen, folder bb8_list/investigations/pocket_rescreen/.
Judged low yield (not launched): three-slot M8 extensions (residue-decided top chains cap at a few omega levels);
one-state redirects of the other ~1,790 7-state rebuilders (bb8_fw1_redirect's structural <=1-rebuild argument).
9-state f_(omega+1) otherwise needs a designed engine (moving separator + 3-state counter) = 10-state budget.

**How to apply:** read the three REPORT.txt files before relaunching anything; append results here.
Related: [[fw1-search-20261022]], [[bb7-holdout-triage]], [[m8-bb8-c04-collapse]], [[screening-lessons]].

2026-10-23 collapse-search DONE, NEGATIVE (collapse_search/REPORT.txt, ~4 core-h, ~300k tokens): 7.2M (n-1)-state
candidates (delete+retarget, absorb, merge) screened literally against start batteries from the parents' real runs;
control = M8 is the UNIQUE survivor of 499,305 C04 candidates. h003/C7/twins -> 8: 0; n1 -> 9: 0 (2.46M); T12a -> 11: 0;
M8 -> 7: 0 (best = BB(7) champion). Structural reason: every target uses all non-halt slots; a collapse needs a relay
state (C04's G) or two states agreeing on used slots; only halting-peek pairs (J~E in n1, H~F in M8) exist. Not
enumerated: two deletions + one new state; other engines. Tool: collapse_search/src/cand.py <MACHINE> + cfollow3.exe.

2026-10-23 ~12:00 F6 FOLLOW-UP: c231ext's folder was extended after its 02:50 verdict (MULTI_ROUND_PROOF.txt + REPORT
section, 11:05) claiming class F6 = 1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RG (champ_231 + C1->0RH,
H=---1RG) halts after a rebuild when a tail length m == 0 mod 3 (else next round). REPORT header still says "no halt
after a rebuild"; never in OPEN_CANDIDATES. Lead found a gap: 3.7 treats N_1 as ~3^^20 and says only ~20 blocks of the
9.3e18-block tail are consumed; N_1 ~ 3↑^20 3 so the tail is fully consumed and Round 2's start/m are unknown.
Stakes: halt at round 2 ~ f_w^2 (< M8); round >= 3 beats M8. Agent f6-verify (Opus, bb8_list/investigations/bb8_f6_verify/).
LESSON: an agent's late-appended analysis can contradict its own header verdict; re-read the whole report, not the
header, and grep OPEN_CANDIDATES for each named candidate.
2026-10-23 f6-verify DONE: F6 NEVER HALTS (rule-level, bb8_f6_verify/REPORT.txt, rsim.py; 25 CPU-min). Section 3.7's
Regime II was wrong: the B=1 countdown end with odd U is a CARRY (1^U -> (U+3)/2 blocks of 1100 pushed left as fuel,
countdown resets to B=53), not an expansion into 2-blocks; each carry pushes ~2x the fuel the next countdown needs ->
exact repeating cycle, Round 1 never ends, H0 never read. Entry moved to SETTLED in OPEN_CANDIDATES.txt.
2026-10-23 ~17:30 BB(7) coverage assessment (user asked "scanned everything?"): digit-list layer fully ranked; pf7 passers
(17%, 2.9M) through bb7-nonlist's coding-agnostic probe (scan done 15:03, tiers, top rows HT 3 vs champ_231 HT 4, hand exam
running; L1 1RB---_1RC1RD_... = ~3^^7000 tower, not record class, halting open); the 83% pf7 REJECTS (~14M) seen only by
pf7's longest-run-of-1s reset signal, calibrated on digit-list controls only. Gap: gap-coded / segment-coded counters.
User approved ("Let's do it!"): bb7-nonlist follow-on = pf7 miss-rate check on N2, famT14 gap-coded rows, fam0LD, L1/X1;
if misses, a second coding-agnostic reset signal (RLE token-count or span-growth drops) over all pf7 rejects, then nlp7.
Also: pocket-rescreen told to cap the 1,119 gap-coded roots rows (exponential per round expected) and write its report.
2026-10-23 pocket-rescreen DONE, NEGATIVE (pocket_rescreen/REPORT.txt, ~8.5 h wall, 5+ helper subagents): 323 eight-state
rows ranked (315 new) + 1,814 roots holdouts growth-probed; no row at/above M8, nothing halting between champ35 and M8.
rank7 CANNOT see M8-type machines (measures first exhaustion only; M8 scores 13 / leaves-template) -> follow every
leaves-template row. Rebuild-forever hosts listed for gadget work (T1/T2 family, champ35 H1 variants, level-63/21 families,
F4.13). UNSCREENED: 1,119 roots rows of 1RB1LG_0RC..., counter in zero-gap lengths; first exhaustion <= level 14, early
read exponential per round; needs a gap-coded engine (outline famT14/notes.txt HANDOFF). Low priority.
2026-10-23 evening, user: "What else could we be missing?" -> list of gaps: (1) provenance/deciders of the 16.9M list
(bbchallenge community file, deciders unknown to the user); (2) M8 recipe one level down = 6-state base + 1 state;
(3) pf7 coding blind spot (bb7-nonlist follow-on); (4) time depth ~1e9; (5) non-list mechanisms; (6) Collatz-like.
CORRECTED: 2.67% of holdout rows (452,828 of 16.9M) have >= 2 undefined transitions (the 10% from the first 20 chunks was a sort artefact: 1RB--- rows sort first) -> the first-reached
slot can be redirected to an EXISTING state (28 completions, still 7 states), never enumerated by TNF. ~1,500 per 1M
rows have a fully undefined 7th state = embedded 6-state holdouts (~25k total).
Launched (user: "Let's see an agent on 2 and 3 plus whatever else"): bb7-from-bb6 (Opus, bb7_holdouts/from_bb6/:
embedded 6-state holdouts + published BB(6) top halters, + 1 new state, faithful follow, M8-from-champion control) and
bb7-slot-redirect (Opus, bb7_holdouts/slot_redirect/: >=2-undefined rows, size-ranked, 28 completions each, same control).
2026-10-23 bb7-slot-redirect DONE, NEGATIVE (slot_redirect/REPORT.txt, 1.3 CPU-h): of 452,828 rows with >= 2 undefined slots,
69,619 pass pf7, only 7 get a dlscan2 template (all no-growth), 72 in the nonlist pool (3 f_omega flags, all false: constant
refill ~676), 3 natural halters with ~1e5 ones; no first exhaustion worth redirecting. Controls: pf7/dlscan2 see two-slot
machines (champion + empty H graded CHAMPION); M8 reproduced (H0 = 1RG/0RB/0RE give the 11 97 12 4374 2617 signature).
Follow-up assigned: vary DEFINED-BUT-UNUSED transitions of record-relevant one-undefined rows (28 options each).
2026-10-23 user: deep prefilter-free scan of the ~25k embedded 6-state holdouts added to bb7-from-bb6 (dlscan/dlscan2 at
5e6+ census, rank7, nlp7 at 10x budget on all rows, reb7; controls BB(6) champion + Kropitz). Second prize: any 6-state
Ackermann-class halter beats BB(6) = 2↑↑↑5.
2026-10-23 free-slot follow-up (bb7-slot-redirect) NEGATIVE, pool EMPTY: all 3,647 record-relevant one-undefined rows use all
13 defined transitions (last first-use at step 7,017). STRUCTURAL: TNF defines a transition only when the run reaches it,
so listed rows never have unused defined transitions; free slots exist only in hand-built machines (relabels/redirects).
=> inside the 7-state holdout list, no slot-variation construction remains; new states or new engines only.
2026-10-23 late: user asked "what else could be missed, thinking broadly". Checked reb7: multi-round nesting IS followed
(rounds7/mrounds explore (template, V mod Q, n) states to a loop or halt; class branching), so low-first-level rebuilders
with many rounds are covered for templated rows. New construction assigned to bb7-slot-redirect: ENUMERATION
CONTINUATION = the 452,828 >=2-undefined rows are un-enumerated branch points whenever the blank run reaches the first
undefined slot at all (setup phase 1e6-1e11 steps); run all to ~1e10, 28 children per reacher, full pipeline on children.
Remaining blind spots (not actionable yet): residue-gated halts in untemplated rows (no faithful re-test exists outside
digit lists), two-sided/multi-list engines, deciders' errors upstream.
2026-10-23 bb7-from-bb6 DONE, NEGATIVE (bb7_holdouts/from_bb6/REPORT.txt, 2.5 CPU-h): 22,069 embedded 6-state rows; only
the 663 rows of the 2026-10-16 bbchallenge BB(6) holdout list are live (rest proven non-halting, undefined slots never
reached). dlscan2 at 1M/10M census on all 663: ZERO Ackermann grades -> NO 6-state digit-list engine exists; 95
engine-like growers are irregular cryptid strings/counters. 20 wiki BB(6) top halters verified by simulation; 4,560
+1-state extensions: best = one more round of the base (<= ~2↑↑↑6). STRUCTURAL: all 6-state engines are fixed depth
(binary counter / exponential Collatz map); one extra state adds rounds, not levels. M8 control reproduced (260-row set,
8 two-escalation halters). => 7 states is the first level with a variable-length (f_omega) list engine; BB(6) stays
tetration/pentation class. Not pursued: state-split-with-halt on non-halt transitions (same fixed-depth argument).
2026-10-23 late, user approved: bb7-never-audit (Opus, bb7_holdouts/never_audit/) = adversarial re-verification of the
top-30 largest 7-state NEVER-HALTS verdicts (levels 20-424, 18 f_(w+1) bases) with independent rule derivation +
residue-faithful exhaustions; controls M8 (must halt), N2/X33/i (must stay never). bb7-nonlist told: tier-1 rows get
real-class first-exhaustion decisions (UNDECIDED if class unknown), second pass at 10x budget + reset-time histogram.
Deferred (user's call): 9-state f_(w+1) design project.
2026-10-23 21:17 bb7-nonlist MAIN PASS DONE, NEGATIVE (bb7_holdouts/nonlist/REPORT.txt, ~18 CPU-h, 0.55M + 1.47M tokens):
pool 2,953,416 (pf7 pass minus dlscan2-graded); growth filter -> 563,521 full-probed; 367 FR (refilled-digit) families,
215 hand-examined by 6 Opus subagents (all 110 tier-1). Every long list except the H1 class = unary counter (<= ~3 arrows).
H1 CLASS logged OPEN (low) in OPEN_CANDIDATES.txt: H1 1RB1RE_1RC1RA_0LD1LE_1RE1LE_0RG0RF_---0LG_1LC1RA, H2, c01
1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0LD0LB, c02 (0RD0LB) = genuine f_omega lists (H1 ~20 groups, level ~42 at
first exhaustion; c01 1533 groups) that REBUILD at exhaustion (f_(w+1)-type loop like N2); probable never-halters, no
invariant/proof; a halt would be far above champ_231. Side: 397 holdouts halt naturally at 1.2e9-1.2e11 steps (<= 420,675
ones, halts_exact.tsv); L1 ~3^^7000, M1 ~2^^55, M5 ~2^^^15 probable halters, all small. Gaps: 0.6% slow starters; 11,147
no-FR families unexamined; rebuild-then-halt not caught by small probe. Tasks (A) tier-1 real-class decisions and (B) pf7
miss-rate + 10x second pass over ~14M rejects were NOT done in the main pass; re-assigned 2026-10-23 ~21:30.
2026-10-23 ~21:45 user approved: h1-extend (Opus, bb7_holdouts/h1_extend/) = M8 recipe on the H1 class (H1, H2, c01, c02:
untemplated f_(w+1)-type loopers never in any +1-state sweep). Step 1 = is the undefined slot (F0 / A1) reached in the
real run; then 68^2 one-new-state children per base, faithful residue follow; control = champion -> M8. Bar M8 (8 states),
h003 (9). Record only if the gadget halt comes after >= 3 rebuilds (first-exhaustion halt of c01 ~ f_w(3000) < M8).
2026-10-23 h1-extend DONE, NEGATIVE (bb7_holdouts/h1_extend/REPORT.txt, ~6 CPU-h, 0.3M tokens): in H1, H2, c01, c02 the
undefined slot (H1 F0, H2 G0 [not F0], c01/c02 A1) is NEVER reached from the blank tape (strong evidence, all classes: every
exhaustion has the form ACC|(1,0) + blank; exact macro sweeps over 10,242 ACC phases through exhaustion+rebuild, 0 halts;
rebuild periodic in ACC mod 8; all defined transitions first used by step 122). So every +1/+2-state child via the slot runs
exactly like its base. CTL (NGramCPS 16/16, ngann 10/10) cannot prove it. Control: champion reaches E0 from every exhaustion
config; M8 is among 94 literal survivors of 260 children (ranking needs pkf6). H1 class stays OPEN/low (never-halting proof
open). CORRECTION: the BB(7) champion is 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF (E0 undefined), not 1LF0LC.
=> M8 recipe exhausted on all known f_(w+1)-type 7-state loopers (templated bases earlier, H1 class now).
2026-10-24 bb7-from-bb6 DEEP 6-STATE SCAN DONE, NEGATIVE (from_bb6/REPORT.txt "DEEP 6-STATE SCAN", ~8 CPU-h): 22,089 rows
(22,069 embedded + 20 top halters with halt slot undefined), no pf7 prefilter; dlscan2 2e7 census: 0 graded; dlscan: 0 keys;
nlp7 at 1e7 macro steps: 69 FR rows (mostly powers of 2 = binary counters), 10 tier-1 rows, none hierarchical. 14 natural
halts all bbchallenge-decided (sigma 2.6e5-1.5e6). Best 663-holdout row 1RB1RA_0LC1RF_0LD1LD_1LE1LC_0RB0RA_---1RE =
exponential counter (digits 4^j-1), no hierarchy. Top loopers (champion-like 1RB1RA_1LC1LE_0LD0LB_0RA0RF_0LC0RA_1RD---,
~f_4-f_5; unary lists up to 43,599 items) never reach their slot. CORRECTION to earlier claim: the 21,406 non-live rows
include known halters (16 of 20 top halters), not only proven non-halters; verdict unchanged. CONTROL CAVEAT: no listing
tool grades the BB(6) champion or Kropitz (not digit-list engines); nlp7 flags Kropitz but misses the champion and #2 ->
the pipeline cannot see champion-type binary-counter/Collatz halters nor rank them. BB(6) stays tetration/pentation class.
2026-10-24 bb7-slot-redirect ENUMERATION CONTINUATION DONE, NEGATIVE but INCOMPLETE (slot_redirect/REPORT.txt last section,
~10 CPU-h): all 452,828 >=2-undefined rows run from blank with a macro simulator (BB(5) exact). Only 30 rows reach an
undefined slot (1 at 1e8, 1 at 1e9, 28 at 1e10-1e11), all listed holdouts that actually halt small (17k-294k ones; largest
1RB1RE_1LC0LB_1RA0RD_0LB1LD_1RF---_0RC1LG_---0RA, 9.6e10 steps). 840 children (28 each): 94 halt at once, 3 later (best
172,858 ones), 15 cycle, 728 still running at budget (396 to 1e13; 216 stuck at branch); 7 nonlist f_omega flags = fixed
lists of 14-51 items, tower ~50 high, far below f_w(20). Standard pipeline blind here (branches at >= 8.3e8 steps, past pf7
3e5 / dlscan2 1e6), nlp7f at 2e7 macro used instead. GAP: 291,881 rows (64%) do not accelerate, run only to ~1e6-1e7
(lower bounds only); literal sample 514 to 3e8-1e9: no halts; miss rate ~1/1000 not excluded. Also 135k rows at 1e7-1e9.
2026-10-24 bb7-never-audit DONE, NO VERDICT BROKEN (never_audit/REPORT.txt, final_verdicts.tsv, ~6 CPU-h, 0.55M tokens):
166 NEVER rows reach lists >= 20 digits (34 reb7 families); 173 rows audited with independently derived codings, symbolic
borrow rules (sound for values >= 1000 per class mod 720), per-class exhaustions (all 720 classes for the 6 largest),
own invariants + lockstep vs literal 1e9 run. 160 CONFIRMED never, 9 UNDECIDED (tools cannot model), 4 no coding fits;
162/166 big rows have a confirmed family member. Undecided exceptions: F5 (3 outer-counter rows, level 26, odd-class
rebuild into unparsed marked list, no halt seen) and F89 (1 multi-template row, level 27). Zero rule disagreements with
reb7; every halting condition met is a parity fixed by an invariant. Controls: X33/i/Y19/Z16 stay never; champion
exhaustion halts in every class; M8 marked OPEN (leaves template) but its real-class halt NOT reproduced (needs the 5-adic
cascade model); N2 not covered by its codings. => reb7's NEVER verdicts at record-relevant size stand; M8-type halts remain
visible only as "leaves template", never as reproduced halts, in every generic pipeline we have.
2026-10-24 user approved: f5-f89-settle (Opus, bb7_holdouts/f5_f89/) = settle the 2 record-relevant rows never-audit could
not confirm: F5 (3 outer-counter siblings, level 26: odd-class rebuild into an unparsed MARKED list 0^2 1 1 0^2..., M8-like
shape) and F89 1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE (level 27, multi-template u=01/s=011). Real-class
decisions only; controls champion + a confirmed F row. Other 11 audit leftovers are not record-relevant (levels 0-3, N2, POLY).
2026-10-24 f5-f89-settle interim (F89 subagent, f5_f89/f89/REPORT.txt, 0.3 CPU-h): F89 NEVER HALTS, single class. Coding:
K-config = state D onto fresh left cell; tape 00 then blocks [1 (01)^d]; rules D [a,b]->[a+4,b-2], B_k, T_k, S [x]->[1^(x+2)];
invariant "all digits odd" closes every rule, no rule halts. Real run hits [1^30] at step 4679; 3e8-step lockstep 7746
K-events 0 misses; 900 literal cases 0 misses. Siblings = relabels/mirrors, same verdict. Not Coq-checked (unbounded k, x
rest on msim.py). F5 still in progress.
2026-10-24 f5-f89-settle DONE: F5 and F89 both NEVER HALT, strong evidence, not Coq, NOT residue-gated (f5_f89/REPORT.txt,
~2 CPU-h). F5 (3 siblings, identical traces 3e8 steps): coding unit 10 with '.'/'#' separators, state [A|d1..e#, c#]; the
audit's "marked list" = a second segment "1 # c #" made by the top event Tk; rules D/Bj/Mj(merge)/T0/Tk, each depth-j rule
valid iff A >= 2j, guaranteed by a paper safety lemma A >= 4j+2 (induction F_j(y) >= 2y+4j-2); parity invariant A even,
digits >= 2 even, c odd; round = rebuild -> Tk marked list -> merges -> T0 longer rebuild; the level-26 exhaustion is just
T25, no class split. Lockstep 0 misses, symsim 1404 runs 0 bad to depth 31. Controls: champion halts in all 12 classes at
both exhaustions; audit-confirmed F68 re-confirmed and its below-threshold literal halts are seen. => the never-audit's 2
record-relevant undecided rows are closed; every record-size BB(7) NEVER verdict now independently confirmed or
explained. Coq proofs would be N2-method work (REPORT lists requirements), no residue engine needed.
