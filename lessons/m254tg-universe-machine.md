---
name: m254tg-universe-machine
description: "Project (started 2026-10-14): TG-strength TM (halts iff ZF + Grothendieck universes inconsistent) built on the 254 machine; UG schema design, agents, workspace zf/m254tg"
metadata:
  node_type: memory
  type: project
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-14T18:36:06.631Z
---

Started 2026-10-14. This came out of a Discord thread about building a "HoTT is inconsistent" machine. The user chose a set-theory target instead: ZF + GU ("every set lies in a Grothendieck universe", TG strength), with HoTT following from the published simplicial-model papers (Kapulkin–Lumsdaine, Lumsdaine–Shulman), cited but not formalized. They also decided against writing their own HoTT spec. logrel-coq was checked and works as a spec, but it has only one universe.

Plan: use the 254 machine as the base (see [[m254-formalization]]). Fall back to the 335 machine ([[zf-machine-verification]]) if the 254 base proves intractable.

Key facts:
- The author's 254-specific backend is unavailable: github Mira-Cult/turing-machines returns 404, and the PA245_ZFC261 zip is not in drive_mike.
- So we compile with Wade's TMBuilder. The 254 source compiles to a 281-state table, and L2 was already proved on its 219-node DAG.
- The axiom design replaces the bundle's C ∧ G' with a merged schema UG_φ. For each φ: every p lies in a transitive, power-closed w; for every B ∈ w there is a GIC-style collecting set C; and if all witnesses can be found in w, then C ∈ w.
- One instance (φ = pair membership in a parameter R) makes w a Grothendieck universe.
- Soundness of UG needs ranks in V (or L plus condensation). Completeness is a quotient-universe argument that mirrors the existing S_ax power/replacement proofs.

Agents (Opus), workspace zf/m254tg/:
- m254tg-machine: RPN design, state count against the 281 baseline, validation, and a 335-route cost comparison.
- m254tg-settheory: Gru transliterated from set.mm df-gru; `SUIR ⊢ ⊥ <-> ZFc + GU ⊢ ⊥`; scoping, then build.

**Why:** a TG machine yields BB independence from HoTT + LEM + AC, and it also dominates our ZFC machine.
**How to apply:** don't modify zf/m254 (frozen). The UG formula is the fixed interface between the two agents.

**Interface fix, 2026-10-14 (from the settheory agent's analysis):**
- The first UG design was ZF-provable. Its parameters were fixed before w, so reflection makes "C∈w" free.
- It also lacked union closure (counterexample: a singular strong limit).
- New interface UG': bind f right after w (φ slots: $0 = a, $1 = y, $2 = f) and conclude ∃U∈w ⊇ ∪C. The variant "C∈w plus a per-x union container" is also allowed.
- Lesson: for large-cardinal axioms in schema form, put the relation quantifier AFTER the universe quantifier. Otherwise reflection trivializes the axiom.
- Soundness route: relativize to M = ∃α x∈V_α. IR then holds by induction on stages, so no Reg, regcon or condensation is needed, and the headline is literally ZFc + GU.
- 335-route comparison (2026-10-14, a machine sub-agent; files zf/m254tg/machine/z335gu/):
  - UREP replaces REPsb0. The relation v5 is quantified after the universe w=v4, and the hypothesis is image-bounded.
  - Results: 364 states (+29), or 351 with INF dropped (INF derivable via w).
  - Soundness and completeness are argued only informally. Baseline to beat: the 254-route Wade-compiled 281+Δ.
- Machine layout approved 2026-10-14: variant A, f = label 0, d = c+1 = w, 296 states (Wade TMBuilder; old flawed UG gave 288, baseline 281). Variant B (C∈w + per-x union container) = 300. Pending: final validation, logic layer (bridge + collision lemmas), TM/prog layers.
- GU_reg_relcon (T_GUR ⊢ ⊥ -> T_GU ⊢ ⊥) proved closed in settheory/SU_reg.v (430 lines).
- 296-state m254tg_wade.tm FROZEN 2026-10-14 (validate 20000 + compiler.py contracts, 0 mismatches). Layer assignments:
  - m254tg-machine: logic port to zf/m254tg/logic/coq (enum_tg_halts <-> SUIR' ⊢ ⊥).
  - m254tg-prog: L2 on the Wade DAG, reusing zf/m254/prog.
  - m254tg-tm: L3 from the Wade-framework 335/393 Sim, NOT zf/m254/tm (that one is for the author's backend).
  - m254tg-settheory: SUIR' <-> ZFc+GU.
- Layer results (2026-10-14):
  - L2 done: zf/m254tg/prog check.py PASS, progtg : rm_halts dagtg ([], regs0) <-> enum_tg_halts, 234-node DAG.
  - L3 done: zf/m254tg/tm check_tm.py PASS, tmtg_rm : halts tm c0 <-> rm_halts dagtg ([], regs0). It is a constants-only port of the R3s336 Sim (9 registers); crosscheck 60M steps, 0 mismatches.
  - The Coq root clash M254TG (settheory vs tm) is being renamed: tm becomes M254TGT.
  - Remaining: logic port (m254tg-machine) and settheory.
- Settheory DONE 2026-10-14 (~2,060 lines, zf/m254tg/settheory build.py CHECK PASS):
  - Theorems: SU_equicons : SUIR ⊢ ⊥ <-> ZFc+GU ⊢ ⊥, plus _R (with Reg) and SU0_equicons.
  - Gru is transliterated from set.mm df-gru; the lead checked its dB indices.
  - Proof routes: soundness via ⋃V_α with w = V_κ; completeness via one UG' instance giving Gru0 -> Gru.
  - Next: settheory agent builds e2e/ (tg296_halts_iff_ZFGU) once the logic port lands. AC (condensation) not started.
- Logic layer DONE 2026-10-14:
  - zf/m254tg/logic/coq (root M254TGL, 1,785 lines): enum_tg_SUIR, plus enum_tg_GU/_GUR, all closed.
  - The collision classes are handled in SoundBWTG.
  - All four layers are closed. The settheory agent is now running the top-level zf/m254tg/check.py (e2e/E2E_TG.v: tg296_halts_iff_ZFGU / _ZFRGU).
- !!! DONE 2026-10-14: the lead ran zf/m254tg/check.py from scratch with all agents idle, and it gave CHECK PASS (exit 0).
  - E2E_TG.v proves tg296_halts_iff_ZFGU : halts tm c0 <-> ZFc + GU ⊢TC ⊥ and _ZFRGU (with Reg). Both are closed, with no axioms.
  - Total time was about 3.5h from the user's go-ahead.
  - Not done: AC (needs condensation), and the HoTT link, which is a citation only.
  - Not yet in the repo, and not announced.
- ZFC retarget (user, 2026-10-14). The HoTT step stays a citation (a formal statement would need self-written defs).
  - Chain: ZFc+AC+GU ⊢⊥ -> ZFc+Reg+GU ⊢⊥ via zfc's L.
  - It needs the new lemma (GU)^L in ZF+Reg+GU. The witness is u = L_κ (κ = height of a V-universe), and proving it needs condensation (L ∩ U = L_κ). No cheaper route is known: other choices of λ need a Mahlo-type closure.
  - Agent m254tg-ac is working in zf/m254tg/ac.
  - Fallback: a raw well-ordering axiom in the machine (est. +15-25 states, with quotient AC derived via least ≈-class reps).
- !!! ZFC DONE (2026-10-15):
  - zf/m254tg/ac (root M254TGA, ~3.8k lines): condensation via a TV hull with canonical witnesses (Z_wo well-order of L) plus a Mostowski collapse, giving GU^L with u = L_κ.
  - Lead ran check.py from scratch: CHECK PASS, exit 0.
  - E2E_TG proves tg296_halts_iff_ZFCGU and _ZFCRGU (ax_ac = zfc's Z_wo.ax_ac), plus the ZFGU/ZFRGU versions; all closed, no axioms.
  - Took ~ one evening with parallel Opus fillers (estimate was "about a day").
- Publishing (user OK 2026-10-15):
  - Agent tg296-package builds ZF/tg296 in the busy-beaver clone (C:\Users\jeffr\Downloads\busy-beaver), branch zf-tg296, modelled on ZF/m254 (PR #16), with CI job zf-tg296.
  - The lead commits, pushes, opens the PR, and merges after CI is green (standing permission).
- PR #19 opened 2026-10-15 (branch zf-tg296, commit 923f561). It adds ZF/tg296 and the CI job zf-tg296.
  - The local clean check passed (52 min).
  - The published .tm is LF, sha e9b63d8e…; the dev copy was CRLF, sha 1b89758c….
  - Merge after CI is green.
- !!! PUBLISHED 2026-10-16: PR #19 merged as ec9ed4f. All 26 CI checks passed; zf-tg296 took ~32 min.
