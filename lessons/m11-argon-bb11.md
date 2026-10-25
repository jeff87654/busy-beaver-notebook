---
name: m11-argon-bb11
description: "Argon's 11-state M11 is NOT a BB(11) record; its title claim f_(w+1)(f_w(f_8 2)/3) is false (Coq-refuted 2026-10-16); lia/zify sealing pitfall"
metadata:
  node_type: memory
  type: project
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-17T03:24:52.973Z
---

M11 = 1RB1RA_1RI1RC_0LD1LG_0RE1LD_0LH1RF_1LK0RA_1RA0LH_1LG1LH_0LK0LJ_1LH1LI_---0LE (Gemini "Argon"; halting proof proofs/BB11_M11_halt.v).
Proved 2026-10-16 in proofs/BB11_M11_bound.v + BB11_M11_vs_n1.v (all Closed): the exact score, a unique halting count N with
f_w^3(5) < N and N+1 < F^15(9) <= f_(w+1)(30). So the title claim is false (`title_claim_false`), and n1 (10 states) beats it (`n1_beats_M11`).
Cause: the second drain's ~J2/3 blocks are left on the tape. The machine halts before another grow pass, so each block adds ones
but no f_w iteration. Related: [[bb10-n1-coq]], [[m13-argon-bb13]].

**Why:** Argon's claimed bounds can be wrong even when check.py passes, because the halting proof does not constrain the final r.
**How to apply:** for any Argon title claim, prove an upper bound as well before you accept a record.

Coq pitfall (new): `lia` (zify) matches atoms against its instances up to unfolding, and typeclass matching ignores `Opaque`.
So a transparent `Definition K1 := J1/3 - 1` with towers inside hangs lia even when it is declared Opaque.
Fix: seal each value as `Lemma x_sig : {y | y = body}. Proof. exact (exist _ _ eq_refl). Qed. Definition x := proj1_sig x_sig.`
Never seal with `proj1_sig (seal body)`: the conversion check still compares the arguments.
Also, `rewrite !arrow_0` loops or stops after one rewrite, because `2 * x` matches `arrow 0 ?a ?b` by conversion, so give the arguments explicitly.
