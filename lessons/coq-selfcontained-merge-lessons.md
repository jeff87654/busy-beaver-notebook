---
name: coq-selfcontained-merge-lessons
description: How to merge busycoq-based multi-file Coq proofs into ONE self-contained .v (gen_selfcontained.py for BB9, gen_selfcontained_n1.py for BB10 n1) and the pitfalls met 2026-10-06/08
metadata:
  node_type: memory
  type: project
  originSessionId: 45e83fb6-f8fb-4d8b-a595-56f7c666ca5e
  modified: 2026-10-08T18:59:24.376Z
---

Generator: `bb8_list/proofs/selfcontained/gen_selfcontained.py` -> `BB9_record_1RB0RA_selfcontained.v` (1.19 MB; busycoq
core LibTactics/Helper/TM/Compute/Flip/Permute/Individual each wrapped in `Module BusyCoq_<File> ... End. Export`,
then BB92/Individual92, the record halting + bound files at top level, the champion's two files in `Module Champion9`,
the vs file with `BB9_champion_*.` -> `Champion9.`, a final section with `ones_agree`, `new_champion`,
`new_champion_margin` (3x), and all `Print Assumptions`). Check: plain `coqc FILE.v` in an empty directory, then
`probe_selfcontained.v`.

Pitfalls (each cost one failed compile; the mini test `mk_mini.py` = prelude + Champion9 + first 160 lines of the
record file catches all of them in ~80 s, the full build takes ~45 min):
1. `From Coq Require Coq.X.Y` double-prefixes: with full names use plain `Require`.
2. Import ORDER sets notation precedence: `From BusyCoq Require Export TM` must become an in-place `Export BusyCoq_TM`
   (not be dropped), else Bool's `&&` beats Helper's sumbool `&&` in Compute.v.
3. Scopes/options from one original file leak into the next (file-local `Local Open Scope nat_scope`, `Set Default
   Goal Selector "!"`): start every inlined file with `Local Open Scope sym_scope`; do not set the goal selector
   globally (LibTactics is written without it).
4. Fresh hypothesis names skip globals OF THE CURRENT LIBRARY only: a same-file constructor `H` shifts anonymous
   `pose proof` names from H,H0 to H0,H1 and breaks `destruct ... as [H1 H2]` (champion `Pv_par`). Fix: rename the
   constructor `St_H` and add `Notation H := St_H` (abbreviations are not globals for that check; patterns,
   `{{H}}>` notations and printing unchanged). Imported globals (other .vo) are never skipped, which is why the
   multi-file build never saw it.
5. Same root cause in new glue code: `Lemma f : forall L, ... Proof. induction L` took `L` = the `dir` constructor
   (same-library global) instead of introducing the binder; use binder names that are no globals (`xs`) and
   `intros` first. Test new glue in an environment that shadows A..I, L, R as same-library constructors
   (`sc_test/FinalSection2.v` pattern), it is stricter than the real file.
6. A probe that `Require Import`s the compiled single file must `Local Open Scope sym_scope` itself before writing
   `tm (A, 0)` (the scope is not exported the way `Individual92`'s is). PowerShell `*>` redirection writes UTF-16:
   `iconv -f UTF-16LE` before grepping a log.
BB(10) n1 (2026-10-08, `gen_selfcontained_n1.py` -> `BB10_n1_selfcontained.v`, 11 source files, modules
Champion10 / Lead10 / N1) added:
7. Any file defining a name equal to a state constructor (n1 and 0LJ0LC define `F`) cannot sit at top level next to
   BB102's `state`: wrap EVERY development in its own Module (a module-local `Definition F` is fine).
8. `Opaque` is not carried by Require/Import, but inside one file it persists across inlined parts (and ends at
   `End Module`; tested with `Print Strategy`). Generator emits `Transparent <earlier opaques>` at each file
   boundary inside a module (else e.g. `simpl` stops unfolding `arrow` in the next file).
9. Final glue must not convert different constants applied to huge arguments (T = arrow 37 2 3, sealed T_sig):
   restate with `Notation arrow := N1.arrow` abbreviations so statements match syntactically, and `rewrite T_def`
   / `replace N1.F with (fun ..)` rather than relying on conversion. Translate only `ones` (variable arguments).
10. Glue test in seconds: map module names back to the multi-file .vo names (mk_final_test.py in the session
   scratchpad) and compile against the existing build, with A..J, L, R shadowed.
11. Published copies may differ only by CRLF; Python read_text normalizes, so the output is identical.
12. Pitfall 4 is not specific to H: n1's `Lemma R1 : forall L t ts A, ... Proof. intros.` named the binders L0, A0
   because state A and TM's dir constructor L were same-library globals, then `PRO A ...` hit the state (first full
   build failed after 433 s). Fix in gen_selfcontained_n1.py: ALL states St_A..St_J and busycoq's `dir` as St_L,
   St_R behind abbreviations. Find candidates first: compile the prelude alone with `Locate x.` for binder names
   (collide.py / mk_prelude.py in the session scratchpad sc_n1/), and prefer renaming every constructor up front.
Mini test (prelude + Champion10 + Lead10 + first 160 lines of n1): 258 s, exit 0.
Result (BB9): build 3673 s on a loaded machine (two concurrent coqc jobs), probe 195 s; both exit 0 on 2026-10-06.

**Why:** the user asked for a self-contained proof file for the BB(9) record; a single file is what outsiders can
check with one `coqc` call.
**How to apply:** reuse the generator for other machines (change the file list); run the mini test before any
45-minute build; keep `Set Default Goal Selector` out of the top level. See [[bb8-champion-subtree-lead]].

- (2026-10-08, two agents independently) `Opaque U` / `Opaque arrow` set in one file is NOT carried by Require/Import: an importing file's fold/simpl then unfolds U and hangs. Restate `Opaque` in every importing file (and at each file boundary inside a merged self-contained file).
