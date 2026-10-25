---
name: m254gb-goldbach-machine
description: "Project started 2026-10-24: TM halting iff PA ⊢ Goldbach (user switched from ZFC to PA); native PA proof-search machine, workspace zf/pagb, agents pagb-machine + pagb-coq"
metadata:
  node_type: memory
  type: project
  originSessionId: 205a0b68-c138-46ef-afb2-3059e16fcd57
  modified: 2026-10-24T22:11:27.816Z
---

Started 2026-10-24.
- First plan: ZFC ⊢ GC, via the 254 bundle ∧ NG (zf/m254gb, phase 1 stopped early).
- The user then switched to **PA ⊢ GC**: "cleaner statement and probably easier to audit".

Key finding: the third-party PA238 machine (drive_mike/PA238_*) does NOT search PA proofs. Its theory is a bit-coded nonextensional set theory (filtered adjunction + full separation) that is only equiconsistent with PA. That cannot give "halts iff PA ⊢ GC" without a formal bi-interpretation, which would be heavy. So we build a native PA proof-search machine: the calculus works over 0/S/+/×/=, with Q + an induction schema + the closed axiom NG; it halts on ⊥. The headline uses the library's PA and a textbook GC formula, with an adequacy lemma over the nat model.

Agents (Opus, launched 2026-10-24):
- pagb-machine (zf/pagb/machine): calculus choice (A = functional terms in Tarski–Megill style, B = relational PA), state counts vs the ZFC 281 baseline, a positive control.
- pagb-coq (zf/pagb/coq): Spec.v with GC_form, the adequacy proof and the deduction bridge; cost scoping of A vs B; then a logic-layer skeleton.

**Why:** a new user-requested headline machine.
**How to apply:** don't touch the frozen zf/m254*, v335 and v336 directories. The two agents agree on the calculus between themselves, with Coq cost weighing in.

Progress 2026-10-24:
- pagb-coq: Spec.v closed (coqchk: no axioms). GC_form textbook formula, GC_adequate over the nat model, PA_GC_refutation. The target is the library's PAeq (bare PA has no equality axioms). Soundness is closed (PA_Sound.v: pprov {NG} ⊥ → PAeq ⊢TC GC_form). Completeness is next.
- pagb-machine: the FLAT calculus is committed. Nested terms are impossible in the 4-tag coding (no variable-term constructor). 346 states vs ZFC 281 (PA without NG ≈ 300; NG ≈ 47). A single VAC schema φ→∀cφ replaced five per-atom vacuity rows. Validation 0 mismatches. The positive control (S0=0) halts in 103 steps.
- Inter-agent messages misrouted (pagb-coq thought m254gb-machine was the designer); the lead relays between them.
- m254gb-machine is measuring the ZFC route, for comparison only.
- 345 FLAT machine WITHDRAWN (not frozen). Its single VAC φ→∀cφ only covers c=code(φ), and completeness needs A→∀xA for every x∉A. The design is switching to A: a var-term constructor (4P(i,0)+3), Eq-atoms T(m)==T(n), F = "σ0==0". The expected count is higher than 345. Gate before freeze: a completeness checklist in DESIGN.md, explicitly signed off by pagb-coq. Lesson: a row-merging trick can silently drop completeness; check each saving against the needed Hilbert rules.
- ZFC-route comparison (m254gb-machine, 2026-10-24): 396 states (+115 over 281). NG' in ∈-language uses finite von Neumann ordinals, with sums as 2-block partitions and products as orthogonal grids; 410 tokens. The extra proof burden is quotient rigidity, plus L-absoluteness. PARKED: PA (~380 expected) is both smaller and cleaner. Write-up in zf/m254gb/machine/DESIGN.md.
- Design A measured at 391 states (ZFC route 396). Collision table (27 partitions) and ℕ fuzz (707k evaluations, mutants caught) pass. Positive control halts at step 123.
- !!! pagb-coq closed pprov_NG_iff_PA_GC (PA_Comp.v): the reference calculus with NG derives F ↔ PAeq ⊢TC GC_form, no axioms. Remaining: machine code-level rows ↔ pprov, L1, prog, tm.
- Agent messaging is unreliable: pagb-coq keeps addressing m254gb-machine. The channel is zf/pagb/INTERFACE.md (the shared file) plus lead relays.
- ZFC route corrected to 403–405 (a generator bug had read the family var "F" as falsity); parked.
- Lead review of checklist #8: pinned ternary vacuity (third var = c+1) looks circular. Renaming needs ∃-elim, which needs vacuity at y = x+1 and regresses upward. Asked for an explicit derivation or a fix (an extra register / occurs check). Freeze gate = pagb-coq sign-off on #8. Lesson: vacuity is primitive in Tarski–Megill; with only 3 label registers, atoms with more than 2 variables break unrestricted vacuity.
- pagb-coq CONFIRMED #8 circular and retracted its "~300 lines" claim. Fixes: (a) general B6a with an occurs check on term codes (preferred: the existing proof applies); (b) unpinned flat vacuity via an extra third-var register (+1.0–1.5k Coq lines). Rule: (a) if ≤ (b)+10 states. NG: the literal ¬GC_form is cheap in Coq; the arithmetic re-encoding costs 500–800 lines, so keep it only if it saves >15 states. pagb-coq's check.py clean rebuild is running.
- Vacuity fix measured (literal NGw): (b) unpinned flat vacuity via a new param4 (u doubles as the third var) = 432; (a) occurs check = 453 (the term walk costs ~80); pinned = 404 but incomplete. Chose (b) by the rule; pagb-coq has the final say plus the flattening translation (+1–1.5k lines). The IND gate is unnecessary (if c=a then a∉φ). The 432 machine passes all checks; order search running. PA now ~30 states above the ZFC route (403–405); PA is still preferred for auditability.
- USER DECISION 2026-10-24: proceed with the PA route; ZFC is parked for good. Reason: easier third-party audit (textbook GC_form, adequacy proved in Coq, library PAeq, smaller trusted base). Requirement: one short headline file (< 100 lines, e.g. e2e/Headline.v) with the table, halts, the main iff, GC_adequate and Print Assumptions, plus coqchk and a clean-rebuild check.py.
- FLIP to (a), general B6a with an occurs check (~453 + literal NGw). (b) is invalid with literal nested NGw: flattening the hypothesis needs nested B6a. A valid (b) needs a pre-flattened NG (~464). (a) adds an RM loop (term walk) and so needs an L2 loop-correctness lemma; no flattening translation is needed.
- ZFC-route final (m254gb-machine, parked, not frozen): 399 states (+118), all validation passes, sha256(m254gb_wade.tm) = dbff2885…6a11; files in zf/m254gb/machine. Families B–D (430–435) are UNSOUND: they hold at n=0, so NG' would be ZF-provable. Kept as a fallback only.
- Routing rule (2026-10-25): pagb-coq ↔ pagb-machine talk only via zf/pagb/INTERFACE.md plus pings to main. pagb-coq's named sends kept landing at m254gb-machine, and that also resumed it after it was stopped.
- !!! 2026-10-25: pagb-coq closed thm_F_iff : thm F ↔ PAeq ⊢TC GC_form (machine code-level calculus, design A + vac (a), PA_CompCode.v). CHECK PASS 19 files, no axioms. Pitfall: never evaluate concrete row codes (huge unary nats); use cd (enc a). Machine (a) = 449 searched (455 with Q pinned). Remaining: freeze → L1 → prog (+ term-walk loop lemma) → tm → e2e Headline.v.
- 2026-10-25: pagb-coq SIGNED OFF design A(a) (rows + §6) and chose "GO 449" (free Q labels, which must stay reachable at v0,v1). The 455 candidate was superseded. DISCARD = MP 1; AX(1;0,7,0) (b=Var(1) closes the occurs gate). Awaiting the 449 rebuild + hashes → lead verifies → FREEZE. L1 needs the frozen spec_pa.py.
- !!! FROZEN 2026-10-25: design A(a), 449 states (897 rows, LF). sha256: pa_wade.tm ed795af7…16a6, source_pa.py 152d4a5f…2587, spec_pa.py 3cfdafbf…dde4, design_choice_A.json da10ced3…abf9. Files set read-only; the record is in zf/pagb/INTERFACE.md "## FROZEN". Next: pagb-coq does L1 → prog (term-walk loop lemma) → tm → e2e Headline.v. pagb-machine is on support only.
- 2026-10-25: TM layer DONE (zf/pagb/tm, a subagent of pagb-coq). tmpa_rm : halts tm c0 ↔ rm_halts dagpa ([], regs0); tm_table (450 incl. halt / 897 rows); a constants-only port of m254tg's tm layer. The lead re-ran check_tm.py: CHECK PASS, frozen sha verified, no Admitted/Axiom. Remaining: L1, prog (term-walk loop), e2e Headline.v.
- !!! DONE 2026-10-25: pagb_halts_iff_PA_GC : halts tm c0 ↔ PAeq ⊢TC GC_form, plus GC_adequate, in e2e/Headline.v (52 lines), both Print Assumptions closed. The lead re-ran zf/pagb/check.py from scratch with agents idle: CHECK PASS (25 min). coqchk passes its kernel re-check but lists 3 environment axioms from busycoq LibTactics (inj_pair2, proof_irrelevance, eq_rect_eq), which the headline doesn't use; this is documented in README and check.py allows exactly those. NOT committed or published; publishing is the user's call. Layers: coq (enum_halts_iff_PA_GC), prog (progpa, ProgOccPA term-walk loop), tm (tmpa_rm).
- Publishing (user OK 2026-10-25): agent pagb-package builds PA/goldbach in the busy-beaver clone, branch pa-goldbach from origin/main, with CI job pa-goldbach (modelled on zf-tg296). The lead commits, pushes, opens the PR and merges after CI is green. Note: PA/m238 on main is now Coq-verified by mira-emmy (halts iff PAeq inconsistent, with real proof transport). A future 238-based Goldbach machine might be much smaller.
- PR #37 opened 2026-10-25 (branch pa-goldbach, commit 1f60d73): PA/goldbach plus CI job pa-goldbach. The local packaged check passed (24 min). Merge (merge commit) once CI is green, per [[merge-prs-without-asking]].
- !!! PUBLISHED 2026-10-25: PR #37 merged as e7997be. CI job pa-goldbach passed (15.5 min, CHECK PASS, coqchk kernel OK). Not announced; announcing is the user's call.
