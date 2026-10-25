---
name: bb43-champion-coq
description: "BB(4,3) champion 1RB1RD1LC_2LB1RB1LC_1RZ1LA1LD_0RB2RA2RD Coq-proved 2026-10-17 (halts + exact sigma = 4 e4 + 18 > 2^^^2^^^2^^^(2^96-1)); 3-symbol busycoq pitfalls"
metadata:
  node_type: memory
  type: project
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-17T21:22:12.919Z
---

Proved on 2026-10-17 in bb8_list/investigations/bb43_1RB1RD1LC/coq. The build is `build.ps1`, about 90 s. Logical root TM43. A 4x3 Ctx is in BB43.v.
- Proved there: halts, the exact final config, sigma = 4*E4 e1 v + 18 (bb43_main), and the bracket P(P(P(2^96-1))) < e4 <= P(P(P(2^96+6))), which implies the wiki's 7.92e28/7.93e28 claim. The probe found all 13 theorems Closed. The publish package is in publish/BB43 (verify/ with compile_clean.sh, 80 s, plus analysis_notes.txt); the lead opens the PR.
- Literature: Kropitz found the machine (May 2024). Polygon analyzed it by hand on the wiki (Oct 2025). No earlier Coq proof was known.
- The run used D(a,b,c) configs, f1 b = 3*2^(b+4)-5, G c = f1^(2c+11)(1) and three G-cascades. See the notes.txt file there.

**Why:** this is the first BB(k>2 symbols) proof in our tree. It also shows the busycoq 3-symbol pitfalls.
**How to apply:** for other multi-symbol machines, reuse the run/runn automation and the align_head tactic in BB43_rules.v. The pitfalls:
- `List.hd` shadows `Streams.hd`.
- Lemma variables get typed `sym` but tapes are typed `Sym`, so a closed `rewrite` fails. Use assert + apply instead.
- Literals inside Nat.iter or `=` parse as symbols, so write `1%nat`.
- Use `remember` on RHS exponents before stepping.
- lia needs ZifyNat for div/mod.
- Never let conversion compare different shapes of iter/f1 on closed values. Use iter_S rewrites.
- Unbounded `run` loops when the target is not recognized, so use `runn N`.
- lia or assumption with a closed huge value in context (P 4, B 1 6) hangs. Clear or generalize first, and use exact.
Related: [[coq-selfcontained-merge-lessons]], [[m11-argon-bb11]].

**Publishing (user OK 2026-10-17):** the lead packages this as BB43/ in the busy-beaver repo (PR, CI job since the build takes about 90 s) and merges once CI is green. Credit Kropitz (discovery) and Polygon (hand analysis).
- PR #22 opened 2026-10-17 (branch bb43, commit 51bbd55): BB43/ with a write-up, verify/, tools/bb43_chk.py and CI job bb43 (full build). Credit: Kropitz found it, Polygon analysed it; the wiki credits Racheline only with 4 other machines from the same batch. Merge once CI is green.
- !!! PUBLISHED 2026-10-17: PR #22 merged as 3a5a3fc (all 30 checks green).
- 2026-10-17: agent bb43 went on to prove the UPPER bound in BB43_score.v (e4_bounds: P(P(P(2^96-1))) < e4 <= P(P(P(2^96+6))); wiki_bracket, so the wiki claim is machine-checked; bb43_main). The lead swapped it in for BB43_bound.v, rebuilt clean (75 s, 13/13 Closed) and opened PR #23 (branch bb43-upper). Merge once CI is green.
- !!! PUBLISHED 2026-10-17: PR #23 (upper bound + wiki_bracket) merged as 7fa4afa, all 30 checks green.
