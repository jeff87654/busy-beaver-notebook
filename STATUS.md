# Status (2026-10-25)

What is settled, what was searched and found empty, which claims in the notes are wrong, and what is still open.
When this page and a note disagree, this page wins. When this page and the
[main repository](https://github.com/jeff87654/busy-beaver) disagree, the main repository wins.

## Verified results (Coq, no axioms, in the main repository)

| label | machine | proved | notes here |
|---|---|---|---|
| champ_231 (BB(7)) | `1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB` | σ > 3↑^20 3 (twin champ_232 `…_1LC0RB`) | `lessons/bb7-champ231-lead.md`, `lessons/bb7-c231-coq.md`, `workspace/bb7_holdouts/` |
| M8 (BB(8)) | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---` | f_ω³(12) < σ < f_ω³(13) | `lessons/m8-bb8-c04-collapse.md`, `workspace/bb8_list/investigations/bb8_resid/` |
| h003 (BB(9)) | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC` | σ > f_ω⁷(12) | `lessons/bb9-c7-lead.md`, `workspace/bb8_list/investigations/bb9_h003*` |
| n1 (BB(10)) | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RZ0LC` | f_(ω+1) level, exact score | `lessons/bb10-n1-coq.md`, `lessons/bb10-selector-c1-counter-grower.md` |
| T12a (BB(12)) | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF1RZ` | f_(ω+1)² level, beats n1 | `lessons/bb12-t12a-coq.md`, `lessons/w2-12state-search.md` |
| M13 (BB(13)), by Argon | `1LB1LA_1RC0LA_1RD1RC_1RE1RK_1RF0LJ_0LG1RI_1RE0RH_1LF0RC_1RM0LE_1LA1LE_0LL1LB_0RM1LL_1RZ1RH` | σ > f_(ω+2)(f_ω(20)) | `lessons/m13-argon-bb13.md`, `workspace/FW2_13_14_SEARCH_AND_PROOFS.md` |
| M14 (BB(14)), by Argon | `1RB1RA_1RI1RC_0LD1LG_0RE1LD_1LN1RF_1LJ0RA_1RA0LH_1LG1LH_1RK0LM_1RZ0LE_0LE0RJ_1LH1LM_0LH0LL_0LG1LN` | σ > f_(ω+2)³(15) | `lessons/m13-argon-bb13.md`, `lessons/m14-argon-bb14.md`, `workspace/FW2_13_14_SEARCH_AND_PROOFS.md` |
| BB(4,3) champion (Kropitz) | `1RB1RD1LC_2LB1RB1LC_1RZ1LA1LD_0RB2RA2RD` | σ = 4·e₄ + 18 exactly | `lessons/bb43-champion-coq.md` |
| Consistency machines | ZF/ZFC 253, 254; ZFC+GU 296; ZF 335; PA 238; PA ⊢ Goldbach 449 | halts iff inconsistent / iff provable | `lessons/zf-*.md`, `lessons/m254*.md`, `lessons/pa-goldbach-coq.md`, `workspace/zf/` |

Superseded but also Coq-verified (useful as proof bases): champ35 (BB(8), 12·(2↑^37 3) + 59), C04, f3_0RC, C7
(BB(9) at f_ω³, f_ω³+, f_ω⁶), fw2 (Argon, BB(9) f_ω²), the 2026-10-07 BB(9) record, 0LA and its three-cycle sibling
(BB(9)), 0LJ0LC (BB(10)), and Jacobzheng's BB(9) champion with its lower bound.

Records came in this order: champ35 → BB(9) 2026-10-07 record → 0LA → n1 → T12a → M13/M14 → fw2 → C04 → M8 → f3 → C7
→ h003, with champ_231 at BB(7). Notes written before a step describe the old bar as current.

## Routes searched and closed (negative)

Don't repeat these without a new idea; each report says what exactly was covered.

- **9-state f_(ω+1) using a 1–2 state gadget on a 7/8-state host.** Covered by fw1-counter9, fw1-hosts and fw1-hosts2,
  bb8_fw1_redirect, topmap-sweep (`bb9_fw1_counter/`, `bb9_fw1_hosts/`, `bb8_fw1_hosts2/`, `bb8_fw1_redirect/`,
  `bb9_topmap_all/`). Exits decided by a residue cap at f_ω^k; f_(ω+1) needs a counter that lives outside the list.
  See `lessons/fw1-search-20261022.md`.
- **BB(7)-champion lineage at 9 states, grow-and-count:** c7m12, n1f0 (394k holdouts), roots9, BB(7) Ackermann
  parents (`lessons/bb9-fw1-search-status.md`).
- **Collapse search:** h003, C7, n1, T12a and M8 have no (n−1)-state collapse; M8 is the unique collapse of C04 among
  499,305 candidates (`collapse_search/REPORT.txt`).
- **12–13 states at ω+2:** G6 and n1 slices, right-end counter route, farcount and borrow, all negative
  (`lessons/w2-12state-search.md`, `workspace/bb8_list/investigations/w2_search/`).
- **BB(7) holdout list:** digit-list layer fully ranked; reb7 classified all 1,797 rebuilders with no rebuild-then-halt
  record; the never-halt verdicts were audited (`lessons/bb7-holdout-triage.md`, `lessons/bb7-never-audit.md`).
- **BB(8) radius-3 digit-list neighbourhood** of the 1RB1RA Ackermann parent: 15.2M machines, nothing halts at a rebuild.
- **Halt redirect of the BB(9)/BB(10) champions** (`halt_redirect/champions_redirect.md`).
- **Doubling-class BB(8) holdouts:** many settled one by one with Coq proofs, then deprioritised: doubling counters cannot reach record size.
- **ZF machine size:** Wade's framework is near-optimal for its design; proto searches negative
  (`lessons/zf-framework-study.md`, `lessons/zf-framework-design-lessons.md`).

## Claims in the notes that turned out wrong

- **"C04 is Collatz-hard / not a usable record"** (`bb9_parked/`): wrong. A parity invariant settled it, and it became a
  record (then M8).
- **M3 "f_(ω+1)"** and **1LD1LC "ω-level 2"** (2026-10-08): both are ω-level 1. The growth metric counted parked lists
  that are never cleared; judge growth by the cleared list only.
- **c231ext "class F6 unconditionally halts"**: refuted; F6 never halts (`bb8_f6_verify/REPORT.txt`).
- **X33 / Z16 "strong evidence halts"** (`bb7_holdouts/rank/notes.txt`): retracted in the same file.
- **P11 prefix-digit borrow** (`w2_search/inplace/NOTES.md`): an artefact of trimming the counter.
- **C13a "tier-1 candidate"**: never halts. **H14**: halts by a different mechanism than "Collatz gamble".
- **M11 (Argon) "beats BB(11)"**: refuted in Coq; n1 beats it (`lessons/m11-argon-bb11.md`).
- **`bb8_twoslot_x/REPORT.txt`** gives a wrong string and size for M8.
- **Argon reports that call simulation "proof":** `bb9_pbarrier_fw1/REPORT.txt` ("MAJOR BREAKTHROUGH"),
  `bb9_triage7_and_1RB1LA/REPORT_champ231_ext.txt` ("PROVEN f_(ω+1)", really about f_ω³),
  `bb9_champ231_accel/REPORT.txt`, `bb9_f89_and_cascade/REPORT.txt`, `bb8_c231_clonesplit/REPORT.txt`. None is Coq-checked;
  all are below h003 if correct.
- **Tool soundness:** `ngann.exe` is unsound for 9 or more states; the 489 "STATIC MSD" rows in `bb9_fw1_counter` were an
  artefact; h003 was first filed TIME by a grader with a hard-coded parameter.

## Open

- [`workspace/bb8_list/investigations/OPEN_CANDIDATES.txt`](workspace/bb8_list/investigations/OPEN_CANDIDATES.txt):
  the project's log of record-relevant machines that could not be settled, with the obstacle for each (its
  "current bars" header is from 2026-10-18).
- **n1 + one 1** (`bb10_beat_n1/REPORT.txt`): a 10-state variant reported to beat n1 by a single extra 1, checked only
  with symbolic lemmas; no Coq proof.
- **m8sweep** (`bb8_m8sweep/`): stopped early, inconclusive. Of 716 f_ω bases only 92 reached tier 1, and E=5 timeout
  leaves are unresolved. The report includes resume instructions.
- **twoslot8** (`bb8_twoslot/`): partial negative; 579k diverged children unscreened, champ_231/232 trees not run.
- **Not started:** 8-state continuation of the 452,828 BB(8) holdout rows with ≥ 2 undefined transitions via a new state
  (TNF territory no enumeration reached); c7m10/c7m11 at 9 states; a designed 10-state f_(ω+1) engine at 9 states.
- **Uncertifiable by design:** Y1 (BB(9)), whose halting depends on a residue class (`lessons/bb9-y1-class-dependent.md`).
- **ZFC ⊢ Goldbach** at 399 states, parked (`workspace/zf/m254gb/`).
