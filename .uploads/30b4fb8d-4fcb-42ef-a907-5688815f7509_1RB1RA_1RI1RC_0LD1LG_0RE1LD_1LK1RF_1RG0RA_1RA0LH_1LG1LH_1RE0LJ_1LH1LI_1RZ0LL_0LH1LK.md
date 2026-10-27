# M12: a 12-state machine at level f_(ω+2)

    1RB1RA_1RI1RC_0LD1LG_0RE1LD_1LK1RF_1RG0RA_1RA0LH_1LG1LH_1RE0LJ_1LH1LI_1RZ0LL_0LH1LK

|   | 0   | 1   |                 |
|---|-----|-----|-----------------|
| A | 1RB | 1RA |                 |
| B | 1RI | 1RC |                 |
| C | 0LD | 1LG |                 |
| D | 0RE | 1LD |                 |
| E | 1LK | 1RF |                 |
| F | 1RG | 0RA |                 |
| G | 1RA | 0LH |                 |
| H | 1LG | 1LH |                 |
| I | 1RE | 0LJ |                 |
| J | 1LH | 1LI |                 |
| K | 1RZ | 0LL | K0 is the halt  |
| L | 0LH | 1LK |                 |

## Main facts

| | |
|---|---|
| Halts | **Yes**, machine-checked (Coq, no axioms): `BB12_M12.halt`. |
| Exact score | Machine-checked formula: N = p + b/2 + 3 ones at the halt, where (p, b) = `pb2` is given by the recursion of section 2 (`score_exact`). The halt K0 = `1RZ` is read on a 0, so σ = N + 1. Not evaluated as a number. |
| Level | Machine-checked, with the standard fast-growing hierarchy: f_(ω+2)(f_(ω+1)(f_(ω+1)(3))) < σ (`sigma_lower_bound_m12`). |
| T12a (previous BB(12) entry) | Beaten, on paper: T12a is f_(ω+1)(f_(ω+1)(·))-class, M12 is f_(ω+2)-class. Not in Coq (T12a has no proved upper bound). |
| M13 (BB(13) entry) | M12's proved lower bound exceeds M13's proved lower bound f_(ω+2)(f_ω(20)). M13 has no proved upper bound, so M12 is not shown to beat M13. |
| Steps | Not computed. |

## 1. How it works

Tapes are written left to right; `X>` / `<X` is the head in state X facing right / left. All rules below are lemmas
of `BB12_M12.v` (names in brackets).

Configurations:

| Coq | tape |
|---|---|
| `Ca j b z` | `0^∞ (10)^j 1^b A> 0 z` |
| `Ch j b z` | `0^∞ (10)^j <H 1^(b+1) 0 z` |
| `Ce p a c d` | `0^∞ (10)^p 1^(a+2) I> (10)^c 0 (10)^d 0^∞` |
| `Cd p b d` | `0^∞ (10)^p 1^(b+2) I> (10)^d 0^∞` |

The inner engine is a finite-level hierarchy W, with W_0(b) = b + 3 and W_(j+1)(b) = W_j^(b+1)(2), so W_j grows
like f_j. States A, D, G, H run it: `Ch j b z →+ Ca j (W_j(b)) z` [`CH_CA`], and each block 1^(a+1) 0 to the right
is absorbed as `Ca j b (1^(a+1) 0 z) →+ Ca (j+1) (W_j^a(b)) z` [`BLK_iter_aux`].

The outer level is driven from state I by two counters to the right of the head, c and d:

- `Ce (p+1) (2k) (c+1) d →+ Ce (p+k+1) (W_p(1)) c d` [`CE_EVEN`]: one c-token moves half of the accumulator
  into the level p and refills the accumulator with W_p(1).
- `Cd (p+1) (2m+1) (d+1) →+ Ce p (W_p(3)) m d` [`C_REL`]: one d-token turns half the accumulator into c-tokens.
- `Ce p a 0 (d+2) →+ Cd p (W_p(a+4)) d` [`D_STEP`]: two d-tokens close the round with one more W_p.
- `Ce (p+1) (2k) 0 0 →+ Cd p (W_p(0)) (k+2)` [`D_REL`]: with no tokens left, half the accumulator becomes d-tokens.
- `Cd p (2m+1) 0 →+` halt in K reading 0, with p + m + 3 ones on the tape [`HALT_step`].

## 2. The run

From the blank tape, 352 steps reach `Ce 8 4 0 0` [`init_352`]. On pairs (p, a):

- Kc(p, a) = (p + a/2, W_(p−1)(1)) is one `CE_EVEN`. Each application raises the level p by half the previous
  accumulator W_(p−1)(1), so it acts like f_ω.
- Kc_full(p, b) = Kc^(b/2)(p − 1, W_(p−1)(3)) is one `C_REL` followed by its b/2 c-tokens: level f_(ω+1).
- Kd_step(p, b) = (p', W_(p')(a' + 4)) where (p', a') = Kc_full(p, b): one `C_REL` + one `D_STEP`, three d-tokens.
  Iterating it is level f_(ω+2).
- D_reload(p, a) = (p − 1, W_(p−1)(0)) is `D_REL`.

Round 1: `Ce 8 4 0 0` →`D_REL`→ `Cd 7 W_7(0) 4`, then one Kd_step and one Kc_full, giving pa1 = (p₁, a₁) with no
tokens left (`run_pa1`; a₁ is even and a₁ ≡ 2 mod 6). Round 2: `D_REL` turns a₁ into a₁/2 + 2 = 3(a₁/6 + 1)
d-tokens, and Kd_step runs a₁/6 + 1 times (pb2 = Kd_step^(a₁/6+1)(D_reload pa1)). The accumulator is then odd
and the machine halts [`run_round2`, `run_pb2`].

So σ = p + b/2 + 4 for (p, b) = pb2. Round 1 already bounds pa1 below by f_(ω+1)(f_(ω+1)(3)) (`pa1_dom` in
`BB12_M12_bound.v`). Round 2 then applies an f_(ω+2)-level iteration a₁/6 + 1 times, which gives
`sigma_lower_bound_m12`.

## 3. Verification

[`verify_m12/`](verify_m12/): busycoq `bd2e36f`, Coq 8.20.1, from-scratch build 35 s, built in CI (job
`bb13-bb14`). `probe.v` re-checks the transition table entry by entry against the string above and confirms that
`halt`, `score_exact`, `sigma_lower_bound_strong` and `sigma_lower_bound_m12` are closed under the global context.

## 4. Relation to other entries

M12 shares its A–D, G and H rows (the W engine) with M14 ([`../BB14/`](../BB14/)), whose proved lower bound
f_(ω+2)(f_(ω+2)(f_(ω+2)(15))) is larger. M12 replaces T12a ([`README.md`](README.md)) as the BB(12) entry.

## Credit

Found and proved in Coq by Argon (a Google Gemini model run by the repository owner in Google's Antigravity),
2026-10-26. The proofs were re-checked here (busycoq `check.py`, `Print Assumptions`, the probe), and the heading of
`BB12_M12.v` was corrected to match the proved bound.
