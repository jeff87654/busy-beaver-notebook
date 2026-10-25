# Verified 354-state "halts iff ZF is inconsistent" Turing machine

`B354.tm` has 354 states and 2 symbols. It is A361 (see `../v361/README.md`) with one further change
from `../reduce/`: equivalent rewrites of three ZF axioms inside the program. EXT and REP have `/\`,
`<->` and `=` commuted, and INF has its variables renamed. Wade's framework is kept.

The trusted formal system is **unchanged**: `coq/Logic.v` is byte-identical to `../coq/Logic.v`.
`coq/L1_B354.v` proves in pure first-order logic that each rewritten axiom and its original are
interderivable (for INF, via universal closures). `coq/L1.v` uses this in both directions:
- soundness: the machine only pushes theorems of the original system;
- completeness: each original axiom is rebuilt from its variant by a short machine proof.

```coq
Theorem zf_machine : halts tm c0 <-> prov (Wel v0 v0).      (* coq/Main.v, closed *)
```

To check it, run `python check_zf.py` from this directory. A clean rebuild of all 24 files takes
about 5 minutes.
