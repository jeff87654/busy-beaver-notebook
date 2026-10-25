# BB(7) 20-Digit Tripling Champion (`champ_231` / `champ_232`) — Coq Proofs

## Overview

This directory contains the generator and verification probe for the machine-checked Coq halting and score lower-bound proofs of the 7-state 2-symbol record machines discovered in the `triage7` holdout census (`bb8_list/investigations/bb9_triage7_and_1RB1LA/REPORT.txt`):

- **`champ_231`**: `1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB` (`G0 = 0LD`)
  - Proof file: [`bb8_list/proofs/BB7_champ20_1RB0RG.v`](../../proofs/BB7_champ20_1RB0RG.v)
- **`champ_232`**: `1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB` (`G0 = 1LC`)
  - Proof file: [`bb8_list/proofs/BB7_champ20_1RB0RG_G0_1LC.v`](../../proofs/BB7_champ20_1RB0RG_G0_1LC.v)
- **Score & Lower Bound Proof**:
  - Proof file: [`bb8_list/proofs/BB7_champ20_bound.v`](../../proofs/BB7_champ20_bound.v)

All three files compile with `build.py` under Coq 8.20 (`busycoq` framework) with **zero axioms** (`Closed under the global context`), and both halting files pass `check.py`.

## Canonical Two-Counter Digit Representation

We represent the 20-digit right-tape array together with both active counters $a, b \ge 0$ in a single canonical family:
$$\texttt{Kd}\; ds\; a\; b \;:=\; \texttt{0}^\infty \;<\{\!\!\{\texttt{E}\}\!\!\} (\texttt{1} \gg \texttt{[1; 1]}^b *\!> \texttt{0} \gg \texttt{0} \gg \texttt{[1; 1]}^a *\!> \texttt{0} \gg \texttt{0} \gg \texttt{rgt}\; ds)$$
where $\texttt{rgt}\; [] = \texttt{1} \gg \texttt{1} \gg \texttt{0}^\infty$ and $\texttt{rgt}\; (y :: t) = \texttt{[1; 1]}^y *\!> \texttt{0} \gg \texttt{0} \gg \texttt{rgt}\; t$.

With this representation, all 10 low-level phases (`R1`, `R2`, `ENTRY`, `LOOP`, `FINAL`, `R4A`, `GLOOP`, `GHALT`, `SROUND`, `INITA`) are pure 1-level crossing stages with **0 nested loops**, yielding three K-level rewrite rules and the halting rule:
1. **`KR1`**: $\texttt{Kd}\; ds\; (S a)\; b \longrightarrow^+ \texttt{Kd}\; ds\; a\; (b + 3)$
2. **`KR2`**: $\texttt{Kd}\; (S y :: t)\; 0\; b \longrightarrow^+ \texttt{Kd}\; (y :: t)\; (b + 3)\; 0$
3. **`KR3`**: $\texttt{Kd}\; (\texttt{repeat } 0\; (S m) \mathbin{++} S y :: t)\; 0\; (S m + s) \longrightarrow^+ \texttt{Kd}\; (\texttt{repeat } 1\; m \mathbin{++} S (S (S s)) :: y :: t)\; 1\; 0$
4. **`KR4x`**: $\texttt{Kd}\; (\texttt{repeat } 0\; k)\; 0\; (k + s) \longrightarrow^* \texttt{c\_end}\; k\; s$, which is halted at `C1 = None` with $2k + 2s + 7 = 2b + 7$ ones on the tape.

## Clearing Recurrence and Main Theorems

- $\texttt{U}\; 0\; x = 3x + 9$, $\texttt{X}\; 0 = 3$
- $\texttt{U}\; (S j)\; x = \texttt{Nat.iter}\; (x - j + 2)\; (\texttt{U}\; j)\; (\texttt{X}\; j)$, $\texttt{X}\; (S j) = \texttt{U}\; j\; (\texttt{X}\; j)$
- $\texttt{bf} = \texttt{Yb}\; 0\; 20\; 5 = \texttt{U}\; 19\; (\texttt{U}\; 18\; (\cdots (\texttt{U}\; 0\; 5)\cdots))$, $\texttt{af} = \texttt{bf} / 3$

Both `champ_231` (at step 3,715) and `champ_232` (at step 3,775) reach $\texttt{Kd}\; (\texttt{repeat } 1\; 20)\; 1\; 2 \longrightarrow^+ \texttt{Kd}\; (\texttt{repeat } 1\; 20)\; 0\; 5$, which reduces to $\texttt{Kd}\; (\texttt{repeat } 0\; 20)\; 0\; \texttt{bf}$ and halts at $\texttt{c\_end}\; 20\; (\texttt{bf} - 20)$.

Machine-checked theorems in `BB7_champ20_bound.v`:
- `score_exact`: $\exists c,\; c_0 \longrightarrow^* c \land \texttt{halted}\; \texttt{tm}\; c \land \texttt{ones}\; c\; (2 \cdot \texttt{bf} + 7)$
- `score_exact_af`: $\exists c,\; c_0 \longrightarrow^* c \land \texttt{halted}\; \texttt{tm}\; c \land \texttt{ones}\; c\; (6 \cdot \texttt{af} + 7)$
- `sigma_lower_bound`: $\exists c\; N,\; c_0 \longrightarrow^* c \land \texttt{halted}\; \texttt{tm}\; c \land \texttt{ones}\; c\; N \land \texttt{arrow}\; 20\; 3\; 2 < N$
- `sigma_lower_bound_strong`: $\exists c\; N,\; c_0 \longrightarrow^* c \land \texttt{halted}\; \texttt{tm}\; c \land \texttt{ones}\; c\; N \land \texttt{arrow}\; 20\; 3\; 3 < N$
- `beats_prev_bb7_champ`: $\exists c\; N,\; c_0 \longrightarrow^* c \land \texttt{halted}\; \texttt{tm}\; c \land \texttt{ones}\; c\; N \land 3 \cdot \texttt{arrow}\; 13\; 2\; 3 + 22 < N$
- `score_exact_G0_1LC` & `sigma_lower_bound_G0_1LC`: identical exact score and $\texttt{arrow}\; 20\; 3\; 2 < N$ lower bound for `champ_232`.
