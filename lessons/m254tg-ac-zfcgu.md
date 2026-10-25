---
name: m254tg-ac-zfcgu
description: "zf/m254tg/ac — Con(ZF+GU) -> Con(ZFC+GU) via L + condensation, DONE 2026-10-14 (3.78k lines, CHECK PASS); headline tg296_halts_iff_ZFCGU"
metadata:
  node_type: memory
  type: project
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-15T01:40:59.226Z
---

zf/m254tg/ac proves acgu_reg_relcon : (ZFc+Reg+AC+GU) ⊢⊥ -> (ZFc+Reg+GU) ⊢⊥ (no axioms), wired into
e2e/E2E_TG.v as tg296_halts_iff_ZFCGU / ZFCRGU (296-state TM halts iff ZFC+GU inconsistent).

Route: GU^L with u = L_κ, κ = U∩On. Condensation without fine structure:
- Indexed Skolem hull H with dom ⊆ L_ζ ∈ U, which gives smallness without cardinal arithmetic.
- Z_refl.TV is reused, with tagged pieces and OP-tuples.
- Mostowski collapse by Z_trec along L-stages.
- Sg_upS on the collapsed set M plus uniqueness of L_a.

**Why:** 3.78k lines actual vs naive 3.2k, so here the ÷3 calibration was too low (see [[formalization-estimates-too-high]]).
Six Opus agents finished in about an hour of wall time.

**How to apply:**
- In this harness, Agent calls block until the agent finishes. Launch the parallel provers in ONE message.
- Agents end without a handback report, so check the files directly.
- A global `T1` definition in an agent file clashed with Z_ac.T1 downstream. Tell agents to use distinctive names.

Related: [[zf-ac-relcon]], [[m254-formalization]].
