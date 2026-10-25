# Make M8's Coq statement easy for an evaluator to check

Repo: `jeff87654/busy-beaver`. Work in `BB8/verify_m8/` only, on a branch, and open a PR. Do not modify
`BB9/verify_c04/` or `BB8/verify/` (renaming their logical paths would rebuild everything; that is a separate PR).

## Goal

An evaluator should be able to trust M8's results by reading two short files, `Defs.v` and `Statement.v`, plus
busycoq's own `TM.v`. Today they have to chase definitions across three directories and decode the path aliasing
(the C04 `lib/` and `../verify` are both mapped to the logical name `BB8`).

## Edits

1. **`Defs.v`** (new, about 60 lines, imports only busycoq and `M8.Individual82`). It holds everything the main
   statements mention:
   - `tm8`, `sym_val`, `count1`, `ones`. Move these out of `Tm8.v` and have `Tm8.v` `Require Export Defs`, so they
     are the same constants and no bridge is needed.
   - `iter`, `f`, `f_omega`, `f_w1`, `arrow`, as copies of `Abs.iter`, `Score.f`, `Score.f_omega`, `FArith.f_w1`
     and `Abs.arrow`.

2. **`Statement.v`** (new). Each main result is a `Theorem` whose type mentions only `Defs` and busycoq names
   (`halts`, `halted`, `c0`, `-[ ]->*`). Each one is proved from the existing `Transfer` and `Beats8` theorems plus
   bridge lemmas.
   - Bridge lemmas: `Defs.f k n = Score.f k n` and similar for the other copied definitions, stated pointwise. Try
     `reflexivity` first and fall back to induction. Do not use functional extensionality or any other axiom.
   - **Remove `Bx` from the statements.** Use `2 * Bx + 4 = arrow 13 2 3` (`FArith.Bx_knuth`) to state the bracket
     as `f_omega (f_omega (6 * arrow 13 2 3 + 2)) < N < f_omega (f_omega (6 * arrow 13 2 3 + 3))`. Since
     12·Bx + 26 = 6·(2·Bx + 4) + 2, the proof is `rewrite`/`lia` from `m8_fgh_bracket`.
   - Include `halts tm8 c0`, the bracket, the coarse `f_w1 3 < N < f_w1 4`, the existence of a halting
     configuration with `ones`, `12 * arrow 37 2 3 + 59 < N`, and the two comparisons (`m8_beats_champ35`,
     `m8_beats_fw2`), each with its full type written out.
   - `sigma_c04` can stay out of `Statement.v`. If it is kept, add a comment saying it is a pure arithmetic
     recursion that never references a machine, so `N = sigma_c04` is not trivial.

3. **Pin the other machines' tables in the same file.** The comparisons mention `BB8_champ35_1RB0RA.tm` and
   `BB9_fw2_1RB0RD.tm`. Add `eq_refl` and string-parser checks for both, as `probe.v` already does for `tm8`, so
   the evaluator doesn't need the other directories' probes.

4. **Probe.** Run `Print Assumptions` on every theorem in `Statement.v`. Also print `Defs.v`'s definitions and
   busycoq's `c0` and `tape0`, since `Print c0` alone shows only `(q0, tape0)`.

5. **Fix the doc claim.** `BB8/1RB0RA_..._0RG0RF_1RG---.md` (section 3.1) says the probe checks by `eq_refl` that
   `ones` is a copy of `BB8_champ35_bound.ones`. It doesn't, and it can't, because the two are over different `Sym`
   types. Replace the sentence with: the copies are textually identical (checked by diff), and `Tm8.ones` is
   printed in the probe.

6. **Bookkeeping.**
   - Add `Defs` and `Statement` to `compile_clean.sh`.
   - Update the expected count of "Closed under the global context" lines in `compile_clean.sh` and in the
     `bb8-m8` job of `.github/workflows/coq.yml`.
   - Regenerate `sha256.txt`.
   - Update the file tables in `verify_m8/README.md` and the M8 write-up, and add one line saying that
     `Defs.v` + `Statement.v` are the files to read.

## Constraints and acceptance

- No axioms. Every `Print Assumptions` must report "Closed under the global context".
- Keep all existing theorem names working, because the docs cite them.
- Build with `BUSYCOQ=… ./compile_clean.sh` if a compiled C04 tree and `../verify` are available. Otherwise the
  PR's `bb8-m8` CI job builds everything from scratch (about 2 hours); wait for it to pass.
- Done when CI is green and a reader can verify the claims from `Defs.v`, `Statement.v` and busycoq's `TM.v` alone.
