# Self-contained proof file for the BB(9) record machine

`BB9_record_1RB0RA_selfcontained.v` is ONE Coq file, depending only on the Coq standard library (Coq 8.20.1),
that proves for

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---

- `halt` : the machine halts from the blank tape;
- `score_closed` : the halting tape holds exactly `3 * arrow (12*Bx-9) 2 8 + 108 * (Bx/5) + 70` ones, with
  `2*Bx+4 = arrow 13 2 3` (`Bx_arrow13`); in Knuth arrows, with T = 2↑^13 3:
  sigma = 3·(2↑^(6T−33) 8) + (54T+26)/5;
- `sigma_lower_bound` : more than 2↑^(2↑^13 3) 3 ones (and `sigma_lower_bound_strong`: more than 2↑^(6T−33) 8);
- `Champion9.halt`, `Champion9.score_exact` : Jacobzheng's 2024 champion
  `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH` halts with exactly `Champion9.b2 + 3` ones;
- `new_champion` : both halt, the champion with Nc ones and ours with No ones, and `Nc + 1 < No`
  (standard scores: the champion's 1RZ writes a 1 on a 0, so its score is Nc + 1; ours reads a 1 at the undefined
  I1, so its score is No);
- `new_champion_margin` : `3 * (Nc + 1) < No`, so no convention about the final write matters.

## Check it

    coqc BB9_record_1RB0RA_selfcontained.v        # 3673 s measured on a busy laptop; the halting proof's machine-level lemmas
    coqc probe_selfcontained.v                    # optional, ~3 min, same directory

The first command must end with twelve lines `Closed under the global context` (one per `Print Assumptions`
at the end of the file); the only warnings are deprecation notices and LibTactics' `ltac_Mark` notice.
The probe makes Coq re-check, by conversion, every entry of both transition tables against the machine
strings, the exact types of the main theorems, and prints the definitions behind the statements
(`halts`, `halted`, `step`, `c0`, `ones`, `arrow`, `Bx`, `bp`, `U`, ...) plus `Print Assumptions` for each theorem.

Note on `grep Axiom`: the file contains exactly one `Axiom` declaration, `inj_pair2` in the inlined busycoq
`LibTactics` (verbatim from TLC's LibTactics; it backs the `inverts` tactic). None of the twelve theorems depends
on it, which is what the twelve `Closed under the global context` lines certify (`Print Assumptions` lists every
axiom a theorem's proof term uses). LibTactics also defines a `skip`/`demo` tactic notation on top of `admit`;
a proof using it cannot be closed with `Qed`, and the file has no `Admitted`.

## How the file is built

`python gen_selfcontained.py` assembles it (deterministically) from

| part | source |
| --- | --- |
| busycoq core: LibTactics, Helper, TM, Compute, Flip, Permute, Individual | `third_party/busycoq/verify` (commit bd2e36f, MIT; each file wrapped in `Module BusyCoq_<File> ... End. Export`) |
| 9-state instantiation | `proofs/BB92.v`, `proofs/Individual92.v` |
| halting proof | `proofs/BB9_record_1RB0RA.v` (top level) |
| exact score | `proofs/BB9_record_bound.v` (top level) |
| the 2024 champion: halting + exact score | `proofs/BB9_champion_1RB1RA.v`, `proofs/BB9_champion_bound.v` inside `Module Champion9` |
| comparison | `proofs/BB9_record_vs_champion.v` (`BB9_champion_*.` renamed `Champion9.`) |
| final section | written in the generator: `ones_agree` (the two `ones` predicates are convertible copies), `margin_core`, `new_champion`, `new_champion_margin`, `Print Assumptions` |

No proof text is changed. The generator hoists `Require` lines to the top (turning the import effect into an
in-place `Import`/`Export`, so that file-local imports such as Helper's `Import Nat` keep their scope and
notation precedence follows the original import order), strips `Print Assumptions` lines (collected at the end),
and starts every inlined file of ours with `Local Open Scope sym_scope` (the originals got the symbol scope on top
from `Individual92`'s `Open Scope`; in one file the previous part may have ended in `nat_scope`).
`Set Default Goal Selector "!"` is not set globally because LibTactics is written without it; every later part
sets it for itself, as the original files do.

The one textual change is in BB92: `Inductive state := A | B | C | D | E | F | G | St_H | I.` with
`Notation H := St_H.` Reason: when Coq invents a hypothesis name (anonymous `pose proof`, bare `intros`) it skips
the names of globals *of the current library*. In the multi-file build the constructor `H` came from another
`.vo`, so anonymous hypotheses were named `H, H0, ...`; in a single file `H` is local, the names shift to
`H0, H1, ...` and collide with explicit patterns such as `destruct ... as [H1 H2]` (first seen in the champion's
`Pv_par`). An abbreviation is not a global for that check, while patterns (`| H, 0 => ...`), the notations
`{{H}}>` and printing are unchanged (`Print tm` shows `H`).

The twin machine `..._0RH0RE_0LH---` (same run, same score; `proofs/BB9_record_twin_1RB0RA.v`) is not included.

## Verification record

`VERIFICATION.txt`, `sha256.txt`, `build.log` and `probe.log` are from the from-scratch compile of this exact file
(SHA-256 `41487fd2e1316a9d4a6ea939e7298f3644d4aeebdc8ca454941fa90b0886760d`) with plain `coqc` (no `-Q`, no other
`.vo` on the load path) in a directory containing nothing else, on 2026-10-06: exit 0, 3673 s, twelve
"Closed under the global context"; probe exit 0, 195 s, eight "Closed under the global context".  A second from-scratch compile on 2026-10-07 (6999 s, probe 172 s) gave the same result (build.log, probe.log). Details in
`../../investigations/bb9_record_1RB0RA_1LI0LC_coq.md`, section 5a.
