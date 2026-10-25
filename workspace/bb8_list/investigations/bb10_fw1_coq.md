# BB(10) candidate M3 `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA`: Coq

Agent inv-bb10-fw1-coq (Opus 5.5), 2026-10-08. Tools: `bb10_fw1_coq/`. Proofs: `bb8_list/proofs/BB10_fw1_*.v`.

## Verdict

**HALTS: machine-checked (check.py PASS). It beats the BB(10) lead 0LJ0LC and the 9-state 0LA. Both comparisons
are machine-checked.**

    PASS BB10_fw1_1RB0RA.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA HALTS (machine-checked, no axioms)

- Score at the halt: N ones, with N > 2↑^(4T+41) (2↑^(4T+39) (2↑^(4T+35) 5)), where T = 2↑^37 3 = 2 b_f + 4 and
  ↑^k means k arrows.
- In particular N >= 3·B3, where B3 is the fourth nested clearing at depth z+6 = 8 b_f + 55.
- This is omega-level 1, as the revised analysis said. The f_(omega+1) claim was withdrawn before this proof was
  written, and the proof follows the corrected 7-jump run.
- Score convention: busycoq stops before the undefined I0. The standard score is N + 1.

| file | content | compile (Idle) |
|---|---|---|
| `BB10_fw1_parts.v` | generated machine-level lemmas: R1t, R2t, R3t (champion rules on raw tokens), ST1, S2x5, S3, S4, S2A (unpack), S2R (W-loop round), H1 (zero-list conversion, n = 10k+17), WRodd, H2 (halt in I0, any z) | 2070 s |
| `BB10_fw1_st0.v` | generated stage 0: K(0^(M+1); 0; b) -> [D6^(4b+2), D2, D2, D0, D5, 0^(M+8b+15) \| 1 \| 1] for all M, b >= 1 (351 lemmas) | 4453 s |
| `BB10_fw1_init.v` | the BB(8) record's 6397-step start-up | 826 s |
| `BB10_fw1_glue.v` | token family `Kt`, W-forms `Wf`/`Wo`, the rules on the family, clearing `CDP` (any bottom m) | ~100 s |
| `BB10_fw1_arith.v` | `U_closed` (2 U j x + 4 = 2↑^(j+1)(2x+4)), `U_mod10` (U j x = 6 mod 10 for j >= 1), monotonicity, `U_ge_exp`, `U_ge_lin` | ~130 s |
| `BB10_fw1_run.v` | `ST0K`, `run_to_P1`, `period1`, `S2_halt`, `run_halts`, **`halt0`** | 14 s |
| `BB10_fw1_1RB0RA.v` | the machine table and `Theorem halt : halts tm c0` for check.py | 59 s |
| `BB10_fw1_bound.v` | `ones_cH` (ones = 6w + 2z + c + 7n + 58), `score_ge` (N >= 3 B3), `B3_big`, `bf_closed`, **`sigma_lower_bound`** | 95 s |
| `BB10_fw1_vs_lead.v` | **`beats_lead`**: the 0LJ0LC lead's ones at the halt (`BB10_lead_bound.score_closed`) < M3's | 59 s |
| `BB10_fw1_vs_0LA.v` | **`beats_0LA`**: the 0LA machine's ones at the halt (`BB9_redir_0LA_bound.score_closed`) < M3's | 66 s |

Every file prints Closed under the global context for its main theorems.

## The run, as proved

Tokens are listed nearest the head first. D(m) = (10)^m 1. `Kt ts a r` = .. D(t2) D(t1) D(a) D(r) D(2) G> 0^inf.
An accumulator with b-value B has r-token 3B + 1. U is the BB(8) record's clearing function. With z = 8 b_f + 49:

| step | result | lemmas |
|---|---|---|
| start-up and the record's clearing | Kt(0^35 \| 1 \| 3 b_f + 1), b_f = U 34 (U 34 0) | `init_reach`, `CDP` |
| stage 0 (E0 -> I, J) | [D6^(4b_f+2), D2, D2, D0, D5, 0^z \| 1 \| 1] | `ST0`, `ST0K` |
| jump 0: D5 -> D2 at depth z | s1 = U z 0 | `CDP` |
| stage 1, then R3 with r-token 2, then D9 -> D3 | P1 = [0^(z+1), 3, 5, C0, F], C0 = 7 + 6 s1, B0 = U^2_(z+1)(0) | `ST1K`, `BORROW2` |
| period 1: S1, S2 (x = 5), S3, S4 + R3 + D9 -> D3 | P2 = [0^(z+5), 3, x2, 6 s1 - 4, F], x2 = 5 + 6 B3 | `period1` |
| period 2: S1 | accumulator B5 = U_(z+5)^3(0) | `BORROW` |
| S2 with B5 << B3 | unpack D(x2) (x2 = 13 + 4w); W-loop of R5 rounds; the zero list (n = 8 b_f + 12 B5 + 67 = 10k + 17) is converted into an odd run of 6k + 13 units; W-loop; the last unit -> HALT in I0 | `S2AK`, `WL`, `H1K`, `WLo`, `H2K`, `S2_halt` |

Facts the halt needs, all proved:
- **Residues.** U j x = 6 (mod 10) for j >= 1, because 2U + 4 = 2^(2^f) = 16 (mod 20). Applied to b_f, B5 and B3,
  this gives x2 = 1 (mod 4) and n = 7 (mod 10). The transit is even by construction: the unpacked accumulator run is
  (1010)^R5.
- **Sizes.**
  - B3 >= 8 B5 + 6: B3 is U_(z+6) applied at least 3 times, and B5 = U_(z+5)^3(0).
  - 2 B5 >= 8 b_f + 55.
  - Together these give enough x-stack for every phase: w4 = 15 p3 - 66 p - 24 q - 73 >= 0.
- **No other residues.** No mod-11 facts and no counter induction are used.

This matches the independent verifier's chain (`bb10_fw1_verify.md`). Its W1 = 8B+59+2A''' is my n, and its
t' = (3 W1 + 14)/5 is my 6k + 13.

## How it was built

- **Explorer.** Machine-level lemmas come from the autoproof/mexp symbolic explorer (`bb10_fw1_coq/gen_m3.py`, specs
  in `parts.py`). Local changes to `mexp.py`:
  - more sub-rounds per loop (`MAXSUB = 40`);
  - positivity is passed on through splits;
  - lower-bound hypotheses for positive variables.
- **Waypoints.** S2 is split by hand into the unpack (S2A), the W-loop round (S2R) and the tail. The halting branch
  (H1, H2) was found from simulation: `cpp/hsim.exe` logs W-forms, and the n -> (units, zeros) map was fitted from it.
- **Stage 0.** A first attempt explored past the stage's end into the next clearing and could not finish.
  `st0g.py` instead stops the explorer at the first K-moment and uses that as the target. Stage 0 then generated in
  30 s.
- **`ST0K` fix.** The explorer's normal form of the stage-0 target rotates one zero token across the two zero runs:
  16 concrete zeros, then [101]^M [101×8]^b, then D5 missing its leading 101. `ST0K` bridges this with `zshift`,
  which permutes runs of the same block via `lpow_lpow` and `lpow_shift'`. `zshift5` states it on the D5 token
  directly. The first version (a `change` on an already-reduced term) failed; the fix compiled in 14 s.
- **Build chain.** All builds ran one coqc at a time at Idle priority (`batch_coqc.py`, `chain.sh`, `chain2.sh`):
  parts, glue, arith, init, st0, run, 1RB0RA, bound, vs_lead, vs_0LA, then check.py.
- **Priority slip.** One explorer run (the stage-0 tail generation) started at Normal priority before I noticed. It
  was lowered to Idle, and all scripts in `bb10_fw1_coq/` now set Idle priority themselves (`common.py`).

## Ranking

- M3 > 0LJ0LC lead and M3 > 0LA: both machine-checked.
- The verifier's ranking is n1 (f_(omega+1), now Coq-proved by bb8-ab) > M3 > 3-cycle sibling > M3J > 0LA.
- **Not done:** I made no M3-vs-3-cycle-sibling comparison. Per the lead, that would only be done against an
  existing bound file for the sibling, and I did not check whether one exists.
