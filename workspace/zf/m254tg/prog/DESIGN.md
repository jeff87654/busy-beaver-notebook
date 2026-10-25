# m254tg: program layer (L2)

Proved with no axioms (`Print Assumptions` reports "Closed under the global context"):

```coq
Theorem progtg      : rm_halts dagtg ([], regs0) <-> enum_tg_halts.     (* coq/MainTG.v *)
Theorem progtg_iter : iter_halts dagtg regs0 <-> enum_tg_halts.
```

* `dagtg` (`M254TGT.DagTG`, the TM layer's frozen file in ../tm/coq) is the decision DAG of the frozen
  `../machine/m254tg_wade.tm`. `tools/gen_coq.py` regenerates it from the machine and checks that the
  node table matches.
  * It has 234 nodes.
  * It is numbered like `zf/tools/gen_coq_dag.py`: names are sorted and `main().0` = node 0.
  * Registers are in declaration order: nextproof 0, topwff 1, wffstack 2, axiomcode 3, param1 4,
    param2 5, scratch1 6, scratch2 7, prooflist 8.
* `rm_halts`, `regs0` and `iter_halts` come from `M254TGT.RM` (zf/v336/coq/RM.v verbatim). `dagtg_wf`
  comes from `M254TGT.RMEquiv`. L3 proves `M254TGT.MainTM.tmtg_rm : halts tm c0 <-> rm_halts dagtg ([], regs0)`.
* `enum_tg_halts` is the frozen enumerator `../logic/coq/EnumTG.v`, started from s0 = all zeros. So
  `regs0` encodes s0 directly; there is no boot offset, unlike zf/m254, whose R0 was nextproof = 2.

Check: `python -I check.py` (about 1 min). It verifies the TM sha256, cross-checks
../tm/coq/DagTG.v against the machine, regenerates the ProgLibTG.v regions byte-identically, scans for keywords, rebuilds from clean, and checks that the
assumptions are closed. `../logic/coq`, `../tm/coq` and `zf/m254/logic/coq` must already be built
by their owners. Don't build while `../tm/check_tm.py` is running: it deletes and rebuilds those .vo
files.

## How it was obtained

Port of zf/m254/prog (L2 for the original 254 program), without its p254 bisimulation, since the TM
layer here runs the Wade DAG itself.

* Outside `axioms()`/`main()`, every node of the old 219-node DAG has a structurally identical node in
  the new DAG (hash-consed comparison).
* `tools/port.py` renumbered ProgLib254/L2Root254 into ProgLibTG/L2RootTG: `ENode k`, lemma names
  with node suffixes, and comments.
* `tools/gen_prog.py` regenerates the 20 increment-only loops and the 47 atoms. The output equals the
  ported text.
* `ax1`, the symbolic run of all of `axioms()`, needed no change. Its conclusion is stated through
  `EnumTG.gate`/`CodesTG.bundle`, so Coq checks that the compiled AX code builds exactly the UG' bundle
  of CodesTG, for symbolic a, b, c.

| file | content |
|---|---|
| coq/ProgLibTG.v | structured semantics on dagtg: node rules, loops, pair/unpair/if_eq, stack subroutines |
| coq/L2RootTG.v | `root_sem` (one root run = one `enum_step`), `iter_halts_dag` |
| coq/MainTG.v | `progtg`, `progtg_iter` |
