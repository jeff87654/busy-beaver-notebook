---
name: bb7-c231-coq
description: "BB(7) record candidates champ_231/232 (Argon) Coq-proved 2026-10-22, sigma = 2*W20(5)+7 > 3↑^20 3; proof layout + pitfalls"
metadata:
  node_type: memory
  type: project
  originSessionId: 49baedf6-5714-43b6-b48c-281ff82be027
  modified: 2026-10-23T03:03:31.622Z
---

champ_231 = 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB and champ_232 (G0=1LC) HALT, Coq-proved 2026-10-22
(investigations/bb7_c231_coq, pkg/ = clean package, probes "Closed"). sigma = 2*W 20 5 + 7 for both (halt reads a 1 at C1),
U0 x = 3x+9, U(j+1) x = U_j^(x+2-j)(W_j 3), W(j+1) B = U_j(W_j B). Proved: sigma > 3↑^20 3, > BB(7) champion 3*(2↑^13 3)+22.
Lead packages it (no PR by the formalizer). Independent rule check: bb7_c231check.

Method that worked fast (~1.5 h total): K-config Kc ds a b with unary [1]^^n blocks; micro passes proved with a plain
`ex := repeat (try solve [finish_norm]; step)` + `follow crX` crossings; the SAME scripts proved the sibling (G0 differs).
Clearing recursion by induction on depth replaces lexicographic descent (side condition k<=b from W j B >= B+j).

Pitfalls: lemmas typed over `Sym` don't rewrite `sym` goals (make them polymorphic); numeral 0 in untyped positions is
Sym under sym_scope (use O); `rewrite !arrow_0` / `rewrite arrow_0` can match `a*b` itself (give explicit instances);
`rewrite <- arrow_S3` on goals with closed arrows made coqc evaluate arrow 18 3 3 (3.7 GB) — use exact terms + arithmetic
lemmas on variables. See [[bb8-champion-subtree-lead]], [[c7-bb9-coq]].
