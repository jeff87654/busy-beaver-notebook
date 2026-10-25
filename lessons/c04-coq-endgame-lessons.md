---
name: c04-coq-endgame-lessons
description: Lessons from closing C04's Coq endgame: reuse generic per-J lemmas at small L, clean explore targets, capture exact halt/K-moment configs by single-stepping
metadata:
  type: feedback
---
Techniques that closed C04's casc_key + score in about 8 h (c04-coq2, 2026-10-18; see [[c04-bb9-candidate]]):
- Generic machine lemmas proved for ALL J (sub-steps, stop) also hold at small L. Route each key through one generic step to a COMMON small moment (keys 37/43/55 -> D0f(14), key 49 -> D0f(20)): 12 small prefixes instead of 18 big ones plus a bespoke key-55 route.
- mexp.explore accepts a target written in the CLEAN abstract shape (Kgx: near run (101)^(6p+c), then tokens) when the token order and the tail count are exactly right. That gives zero normalization glue (prog_eq + pow_add/pow_mul + reflexivity). Earlier "overshoot" failures were token-order and tail-count errors, not encoding.
- To find an exact target: single-step a CONCRETE config with planner8.step, detect the K-moment, then diff the runs while varying one parameter at a time (cap6.py / try_prefix2.py). For halts (explore raises Fail on a halt): hand-drive run_stuck+find_loop through the forced split, then shift a run by +1 so that the limit form is split-free.
- Lemma statements need the m-token exactly (D(1) vs D(0) bug); 0/1 inside nat lists need %nat under sym scope; CDP leaves `repeat O (S j) ++ []`.
- Keep other agents' dependencies frozen: put new invariants (finite far side) in NEW files (Fin.v regenerated from Step.v's proof text) and never recompile shared .vo.
**Why:** each of these unblocked a stall that cost hours. **How to apply:** in the next record formalization's endgame, look for the shared small-L moment first and write clean targets.
