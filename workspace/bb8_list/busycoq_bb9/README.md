# BB(9) champion proofs in busycoq standard form

Machine: `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH`, found by Jacobzheng.

`verify/` contains files that drop into upstream `busycoq/verify/` as they are. They use only the logical path `BusyCoq`:

| file | content |
|---|---|
| `BB92.v` | `BB52.v` with 9 states (`A`..`I`); nothing else changed |
| `Individual92.v` | `Individual52.v` with 9 states; it starts with `From BusyCoq Require Export Individual BB92.` |
| `BB9_champion.v` | `Theorem halt : halts tm c0.` |
| `BB9_champion_bound.v` | `score_exact`, `sigma_lower_bound_strong`, and `sigma_lower_bound : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ f_omega (f 9 2) < N + 1` |

`0001-Verify-the-BB-9-champion-halts-with-a-lower-bound-on.patch` is a `git format-patch` against busycoq
`bd2e36f`. It adds the four files, appends them to `ALLVFILES` in `verify/Makefile`, and adds an entry to the
"Individual machines" list in the README. To apply it:

    git am 0001-Verify-the-BB-9-champion-halts-with-a-lower-bound-on.patch

Verified on 2026-10-03:
- the patch applies cleanly to a fresh clone;
- the files compile with Coq 8.20 (`coqc -Q . BusyCoq`);
- `Print Assumptions` reports "Closed under the global context" for `halt`, `sigma_lower_bound`,
  `sigma_lower_bound_strong` and `score_exact`;
- the printed `tm` matches the machine string.

Score convention: busycoq stops before the final `1RZ` write, so the score is `N + 1`.

The working copies under `../proofs/` (BB8 logical path) are unchanged.
