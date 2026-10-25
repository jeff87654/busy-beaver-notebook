# SMFW — SM_SPEC deliverable B2 (tape-level primitives)

Hand-written 2-symbol TM fragments for the string-stack machine's primitives, on the exact tape
layout of `../SM_SPEC.md`, unit-tested against `../sm/sm_abstract.py`. Run everything with `python -I`.

* `codec.py`   abstract SM state <-> concrete tape (encode/decode); pins the layout (see LAYOUT.md).
* `sim.py`     minimal TM simulator with exit detection (`6.break.0/1`, `5.root`, halt).
* `harness.py` random valid-tape generators + `run_frag`.
* `run_tests.py` per-op random testing vs sm_abstract: `python -I run_tests.py [OP ...] [--n N]`
  (no OP => all). Hundreds of random cases + edge cases per primitive.
* `frag_*.tm`  the primitive fragments. `gen_check.py` generates `frag_check.tm`.
* `LAYOUT.md`  orientation, encoding, worked example, divergences.
* `COUNTS.md`  state counts per primitive, totals, protocol choices, status.

Verified: boot, INCC, DECC, NEWP, NEWT, APP1, PUSH v (v=3..11), CHECK, RB (adv/zero/END + N-rotation).
Not implemented (need the STEP-L/STEP-R shuttle engine): DUP k, DUPT, DET, COMMIT — see COUNTS.md.
