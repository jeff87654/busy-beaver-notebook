# zf/pagb — a 449-state Turing machine that halts iff PA proves Goldbach's conjecture

Headline (Coq 8.20, no axioms): `e2e/Headline.v`

```coq
Theorem pagb_halts_iff_PA_GC :
  PAGBT.ZFTM.ZFTM.halts PAGBT.ZFTM.tm PAGBT.ZFTM.ZFTM.c0 <-> @tprv _ _ falsity_on class PAeq GC_form.
Theorem GC_adequate rho : sat interp_nat rho GC_form <-> Goldbach_nat.
```

`PAeq`, `tprv`, `sat`, `interp_nat` are the Coq Library of Undecidability Proofs' own (vendored unmodified in
`vendor/`); `GC_form` (with `even`, `leq`, `Pr`) and `Goldbach_nat` are written out in Headline.v.

Check everything from scratch: `python -I check.py` (frozen machine sha256s; each layer's clean check;
Headline; coqchk on everything Headline depends on). About 25 minutes at idle priority.

**Axioms.** `Print Assumptions` (which tracks exactly what a theorem depends on) reports both headline
theorems "Closed under the global context". `coqchk` re-checks the whole environment in the kernel and
lists every axiom declared anywhere in a loaded library. Here that is three: `BusyCoq.LibTactics.inj_pair2`,
`Coq.Logic.ProofIrrelevance.proof_irrelevance` and `Coq.Logic.Eqdep.Eq_rect_eq.eq_rect_eq`. They come in
through busycoq's `TM.v` imports, which are left unmodified, and the headline theorems use none of them.
`check.py` accepts exactly these three in the coqchk output and fails on any other.

| dir | layer | main theorem |
|---|---|---|
| machine/ | the frozen machine (pa_wade.tm, source_pa.py, spec_pa.py; design in DESIGN.md) | — |
| tm/ | TM ↔ register-machine DAG (certified list-zipper simulation) | `MainTM.tmpa_rm` |
| prog/ | register-machine DAG ↔ abstract enumerator (structured semantics, occurs-check walk) | `MainPA.progpa` |
| coq/ | enumerator ↔ code calculus ↔ named Hilbert calculus ↔ library PAeq; Spec | `PA_Logic.enum_halts_iff_PA_GC` |
| e2e/ | composition, < 100 lines | `Headline.pagb_halts_iff_PA_GC` |
