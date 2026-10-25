---
name: formalization-estimates-too-high
description: "My Coq formalization effort estimates run 3-10x too high; calibrate down and don't let them gate decisions"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-11T02:02:30.670Z
---

The user noted (2026-10-11): "you always underestimate your skill and speed when it comes to formalization."
Evidence the same day: std-ZF retarget estimated 8-10k lines / several days -> done in ~2h; infinity equivalence
estimated 3.5-5k lines -> ~1.2k lines in 40 min; regularity relative consistency ("hard", "chapter of Kunen")
-> ~1.3k lines in a few hours; A361/B354 ports ~1h each.

**Why:** pessimistic estimates nearly talked the user out of worthwhile proofs (regularity relcon).
**How to apply:** when sizing a Coq/busycoq formalization with agents, divide the naive estimate by ~3-5, say so,
and recommend attempting rather than skipping when the payoff is real; still report scoping risks honestly.
Related: [[zf-machine-verification]].
