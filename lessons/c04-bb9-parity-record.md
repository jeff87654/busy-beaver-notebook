---
name: c04-bb9-parity-record
description: C04 (BB9 record completion 1RB0RA_..._1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF) halts after 2nd escalation, sigma > f_w(f_w(12B)) -- parity invariant of its 5-adic chain; Coq-proved 2026-10-18 (see c04-bb9-candidate)
metadata:
  type: project
---

C04 investigation (2026-10-17, workspace bb8_list/investigations/bb9_c04_deep, REPORT.txt + notes.txt).
Result: C04 halts (H1) three to ~0.6P clears after activating the parked list 1^(12R2-10) (second escalation), so
sigma > 2^^(11 R2) 4 > f_w(f_w(12B+24)) >> fw2's f_w(f_w(465009)).  Status STRONG EVIDENCE (model verified in ~700 pkf4 worlds), not proved.
Key facts: the level-B cascade is ONE 5-adic affine orbit L -> (3L+c_r)/5, c = (32,-46,-64,-52; stop -100), all even => L mod 2 invariant;
L0 = 36B+73 odd; the only pre-escalation halt (10 <- 34 <- 46 <- 94...) is all-even => impossible.  Odd entry keys {31,37,43,49,55} all
lead to ESC then HALT (key 31 via P' mod 5 variants with counter modes).  Exact sigma is not computable in practice (entry point depends on
all base-5 digits of B), only bounds.

**Why:** the previous agent (bb9_parked) concluded "Collatz-hard" because the endgame value is uncomputable; the parity invariant makes the
uncomputable value irrelevant for the halting/record question.
**How to apply:** for cryptid-like 5-adic/affine chains, check residue invariants (mod 2, mod 3) of the chain constants before giving up;
a Coq proof would need the parametric sub-step lemma (hard part, see REPORT.txt section 6).  Related: [[bb8-champion-subtree-lead]], [[argon-bb9-fw2]].
