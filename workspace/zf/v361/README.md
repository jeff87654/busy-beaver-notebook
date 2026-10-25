# Verified 361-state "halts iff ZF is inconsistent" Turing machine

`A361.tm` (361 states, 2 symbols) is derived from Andrew Wade's 393-state `zf2.tm`. Wade's
framework is kept, and the program was optimized in `../reduce/` (see `../reduce/RESULTS.md`):
- the duplicated clauses are removed;
- each clause's parameter roles are permuted, chosen by search;
- the subroutines are rewritten (DET pops into a scratch register; the B6a test destroys its inputs;
  wff constructors tag by pairing directly; one shared pair/unpair instance; if_eq without a level-2
  break);
- the dispatch chain is capped at 7.

It searches **exactly the same formal system**. `coq/Logic.v` is byte-identical to `../coq/Logic.v`.

```coq
Theorem zf_machine : halts tm c0 <-> prov (Wel v0 v0).      (* coq/Main.v, closed *)
```

To check it, run `python check_zf.py` from this directory. It compares the literal table of
`A361.tm` with `coq/ZF2Dag.v`, builds the proof, and checks the theorem statement and its
assumptions. The trust surface and the proof structure are the same as for the 393-state machine;
see `../README.md`. A clean rebuild of all 20 files takes about 4 minutes.
