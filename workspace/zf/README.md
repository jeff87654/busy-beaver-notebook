# A formally verified "halts iff ZF is inconsistent" Turing machine

This directory contains a Coq proof that Andrew Wade's 393-state, 2-symbol Turing machine
`ext/turing_machine_explorer/zf2.tm` halts, started on a blank tape, if and only if a
Hilbert-style formalization of ZF set theory (without regularity and choice) proves `v_0 e. v_0`.

```coq
Theorem zf_machine : halts tm c0 <-> prov (Wel v0 v0).      (* coq/Main.v *)
(* Print Assumptions zf_machine:  Closed under the global context *)
```

The machine is from codeberg.org/ajwade/turing_machine_explorer (Aug 2025). It is a port of Stefan
O'Rear's `zf2.nql` to Wade's own compiler. The bbchallenge wiki currently lists 432 states for it; the
repository version used here has 393. Rebuilding it from `zf2.py` with the axiom order given in the
README reproduces `zf2.tm` byte for byte.

## Checking it

```
cd zf
python check_zf.py
```

The script:
1. re-parses `zf2.tm` and checks that `zf2_table` in `coq/ZF2Dag.v` is exactly the file's
   transition table (785 rows, start state `0.boot.A`);
2. builds `coq/Main.v` with coqc 8.20, using busycoq's `verify/` as `BusyCoq`;
3. checks the theorem statement and that `Print Assumptions` reports no axioms.

## What a reviewer has to trust

* **busycoq's `TM.v`.** These are the standard definitions of `step`, `halts` and `c0` used by the
  BB(5) proof and in our earlier BB(9)/BB(10) proofs.
* **The machine.** `coq/ZFTM.v` builds `tm` from the program graph, and its theorem `tm_table` proves
  by computation that `tm` gives exactly the same transition as `zf2_table` for every state and
  symbol. That covers halting transitions too, so the table has no extra or missing rows.
  `check_zf.py` then ties `zf2_table` to the file.
* **The formal system.** Read `coq/Logic.v`: `prov` has the inference rules DET and GEN, the logical
  axioms B1–B4, B6a–c, B7 and B8a–c, and the ZF axioms EXT, REP (a schema), POW, UNI and INF. Compare
  them with the axiom list in the header of `ext/sorear-mtm/machines/2017-zf-sorear-748/zf2.nql`.
  Here `E.` and `/\` are abbreviations for `-. A. -.` and `-. ( -> -. )`.
* **The statement.** The machine halts iff `prov (v0 e. v0)`. That `v0 e. v0` is refutable, so that
  proving it means the system is inconsistent, and that ZF − Reg − AC is equiconsistent with ZF, are
  standard facts. They are argued on paper and not formalized.

## Proof structure (`coq/`)

| Layer | Files | Statement |
|---|---|---|
| TM ↔ register machine | ZFTM.v, SimBase/SimOps/SimRegs/SimIP/SimDag/SimBoot/Sim.v | `halts tm c0 <-> rm_halts zf2 ([], regs0)` |
| path ↔ big-step semantics | RM.v, RMEquiv.v | `wf p -> rm_halts p ([], R) <-> iter_halts p R`; `zf2_wf` |
| program ↔ abstract enumerator | ZF2Dag.v, ProgLib.v, Prog.v | one run of the program root = one `enum_step` |
| enumerator ↔ provability | Logic.v, Enum.v, L1_Prop/L1_Arith/L1.v | `enum_halts <-> prov (Wel v0 v0)` |
| assembly | MainGlue.v, Main.v | `zf_machine` |

The sections below summarize each layer.

**TM ↔ register machine.**
* Boot is a certified run of 39,773 steps.
* Each dispatch cycle (select, inc, decnz on nonzero and on zero, break, continue, halt) is proved
  once, generically, over symbolic register files.
* Wade's README notes that the framework never checks that the instruction pointer fits in front of
  the register file. Lemma `ip_space` proves that it always does. It checks the first 347
  register-machine steps by computation; after those, at least 131 decrements have run, and that
  margin covers the bound of 149 cells the pointer can ever need.
* The single missing row in the table (state `1.inc` reading 1) is shown to be unreachable.

**Program ↔ enumerator.**
* The 324-node graph is unfolded symbolically, with loops handled by induction.
* All 20 clauses are matched against the functional specification `Enum.enum_step`.
* No wff code is ever evaluated; the codes are astronomically large.

**Enumerator ↔ provability.**
* Soundness uses a decoder that is total on all numbers: every number decodes to some wff, and junk
  decodes to `v0 = v0`. The invariant is "every stack entry decodes to a theorem". This matters
  because the machine really does push numbers that are not codes of any wff.
* The proof derives `x = x` inside the Hilbert system.
* Completeness compiles any derivation into the machine's proof encoding.

Build everything with `python coq/build.py Main.v`.

`tools/` holds the Python simulators and generators, `DESIGN.md` the original design notes, and
`reduce/` and `framework/` the work on smaller machines.
