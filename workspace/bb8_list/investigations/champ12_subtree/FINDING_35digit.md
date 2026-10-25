# Champion-rule 8-state machines with a 35-digit start (found 2026-10-03)

Source: the 8-state TNF subtree that shares the BB(7) champion's first 8 transitions in first-use order
(root `1RB0RA_1LC---_1RD0LB_1RA1LE_---0LC_------_------_------`, `knuth8.exe exactsplit`, 8 parts in `m8/`,
67,976,045 nodes, 13,364 holdouts, 8.85 CPU-h), graded with `neighbors/dlscan2.exe` (`m8/dl2.tsv`).

Four holdouts graded CHAMPION (recount 2026-10-04; the fourth, `..._1RG1LD_1LC0RH_1RG1LH`, differs from the first only in H1) (the BB(7) champion's rules, halting when the digit list is used up) start from
K(2, 0^34; 0; 0), where the BB(7) champion starts from K(2, 0^10; 0; 0):

| machine | template (dlscan2) | start (step) |
| --- | --- | --- |
| `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF` | R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101 | 6,397 |
| `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG` | R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=1010 | 6,428 |
| `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC1RH_0LH0RF` | R,F,P=1,u=01,s=1,d=3d+1,b=3b+0,S=10101010 | 6,524 |

K(ds; a; b) = 0^inf P [u^(3d+1) s for each digit d, farthest first] u^(3a+1) s u^(3b+beta) S Q>0 0^inf.

Rules (identical to the BB(7) champion's, checked by literal probes, `m8_35digit_rulegrid.txt`, first machine):
- R1 K(ds; a+1; b) -> K(ds; a; 2b+2)  (a = 1..3, b = 0..9)
- R2 K(.., x+1; 0; b) -> K(.., x; 2b+2; 0)
- R3 K(.., y+1, 0^k; 0; b) -> K(.., y, 2b+2, 0^(k-1); 0; 0)  (k = 1..34, b = 0..5; zero digits kept)
- R4 K(0^n; 0; b) halts  (n = 0..35, b = 0..10: 42/42 halt; E0 is the undefined transition)
- 87 rule cases + 42 halting cases, no mismatch, no timeout.

Checks:
- Literal runs from the blank tape for 5*10^9 steps (`m8_trace_*.txt`): 51 consecutive family transitions per
  machine, all equal to the rule-level successor.
- An independent literal simulator (no template parsing) reproduces the start tapes exactly (and the champion's
  K(2,0^10;0;0) at step 2117).

Consequence (if R1-R4 hold for all parameters, as for the BB(7) champion): the digit list decreases
lexicographically, so the run reaches an all-zero list and halts; the list (2, 0^34) gives 24 more levels of the
champion's recursion than (2, 0^10), so sigma is far above 2↑¹¹2↑¹¹3 (roughly a 2↑^34-level bound; to be computed).
NOT yet machine-checked. Coq halting proof and a formal lower bound are the next steps.

Full m8 grading (recount 2026-10-04): CHAMPION 20 = 16 with the champion's 11-digit start + 4 with the 35-digit start;
NOBOUNDARY 9 = 7 with the 11-digit start + 2 with a 30-digit start K(2,0^29;0;0) that rebuild at the empty list
(`..._1LC0RH_1RG1RF`, `..._1LC0RH_1RG1RH`). dlscan.py (original template + kfit) found no digit-list machine in the 13,364 holdouts.
