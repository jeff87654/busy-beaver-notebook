# f_(omega+2) search, 12-13 states (lead brief, 2026-10-09)

Goal: a 12- or 13-state TM that halts with sigma at f_(omega+2) level, built on our proved 10-state f_(omega+1)
machine n1 or its looper cousin G6. Bar: n1 (BB(10), f_(omega+1)(~2^^363)). Tiers:
- Tier 1 (already a big win): halts after >= 2 FULL rounds, each round = counter reloaded from the accumulator
  (f_(omega+1) per round), i.e. f_(omega+1)^2 or more.
- Tier 2 (the target): number of rounds ~ b (the huge start parameter) or ~ an accumulator, i.e. f_(omega+2).

Read first: memory notes bb17-bb18-champion-anatomy, bb10-selector-c1-counter-grower, bb10-n1-coq, bb9-fw1-search-status
(C:/Users/jeffr/.claude/projects/C--Users-jeffr-Downloads-bb8/memory/); bb_champs_17_18/NOTES.md (BB17 = engine + counter
layer + merge/parity layer: when c empties, d -= 2 and c is refilled from the accumulator by a merge; when d empties, d
is refilled from the accumulator; halting = parity gamble on the d refill); halt_redirect/selector.md (n1 6b, G6 s2, c1 s5,
gadget-search negatives s3); bb10_n1_coq/NOTES.md (n1 event specs, lit.py literal B-form simulator).

Bases:
- n1 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC : halts J0 at counter exhaustion,
  config `FarE k + [0 1^w | 1 | R]` (far bits = (10101)^k + fixed 44-bit tail). Event H [1^(n+1)|a] -> [2,1^(2a+4),0,1^n|6]
  already turns an accumulator into a counter list (it happens once at startup).
- G6 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI--- : never halts; each exhaustion
  ("left event", borrow runs off the left end) repacks a NEW counter of ~0.8R D6 tokens: rounds u_(i+1) ~ f_(omega+1)(u_i).
  J1 never read. Missing: an outer counter d decremented per round + halt when it empties (+ a way for d to be big).

Method (house style: cheap automation before tokens, reusable tools, judge growth by the CLEARED list (zeros=) not k):
1. Instrument the base: find the literal stages at round boundaries / exhaustion and the transitions read ONLY there
   ("hooks"; clone-split idea in bb9-fw1-search-status: redirect a used transition X->T to new state K = copy of T except
   on one symbol). Never modify transitions used inside the follower's jumps (that invalidates fol.py).
2. Lazy TNF enumeration of the gadget (new states K, L, (M) + free slots), branching only on slots actually read, through
   literal tests on crafted small configurations (several R / n / k values to see scaling), then follow survivors from the
   real start with fol.py (std / big / shrink policies) across several rounds and several b0 values.
3. Grade: halts? after how many rounds? does each round reload the counter from the accumulator? rounds vs b0?
Report honestly: screening evidence vs proof. No Coq yet; a Tier-1/2 hit gets a separate verification pass.

Constraints: CPU is capped (governor bb8_list/cpucap.ps1, 25% hard cap); keep your own jobs to <= 2 processes, Idle
priority. Write all files under your own dir (w2_search/<base>/); do not modify halt_redirect/ tools in place (copy them).
The Write tool may refuse .md reports from subagents: write REPORT.md with a Bash heredoc. Keep a NOTES.md as you go.
